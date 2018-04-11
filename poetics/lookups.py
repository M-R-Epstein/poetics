import logging
import re

from Levenshtein import distance

from poetics import config as config


########################################################################################################################
# Pronunciation
########################################################################################################################
# Returns phonetic pronunciation for words from phoneticized cmudict.
def phonetic_dict(word):
    word = word.lower()
    if word in config.phoneticized_dict:
        return config.phoneticized_dict[word]
    else:
        return None


# Returns a list of possible word endings using list from sonic_features.json.
def get_word_endings(pronunciation):
    out_list = []
    # The maximum length of a word ending pronunciation in the file is 15, so our loop is constrained to the smallest of
    # 15 or the length of the pronunciation. We start at 1 because we don't want to count words that are one of the
    # endings in the file in their entirety.
    for i in range(1, min(len(pronunciation), 15)):
        segment = pronunciation[i:]
        if segment in config.word_endings:
            # We record the index instead of the actual pronunciation because the same segment will always have the same
            # index (the list is from a file rather than dynamic) and the indexes are more performant for comparisons.
            out_list.append(config.word_endings[segment])
    return out_list


# Checks if a word is in the list of onomatopoetic words.
def check_onomatopoetic(word):
    if word.lower() in config.onomatopoetic_words:
        return True
    else:
        return False


# Gets a word's pronunciations from phoneticized cmudict.
# Future: currently reads "o'er" as "over" which is correct but messes with scansion. Some kind of elision check?
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
            if word[-2] == "'":
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
    # If that hasn't worked, attempt to deal with elision:
    if not pronunciations:
        if "'" in word:
            elided = build_elided(word)
            if elided[0]:
                pronunciations = elided[0]
                logging.warning('Reading \"%s\" as an elided form of \"%s\".', word, elided[1])
    # If we are still without a pronunciation, have Enchant (spellchecker) try to find a recognized word.
    # Using a dictionary which is a list of words in cmudict so it only suggests pronouncable words.
    if not pronunciations:
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


# Builds a pronunciation for a plural or posessive form of a word that we have a pronunciation for the singular form
# of.
def build_plural_or_posessive(base_pronunciations):
    sibilant = ['S', 'Z', 'SH', 'ZH', 'CH', 'JH']
    voiceless = ['P', 'T', 'K', 'F', 'TH']
    for index, pronunciation in enumerate(base_pronunciations):
        out_pro = pronunciation
        b_coda = pronunciation[-1][3].split(' ')
        # If the final consonant sound of the final syllable is sibilant, add a new syllable ending with IH Z which
        # 'steals' the last consonant from the previous syllable's coda to be its onset.
        if b_coda[-1] in sibilant:
            new_syl = [0, b_coda[-1], 'IH', 'Z']
            out_pro[-1][3] = ' '.join(b_coda[:-1])
            out_pro.append(new_syl)
        # If the final consonant sound is an unvoiced consonant, add S to the coda of the last syllable.
        elif b_coda[-1] in voiceless:
            new_coda = b_coda
            new_coda.append('S')
            out_pro[-1][3] = ' '.join(new_coda)
        # Otherwise, add Z to the coda of the last syllable.
        else:
            if b_coda[0]:
                new_coda = b_coda
            else:
                new_coda = []
            new_coda.append('Z')
            out_pro[-1][3] = ' '.join(new_coda)
        base_pronunciations[index] = out_pro
    return base_pronunciations


# Attempts to get a pronunciation for a word with elision.
# Future: the many other forms of elision.
def build_elided(word):
    out_words = []
    pronunciation = None
    elided_word = None
    if word[-1] == 'd' and word[-2] == "'":
        if word[-3] == 'y':
            out_words.append(word[:-3] + 'ied')
        elif word[-3] == 'c':
            out_words.append(word[:-2] + 'ked')
        elif word[-3] == 'e':
            out_words.append(word[:-2] + 'd')
        else:
            out_words.append(word[:-2] + 'ed')
            out_words.append(word[:-2] + word[-3] + 'ed')
    if out_words:
        for w in out_words:
            pronunciation = phonetic_dict(w)
            if pronunciation:
                elided_word = w
                break
    return pronunciation, elided_word


########################################################################################################################
# Form identification
########################################################################################################################
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
# Tries to name the form of a stanza based on rhyme scheme, line lengths, meters, and line count.
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


# Attempts to name the form of a poem based on rhyme scheme, line lengths, and line count.
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


# Takes a poem's line count and builds a list of the repeating poem forms that could match a poem of that length
def get_repeating_rhyme_patterns(poem_lines):
    out_forms = []
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']
    for form in config.poem_forms_repeating:
        # Get the length of the head of the pattern if one exists.
        rhyme_head = len([character for character in form[1] if not character.isdigit()])
        syllables_head = 0
        if form[4]:
            syllables_head = len(form[4].split())
        # Get the length of the tail of the pattern if one exists.
        rhyme_tail = len([character for character in form[3] if not character.isdigit()])
        syllables_tail = 0
        if form[6]:
            syllables_tail = len(form[6].split())
        # Get the length of the core repeated portion.
        rhyme_core = len([character for character in form[2] if not character.isdigit()])
        syllables_core = 0
        if form[5]:
            syllables_core = len(form[5].split())
        # Number of lines left after we remove the length of the head/tail.
        poem_remaining_lines = poem_lines - (rhyme_head or syllables_head) - (rhyme_tail or syllables_tail)
        # If the pattern can fit, then repeat the repeating portions to achieve the appropriate length.
        if poem_remaining_lines % (rhyme_core or syllables_core) == 0:
            out_rhyme_pattern = []
            out_syllable_pattern = []
            # If there is a syllables_core, then deal with repeating the syllable counts.
            if syllables_core > 0:
                out_syllable_pattern.extend(form[4])
                for i in range(0, (poem_remaining_lines // syllables_core)):
                    out_syllable_pattern.append(form[5])
                out_syllable_pattern.extend(form[6])
            # If there is a rhyme_core, then deal with repeating it (with interlocking).
            if rhyme_core > 0:
                split_repeat = re.findall('([a-zA-Z]\d?)', form[2])
                alphabet_count = 0
                current_alphabet = alphabet[:]
                # Remove letters in the first instance of the pattern from the currently used alphabet.
                for letter in [letter.upper() for letter in set([pos[0] for pos in split_repeat])]:
                    current_alphabet.remove(letter)
                # Add the head and then the letters from the first instance to out_pattern.
                out_rhyme_pattern.extend(form[1])
                out_rhyme_pattern.extend([letter[0].upper() for letter in split_repeat])
                poem_remaining_lines -= len(split_repeat)
                last_repeat = []
                # Repeat the core pattern the appropriate number of times.
                for i in range(0, (poem_remaining_lines // len(split_repeat))):
                    next_input = split_repeat[:]
                    for index, pos in enumerate(next_input):
                        if pos[-1:].isdigit():
                            if last_repeat:
                                next_input[index] = last_repeat[int(pos[-1:]) - 1].upper()
                            else:
                                next_input[index] = split_repeat[int(pos[-1:]) - 1].upper()
                        elif pos.islower():
                            replacements = [index2 for index2, item in enumerate(split_repeat) if item == pos]
                            for replacement in replacements:
                                next_input[replacement] = current_alphabet[0]
                            current_alphabet.remove(current_alphabet[0])
                        # If we have used all of the letters, we starting using Aa Ab ... Ba ... Aaa.
                        if not current_alphabet:
                            prime_letter = alphabet[alphabet_count % 26]
                            for letter in alphabet:
                                current_alphabet.append(prime_letter + letter.lower() * ((alphabet_count // 26) + 1))
                            alphabet_count += 1
                    last_repeat = next_input[:]
                    out_rhyme_pattern.extend(next_input)
                # Handle the tail if we have one.
                if form[3]:
                    split_tail = re.findall('([a-zA-Z]\d?)', form[3])
                    for index, pos in enumerate(split_tail):
                        if pos[-1:].isdigit():
                            split_tail[index] = last_repeat[int(pos[-1:]) - 1].upper()
                        elif pos.islower():
                            replacements = [index2 for index2, item in enumerate(split_tail) if item == pos]
                            for replacement in replacements:
                                split_tail[replacement] = current_alphabet[0]
                            current_alphabet.remove(current_alphabet[0])
                        if not current_alphabet:
                            prime_letter = alphabet[alphabet_count % 26]
                            for letter in alphabet:
                                current_alphabet.append(prime_letter + letter.lower() * ((alphabet_count // 26) + 1))
                            alphabet_count += 1
                    out_rhyme_pattern.extend(split_tail)
            if out_rhyme_pattern:
                out_rhyme_pattern = [''.join(out_rhyme_pattern)]
            else:
                out_rhyme_pattern = []
            if out_syllable_pattern:
                out_syllable_pattern = ' '.join(out_syllable_pattern)
            else:
                out_syllable_pattern = []
            out_forms.append([form[0], out_rhyme_pattern, out_syllable_pattern, poem_lines])
    return out_forms
