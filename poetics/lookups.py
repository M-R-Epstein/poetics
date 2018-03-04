import logging

from Levenshtein import distance

from poetics import config as config
from poetics.patterning import get_repeating_rhyme_patterns
from poetics.conversions import build_plural_or_posessive


# Returns phonetic pronunciation for words from phoneticized cmudict.
def phonetic_dict(word):
    word = word.lower()
    if word in config.phoneticized_dict:
        return config.phoneticized_dict[word]
    else:
        return None


# Gets a word's pronunciations from phoneticized cmudict.
# Future: Currently reads "o'er" as "over" which is correct but messes with scansion. Some kind of elision check?
def get_pronunciations(token):
    special_cases = {'p.m.': 'pm',
                     'vs.': 'vs',
                     'mt.': 'mt',
                     'mont.': 'mont',
                     'co.': 'co',
                     'corp.': 'corp',
                     'inc.': 'inc',
                     'ltd.': 'ltd',
                     'dr.': 'dr',
                     'rep.': 'rep',
                     'rev.': 'rev',
                     'sen.': 'sen',
                     'st.': 'st',
                     'jr.': 'jr',
                     'bros.': 'bro\'s',
                     'Ph.': 'ph'}
    token = token.lower()
    if token in special_cases:
        word = special_cases[token]
    else:
        word = token
    pronunciations = phonetic_dict(word)
    # If we don't get a working word from cmudict, see if we have a depluralized version of the word.
    if not pronunciations:
        base_pronunciations = None
        used_word = None
        transformation_type = 'plural (or present)'
        if word[-1] == 's':
            # If the word is apparently a posessive form, see if we have a pronunciation for the word without 's.
            if word[-2] == '\'' or word[-2] == '’':
                base_pronunciations = phonetic_dict(word[:-2])
                used_word = word[:-2]
                transformation_type = 'posessive'
            # If it's not posessive, treat it as a possible plural.
            else:
                base_pronunciations = phonetic_dict(word[:-1])
                used_word = word[:-1]
                if not base_pronunciations and word[-2] == 'e':
                    base_pronunciations = phonetic_dict(word[:-2])
                    used_word = word[:-2]
        if base_pronunciations:
            pronunciations = build_plural_or_posessive(base_pronunciations)
            logging.warning('Reading \"%s\" as the %s form of \"%s\".', word, transformation_type, used_word)
    if not pronunciations:
        # If we are still without a pronunciation, have Enchant (spellchecker) try to find a recognized word.
        # Using a dictionary which is a list of words in cmudict so it only suggests pronouncable words.
        potentials = config.enchant_dictionary.suggest(word)
        # Handles a strange bug with PyEnchant appending carriage returns to suggestions.
        for index, potential in enumerate(potentials):
            potentials[index] = potential.strip()
        # If Enchant only returns one suggestion, we use that
        if len(potentials) == 1:
            logging.warning('Reading \"%s\" as \"%s\".', word, potentials[0])
            pronunciations = phonetic_dict(potentials[0])
        # If we get multiple suggestions, use Levenshtein distance to select the closest.
        elif len(potentials) > 1:
            distances = {}
            for suggestion in potentials:
                distances[suggestion] = distance(suggestion, word)
            best_match = min(distances, key=distances.get)
            logging.warning('Reading \"%s\" as \"%s\".', word, best_match)
            pronunciations = phonetic_dict(best_match)
        # If PyEnchant returns an empty list of suggestions then log that.
        else:
            logging.error('Found no valid suggestions for \"%s\".', word)
    return pronunciations


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
                foot_names.append((config.metrical_feet_2[foot], 'acephalous'))
                repetition = len(trimmed_pattern1) + 1
            if len(set(trimmed_pattern2)) == 1:
                foot = trimmed_pattern2[0]
                foot_names.append((config.metrical_feet_2[foot], 'catalectic'))
                repetition = len(trimmed_pattern2) + 1
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


# Future: Internal rhyme patterns, word repetitions, caesura, specific rhyme types, and refrains.
def name_stanza(rhyme_scheme, line_lengths, meters, line_count):
    # If all lines are the same length, set line_lengths to that one length.
    if len(set(line_lengths)) == 1:
        line_lengths = str(line_lengths[0])
    else:
        line_lengths = ' '.join(line_lengths)

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


def name_poem(rhyme_scheme, line_lengths, line_count):
    # Strip whitespace from rhyme_scheme
    if rhyme_scheme:
        rhyme_scheme = rhyme_scheme.replace(' ', '')
    # If all lines are the same length, set line_lengths to that one length.
    if len(set(line_lengths)) == 1:
        line_lengths = str(line_lengths[0])
    else:
        line_lengths = ' '.join(line_lengths)

    matches = []
    # Get all possible forms that are the right length.
    forms = [form for form in config.poem_forms if form[3] == line_count]
    forms.extend(get_repeating_rhyme_patterns(line_count))
    for form in forms:
        # If the form has no rhyme requirement or the poem's rhyme scheme matches.
        if not form[1] or rhyme_scheme in form[1]:
            # If the form has no line length requirements or we have a match.
            if not form[2] or line_lengths in form[2]:
                matches.append(form[0])
    return matches
