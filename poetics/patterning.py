import re

from poetics import config as config


########################################################################################################################
# General
########################################################################################################################
# Returns an extremely simple match ((matches * 2) / (sum of pattern lengths)) ratio between two patterns.
def pattern_match_ratio(pattern1, pattern2):
    len1 = len(pattern1)
    len2 = len(pattern2)
    matches = 0
    range_cap = len1
    # If the patterns aren't the same length, then cap our loop range based on the shorter one.
    if not len1 == len2:
        range_cap = min(len1, len2)
    # Add 1 to matches for each character matching character
    for i in range(0, range_cap):
        if pattern1[i] == pattern2[i]:
            matches += 1
    return (matches * 2) / (len1 + len2)


# Assigns letters to features in an ordered dict.
# TODO: Need to update this so that it uses Aa or aA if we go over 26 letters.
def assign_letters_to_dict(ordered_dict, lower=False):
    keys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if lower:
        keys = 'abcdefghijklmnopqrstuvwxyz'
    for index, feature in enumerate(ordered_dict):
        if index < 26:
            ordered_dict[feature] = keys[index]
        # If we have more than 26 rhymes, starts using pairs of letters and so on
        else:
            ordered_dict[feature] = keys[index % 26] * ((index // 26) + 1)
    return ordered_dict


########################################################################################################################
# Scansion and Meter
########################################################################################################################
# Creates a set of predicted scans based on appearance of stress/lack at positions for multi/single syllable words.
def predict_scan(length, scans):
    # Tracks stress appearances at positions for multisyllabic words.
    scan_counts = []
    # Tracks stress appearances at positions for monosyllabic words.
    scan_counts_single = []
    predicted_scan = ''
    predicted_scan_single = ''

    for x in range(0, length):
        scan_counts.append([int(0), int(0)])
        scan_counts_single.append([int(0), int(0)])
    for scan in scans:
        position = 0
        for word in scan:
            # If the word has multiple possible stress patterns, ignore it.
            if len(word) > 1:
                continue
            # If the word is multi-syllabic, then add its stresses to scan_counts.
            elif len(word[0]) > 1:
                for stress in word[0]:
                    scan_counts[position][int(stress)] += 2
                    position += 1
            # If the word is monosyllabic, modify scan_counts based on its stress mark.
            else:
                if word[0] == 'S':
                    scan_counts_single[position][1] += 2
                elif word[0] == 'W':
                    scan_counts_single[position][1] += 1
                elif word[0] == 'U':
                    scan_counts_single[position][0] += 2
                position += 1
    # Set each position in our predicted scan based on whether stress or lack appeared there most often.
    for index, position in enumerate(scan_counts):
        if max(position) > 0:
            max_value = max(position)
            predicted_scan += str(position.index(max_value))
        # If we have no data for a position, we mark it with X.
        else:
            predicted_scan += 'X'
    # Do the same for a predicted scan based only on single syllable words.
    for index, position in enumerate(scan_counts_single):
        if max(position) > 0:
            max_value = max(position)
            predicted_scan_single += str(position.index(max_value))
        # If we have no data for a column, we mark it with X.
        else:
            predicted_scan_single += 'X'

    return predicted_scan, predicted_scan_single


# Checks how well predicted stress patterns for the lines of a poem match standard meters.
# Future: Address podic meter.
# Future: Could deal with acephalous/catalectic three or four syllable feet.
def check_meters(length, predicted, predicted_single):
    foot_patterns = []
    predicted_merged = ''
    x_count = 0
    clean_predicted = ''
    clean_predicted_single = ''
    # Create a merger of predicted and predicted_single that favors predicted.
    for index, pos in enumerate(predicted):
        if not pos == 'X':
            predicted_merged += pos
        elif not predicted_single[index] == 'X':
            predicted_merged += predicted_single[index]
        else:
            predicted_merged += 'X'
            x_count += 1
    # If our merged form is more than half 'X', then we don't have enough data to guess. Return ''.
    if x_count > length // 2:
        return predicted_merged, ''
    for meter in config.classic_meters:
        if length == len(meter):
            foot_patterns.append(meter)
    # If the length of our scan is divisble by 2, add patterns for repeated 2 syllable feet
    if length % 2 == 0:
        for foot in config.metrical_feet_2:
            foot_patterns.append(foot * (len(predicted) // 2))
    # If the length of our scan is divisible by 3, add patterns for repeated 3 syllable feet
    if length % 3 == 0:
        for foot in config.metrical_feet_3:
            foot_patterns.append(foot * (len(predicted) // 3))
    # If the length of our scan is divisible by 4, add patterns for repeated 4 syllable feet
    if length % 4 == 0:
        for foot in config.metrical_feet_4:
            foot_patterns.append(foot * (len(predicted) // 4))
    # If we found any possible patterns yet, the length must be odd and indivisble by 3. Add some modified meters.
    if not foot_patterns:
        for foot in config.metrical_feet_2:
            # Add repeated 2 beat metrical feet with an additional syllable for comparison.
            foot_patterns.append((foot * (length // 2)) + foot[0])
    # Create a copy of predicted where positions without data ('X') are removed. Does the same for predicted_single.
    for pos in predicted:
        if pos == '1' or pos == '0':
            clean_predicted += pos
    for pos in predicted_single:
        if pos == '1' or pos == '0':
            clean_predicted_single += pos
    # Compares foot_patterns with the positions without data removed to predicted and predicted_single.
    predicted_ratios = []
    predicted_single_ratios = []
    for pattern in foot_patterns:
        clean_pattern = ''
        clean_pattern_single = ''
        for index, pos in enumerate(pattern):
            if not predicted[index] == 'X':
                clean_pattern += pos
            if not predicted_single[index] == 'X':
                clean_pattern_single += pos
        if clean_predicted:
            predicted_ratios.append(pattern_match_ratio(clean_predicted, clean_pattern))
        else:
            predicted_ratios.append(0)
        if clean_predicted_single:
            predicted_single_ratios.append(pattern_match_ratio(clean_predicted_single, clean_pattern_single))
        else:
            predicted_single_ratios.append(0)
    # Creates a weighted combination of predicted_ratios and predicted_single_ratios.
    weighted_ratios = []
    for i in range(0, len(predicted_ratios)):
        weighted_ratios.append((predicted_ratios[i] * 0.7) + (predicted_single_ratios[i] * 0.3))
    # Creates a list of the patterns with the best ratios, as long as those ratios are better than 0.8.
    plausible_meter_indexes = [index for index, rat in enumerate(weighted_ratios)
                               if rat == max(weighted_ratios) and rat > 0.8]
    # If we have one unique pattern left, then use it.
    plausible_meters = list(set([foot_patterns[index] for index in plausible_meter_indexes]))
    if len(plausible_meters) == 1:
        return predicted_merged, plausible_meters[0]
    # Otherwise, we compare with predicted_merged to see if either is better.
    elif len(plausible_meters) > 1:
        distances = []
        for index in plausible_meter_indexes:
            dist = pattern_match_ratio(predicted_merged, foot_patterns[index])
            distances.append((index, dist))
        # Note: if two patterns are equidistant from our prediction, the first is returned.
        return predicted_merged, foot_patterns[min(distances, key=lambda t: t[1])[0]]
    # If we have no plausible meters, return ''.
    else:
        return predicted_merged, ''


########################################################################################################################
# Rhyme
########################################################################################################################
# Chooses between candidate rhymes based on how often they appeareared in resolved lines, and then in unresolved lines
# if they never appeared in resolved lines.
def resolve_rhyme(candidates, rhyme_counts, rhyme_counts_mult):
    appearance_count = []
    appearance_count_mult = []
    # Create counts of the appearances of the candidate rhymes in resolved lines, and unresolved lines
    for candidate in candidates:
        appearance_count.append(rhyme_counts[candidate])
        appearance_count_mult.append(rhyme_counts_mult[candidate])
    # If we have a rhyme match to resolved lines, pick the one that matches the most lines.
    if max(appearance_count) >= 1:
        return candidates[appearance_count.index(max(appearance_count))]
    # If not, pick a rhyme based on how many unresolved lines it matches with (if any).
    else:
        return candidates[appearance_count_mult.index(max(appearance_count_mult))]


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
