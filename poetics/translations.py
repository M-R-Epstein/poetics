import logging
import nltk
import re
import enchant
import json

cmudict = nltk.corpus.cmudict.dict()


def syllable_dict(word):
    import os
    directory = os.path.dirname(__file__)
    syllables_dir = os.path.join(directory, 'text/cmudict_syllables.json')

    global syllables_dict
    # Load the dictionary from Json if we haven't already
    try:
        syllables_dict
    except NameError:
        with open(syllables_dir) as file:
            syllables_dict = json.load(file)
    # Return syllabified pronunciation if it's in there
    if word in syllables_dict:
        return syllables_dict[word]
    else:
        logging.warning('Could not retrieve syllabified form of %s', word)
        return []


def tokenize(line):
    tokenized = []

    # Substitutions for various punctuation.
    subs = {'-': ' ', '‘': "'", '’': "'"}
    for chars, substitution in subs.items():
        line = line.replace(chars, substitution)

    # Loops through expressions/replacements in expressions. Currently deals with getting rid of uneeded apostrophes
    # while maintaining conjunctions
    # Final expression removes all non-apostrophe, digit, or word characters left over
    expressions = {'\'[^\w]': ' ', '[^\w]\'': ' ', "\'\Z": ' ', "\A\'": ' ', '[^\d\w\']': ' '}
    for expression, replacement in expressions.items():
        line = re.sub(expression, replacement, line)

    # Lower case it
    line = line.lower()
    # Split into individual words
    tokenized.extend([word for word in line.strip().split()])
    return tokenized


# Note: Currently reads "o'er" as "over" which is correct but messes with scansion. Some kind of elision check?
# Gets a word's pronunciation from CMUdict
def get_phonetic(word):
    phonetic = []
    syllabified = []

    try:
        phonetic = cmudict[word]
        syllabified = syllable_dict(word)
    except KeyError:
        # If we don't get a working word from cmudict, have Enchant (spellchecker) try to find a recognized word
        # Using a dictionary which is a list of words in cmudict so it only suggests pronouncable words
        try:
            import os
            from Levenshtein import distance
            dictionary = enchant.request_pwl_dict(os.path.dirname(__file__) + "/text/wordlist.txt")
            potentials = dictionary.suggest(word)
            # Handles a strange bug with PyEnchant appending carriage returns to suggestions
            for index, potential in enumerate(potentials):
                potentials[index] = potential.strip()
            # If Enchant only returns one suggestion, we use that
            if len(potentials) == 1:
                logging.warning('Reading \"%s\" as \"%s\"', word, potentials[0])
                phonetic = cmudict[potentials[0]]
                syllabified = syllable_dict(potentials[0])
            # If we get multiple suggestions, use Levenshtein distance to select the closest.
            elif len(potentials) > 1:
                distances = {}
                for suggestion in potentials:
                    distances[suggestion] = distance(suggestion, word)
                best_match = min(distances, key=distances.get)
                logging.warning('Reading \"%s\" as \"%s\"', word, best_match)
                phonetic = cmudict[best_match]
                syllabified = syllable_dict(best_match)
            # If PyEnchant returns an empty list of suggestions
            else:
                logging.error('Found no valid suggestions for %s', word)
        except KeyError:
            logging.error('KeyError attempting to resolve %s', word)

    return phonetic, syllabified


# Attempts to extract rhymelike features from a list of pronunciations and a list of syllabified pronunciations
def get_rhymes(pronunciations, syl_pronunciations):
    p_rhymes = []
    word_init_consonants = []
    stressed_vowels = []
    stress_initial_consonants = []
    stress_final_consonants = []

    # Obtains word-initial consonant sounds,
    # Note: Currently words without stress are ignored for stress-relative features.
    # TODO: word_init_consonants and stressed_vowels don't actually need to be done on the syllabified version
    for pronunciation in syl_pronunciations:
        stressed_syllable = ''

        match = re.search('^[\w\s]+(?=[a-zA-Z]{2}[0-2])', pronunciation)
        if match:
            word_init_consonants.append(match.group(0).strip())

        match = re.search('[\w\s]*1[\w\s]*', pronunciation)
        if match:
            stressed_syllable = match.group(0).strip()

        match = re.search('[a-zA-Z]{2}(?=1)', stressed_syllable)
        if match:
            stressed_vowels.append(match.group(0).strip())

        match = re.search("[\w\s]+(?=[a-zA-Z]{2}1)", stressed_syllable)
        if match:
            stress_initial_consonants.append(match.group(0).strip())

        match = re.search("(?<=[a-zA-Z]{2}1)[\w\s]+", stressed_syllable)
        if match:
            stress_final_consonants.append(match.group(0).strip())

    # Iterates through the pronunciations provided to extract perfect rhymes
    for index, pronunciation in enumerate(pronunciations):
        joined = ' '.join(pronunciations[index])
        first_stress = re.search("[a-zA-Z]{1,2}1[\w|\s]*", joined)
        # Deals with pronunciations ostensibly without stress (ie: some pronunciations of 'the') to provide their rhyme
        if not first_stress:
            first_stress = re.search("[a-zA-Z]{1,2}0[\w|\s]*", joined)
        # If we found a rhyme, add it to our list of rhymes
        if first_stress:
            p_rhymes.append(first_stress.group(0))

    # Set and back to remove duplicates
    p_rhymes = list(set(p_rhymes))
    word_init_consonants = list(set(word_init_consonants))
    stressed_vowels = list(set(stressed_vowels))
    stress_initial_consonants = list(set(stress_initial_consonants))
    stress_final_consonants = list(set(stress_final_consonants))

    return p_rhymes, word_init_consonants, stressed_vowels, stress_initial_consonants, stress_final_consonants


# Converts parts of speech tags from tagger to those used by wordnet. Returns None if not relevant
def convert_pos(pos):
    relevant_letters = ['a', 'n', 'r', 'v']
    pos = pos.replace("J", "A").lower()
    if pos[0] in relevant_letters:
        return pos[0]
    else:
        return None
