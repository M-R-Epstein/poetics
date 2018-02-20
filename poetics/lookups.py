import logging
import re

from Levenshtein import distance

from poetics import config as config


# Returns pronunciations for words from json copy of cmudict.
def cmu_dict(word):
    word = word.lower()
    # Return pronunciation if it's in there
    if word in config.cmu_dict:
        return config.cmu_dict[word]
    else:
        raise KeyError


# Returns syllabified pronunciation for words from syllabified cmudict.
def syllable_dict(word):
    word = word.lower()
    # Return syllabified pronunciation if it's in there
    if word in config.syllabified_dict:
        return config.syllabified_dict[word]
    else:
        logging.warning('Could not retrieve syllabified form of "%s"', word)
        return []


# Note: Currently reads "o'er" as "over" which is correct but messes with scansion. Some kind of elision check?
# Gets a word's pronunciation from cmudict and syllabified pronunciation from a syllabified version.
def get_phonetic(word):
    phonetic = []
    syllabified = []
    try:
        phonetic = cmu_dict(word)
        syllabified = syllable_dict(word)
    except KeyError:
        # If we don't get a working word from cmudict, have Enchant (spellchecker) try to find a recognized word.
        # Using a dictionary which is a list of words in cmudict so it only suggests pronouncable words.
        try:
            potentials = config.enchant_dictionary.suggest(word)
            # Handles a strange bug with PyEnchant appending carriage returns to suggestions.
            for index, potential in enumerate(potentials):
                potentials[index] = potential.strip()
            # If Enchant only returns one suggestion, we use that
            if len(potentials) == 1:
                logging.warning('Reading \"%s\" as \"%s\"', word, potentials[0])
                phonetic = cmu_dict(potentials[0])
                syllabified = syllable_dict(potentials[0])
            # If we get multiple suggestions, use Levenshtein distance to select the closest.
            elif len(potentials) > 1:
                distances = {}
                for suggestion in potentials:
                    distances[suggestion] = distance(suggestion, word)
                best_match = min(distances, key=distances.get)
                logging.warning('Reading \"%s\" as \"%s\".', word, best_match)
                phonetic = cmu_dict(best_match)
                syllabified = syllable_dict(best_match)
            # If PyEnchant returns an empty list of suggestions then log that.
            else:
                logging.error('Found no valid suggestions for \"%s\".', word)
        except KeyError:
            logging.error('KeyError attempting to resolve \"%s\".', word)

    return phonetic, syllabified


# Attempts to extract rhymelike features from a list of pronunciations and a list of syllabified pronunciations.
def get_rhymes(pronunciations, syl_pronunciations):
    p_rhymes = []
    word_init_consonants = []
    stressed_vowels = []
    stress_initial_consonants = []
    stress_final_consonants = []
    stress_bracket_consonants = []

    # Obtains word-initial consonant sounds,
    # Note: Currently words without stress are ignored for stress-relative features.
    for pronunciation in syl_pronunciations:
        stressed_syllable = ''

        match = re.search('^[\w]{1,2}(?=[\w\s]+[a-zA-Z]{2}[0-2])', pronunciation)
        # Old search for all init consonants: match = re.search('^[\w\s]+(?=[a-zA-Z]{2}[0-2])', pronunciation)
        if match:
            word_init_consonants.append(match.group(0).strip())

        match = re.search('[\w\s]*1[\w\s]*', pronunciation)
        if match:
            stressed_syllable = match.group(0).strip()

        match = re.search('[a-zA-Z]{2}(?=1)', stressed_syllable)
        if match:
            stressed_vowels.append(match.group(0).strip())

        match = re.search("[\w]{1,2}(?=[\w\s]+[a-zA-Z]{2}1)", stressed_syllable)
        # Old search for all init consonants: match = re.search("[\w\s]+(?=[a-zA-Z]{2}1)", stressed_syllable)
        if match:
            stress_initial_consonants.append(match.group(0).strip())

        match = re.search("(?<=[a-zA-Z]{2}1)[\w\s]+", stressed_syllable)
        if match:
            # Split is necessary to get only the last sound because you can't use repetition in Lookbehinds.
            # Without split, we get all consonants after the vowel in the stressed syllable.
            split = match.group(0).split(' ')
            stress_final_consonants.append(split[-1].strip())

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

    # As long as we have a nonzero number of initials, and the same number of finals, create consonant brackets.
    if stress_initial_consonants and len(stress_initial_consonants) == len(stress_final_consonants):
        for index, consonant in enumerate(stress_initial_consonants):
            stress_bracket_consonants.append(consonant + ' ' + stress_final_consonants[index])

    # Set and back to remove duplicates
    p_rhymes = list(set(p_rhymes))
    word_init_consonants = list(set(word_init_consonants))
    stressed_vowels = list(set(stressed_vowels))
    stress_initial_consonants = list(set(stress_initial_consonants))
    stress_final_consonants = list(set(stress_final_consonants))
    stress_bracket_consonants = list(set(stress_bracket_consonants))

    return (p_rhymes, word_init_consonants, stressed_vowels, stress_initial_consonants, stress_final_consonants,
            stress_bracket_consonants)


# Tries to return the name of a rhyme pattern.
def name_rhyme(rhyme):
    if rhyme in config.rhyme_patterns:
        return config.rhyme_patterns[rhyme]
    else:
        return ''


# Tries to name a meter based on metrical pattern.
def name_meter(pattern):
    classical_name = None
    foot = None
    foot_name = None
    foot_names = []
    repetition = None
    # Don't bother for blank patterns
    if len(pattern) == 0:
        return None, None
    if pattern in config.classic_meters:
        classical_name = config.classic_meters[pattern]
    # Try to match a 2 syllable foot
    if len(pattern) % 2 == 0:
        split = [pattern[i:i + 2] for i in range(0, len(pattern), 2)]
        if len(set(split)) == 1:
            foot = split[0]
            foot_name = config.metrical_feet_2[foot]
            repetition = len(split)
    # Try to match a 3 syllable foot if no 2 syllable feet matched
    if not foot:
        if len(pattern) % 3 == 0:
            split = [pattern[i:i + 3] for i in range(0, len(pattern), 3)]
            if len(set(split)) == 1:
                foot = split[0]
                foot_name = config.metrical_feet_3[foot]
                repetition = len(split)
    # Try to match a 4 syllable foot if no 2 or 3 syllable feet matched
    if not foot:
        if len(pattern) % 4 == 0:
            split = [pattern[i:i + 4] for i in range(0, len(pattern), 4)]
            if len(set(split)) == 1:
                foot = split[0]
                foot_name = config.metrical_feet_4[foot]
                repetition = len(split)
    # Finally, check for metres that are odd to see if they are slightly modified 2 syllable foot meters
    # Note: may want to modify this to account for pyrrhic or spondaic meters.
    if not foot:
        if len(pattern) % 2 == 1:
            trimmed_pattern1 = [pattern[i:i + 2] for i in range(1, len(pattern), 2)]
            trimmed_pattern2 = [pattern[i:i + 2] for i in range(0, len(pattern) - 1, 2)]
            if len(set(trimmed_pattern1)) == 1:
                foot = trimmed_pattern1[0]
                foot_names.append((config.metrical_feet_2[foot], 'headless'))
                repetition = len(trimmed_pattern1) + 1
            if len(set(trimmed_pattern2)) == 1:
                foot = trimmed_pattern2[0]
                foot_names.append((config.metrical_feet_2[foot], 'catalectic'))
                repetition = len(trimmed_pattern2) + 1
            if len(foot_names) == 1:
                foot_name = foot_names[0]
    # Get a name
    if classical_name:
        return classical_name, None
    elif foot_name:
        foot_adj = config.metrical_foot_adj[foot_name]
        if repetition < 30:
            repetition = config.meter_names[repetition - 1]
            return foot_adj, repetition
        else:
            return foot_adj, 'meter'
    elif foot_names:
        foot_adjs = [(config.metrical_foot_adj[name], prefix) for name, prefix in foot_names]
        if repetition < 30:
            repetition = config.meter_names[repetition - 1]
            joined = ' or '.join([prefix + ' ' + foot_adj for foot_adj, prefix in foot_adjs])
            return joined, repetition
        else:
            joined = ' or '.join([prefix + ' ' + foot_adj for foot_adj, prefix in foot_adjs])
            return joined, 'meter'
    else:
        return 'unrecognized', 'meter'


def name_stanza(rhyme_scheme, line_lengths, meters, line_count):
    matches = []
    # Make a list of forms that are an appropriate number of lines.
    forms = [forms for forms in config.stanza_forms if forms[4] == line_count]
    for form in forms:
        # If the form has no rhyme requirement or the stanza's rhyme scheme matches.
        if not form[1] or rhyme_scheme in form[1]:
            # If the form has no line length requirements or we have a match.
            if not form[2] or line_lengths in form[2]:
                # If the form has no metrical requirement or we have a match.
                if not form[3] or meters in form[3]:
                    matches.append(form[0])
    if not matches:
        if 1 < line_count < 9:
            matches.append('Unrecognized ' + config.stanza_length_names[line_count - 1])
        elif line_count <= 100:
            matches.append('Unrecognized ' + config.stanza_length_names[line_count - 1] + ' line stanza')
        else:
            matches.append('Unrecognized stanza')
    return matches
