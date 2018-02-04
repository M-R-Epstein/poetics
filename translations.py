import logging
import nltk
import re
import enchant

cmudict = nltk.corpus.cmudict.dict()


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
    try:
        return cmudict[word]
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
                return cmudict[potentials[0]]
            # If we get multiple suggestions, use Levenshtein distance to select the closest.
            elif len(potentials) > 1:
                distances = {}
                for suggestion in potentials:
                    distances[suggestion] = distance(suggestion, word)
                best_match = min(distances, key=distances.get)
                logging.warning('Reading \"%s\" as \"%s\"', word, best_match)
                return cmudict[best_match]
            # If PyEnchant returns an empty list of suggestions
            else:
                logging.error('Found no valid suggestions for %s', word)
                return False
        except KeyError:
            logging.error('KeyError attempting to resolve %s', word)
            return False


# Note: Only checks for perfect rhymes currently. Also includes secondary stress in comparison.
# Attempts to extract the rhyme(s) from a list of lists of phonemes
def get_rhymes(pronunciations):
    rhymes = []
    # Iterates through the pronunciations provided to extract the rhymes
    for index, pronunciation in enumerate(pronunciations):
        joined = ' '.join(pronunciations[index])
        first_stress = re.search("[a-zA-Z]{1,2}1[\w|\s]*", joined)
        # Deals with pronunciations ostensibly without stress (ie: some pronunciations of 'the') to provide their rhyme
        if not first_stress:
            first_stress = re.search("[a-zA-Z]{1,2}0[\w|\s]*", joined)
        # If we found a rhyme, add it to our list of rhymes
        if first_stress:
            rhymes.append(first_stress.group(0))
    # If we have found more than one rhyme we check to make sure that they are actually unique
    rhymes = list(set(rhymes))
    return rhymes


# Converts parts of speech tags from tagger to those used by wordnet. Returns None if not relevant
def convert_pos(pos):
    relevant_letters = ['a', 'n', 'r', 'v']
    pos = pos.replace("J", "A").lower()
    if pos[0] in relevant_letters:
        return pos[0]
    else:
        return None
