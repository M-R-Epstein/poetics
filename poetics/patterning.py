from collections import Counter

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
def assign_letters_to_dict(ordered_dict, lower=False):
    keys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    keys2 = 'abcdefghijklmnopqrstuvwxyz'
    if lower:
        keys = 'abcdefghijklmnopqrstuvwxyz'
        keys2 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for index, feature in enumerate(ordered_dict):
        if index < 26:
            ordered_dict[feature] = keys[index]
        # If we have more than 26 rhymes, we starting using Aa Ab ... Ba ... Aaa.
        else:
            ordered_dict[feature] = keys[(index // 26) - 1] + keys2[index % 26]
    return ordered_dict


# Checks if a list of tokens contains any words.
def check_for_words(tokens):
    for token in tokens:
        if not token.is_wspace and not token.is_punct:
            return True
    return False


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
# Future: Podic meters.
# Future: Acephalous/catalectic three or four syllable feet.
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
# Chooses between candidate rhymes based on maximizing rhyme.
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
    elif max(appearance_count_mult) >= 1:
        return candidates[appearance_count_mult.index(max(appearance_count_mult))]
    # If none, we have no basis for resolution.
    else:
        return None


# Attempts to maximize matches across tokens for their values for the feature.
def maximize_token_matches(tokens, feature):
    # List of tokens that don't have that feature resolved.
    unresolved_tokens = [token for token in tokens if not getattr(token, 's_' + feature)]

    # If all of the tokens already have the feature resolved (that is, if all pronunciations assigned to a token
    # have the same value for the feature), then there's nothing to maximize.
    if not unresolved_tokens:
        return

    # Counter for occurances of the feature for tokens that have the feature resolved.
    count = Counter([getattr(token.pronunciations[0], feature) for token in tokens
                     if getattr(token, 's_' + feature) and token.pronunciations])
    # Counter for occurances of the feature for tokens that don't have the feature resolved.
    multi_count = Counter([getattr(pronunciation, feature) for token in unresolved_tokens
                           for pronunciation in token.pronunciations])

    # Creates a list of tuples which store the token and the most likely value (for feature) for each unresolved token.
    best_features = []
    for token in unresolved_tokens:
        best_features.append((token, resolve_rhyme([getattr(pronunciation, feature) for pronunciation
                                                    in token.pronunciations], count, multi_count)))

    # Update our count of resolved token features to include the most likely values we've calculated.
    count.update([value for token, value in best_features])

    # Threshold for the number of unique values for the feature amongst tokens above which that feature is not
    # maximized. This is set as half the number of tokens, rounded up. I.e., if we have 16 (or 15) tokens, then if there
    # are more than 9 unique values then don't consider that feature patterened and don't maximize for it.
    threshold = (len(tokens) // 2) + (len(tokens) % 2 > 0)

    # If we have more unique values for feature than the threshold, then don't do any maximizing.
    if len(count) > threshold:
        return
    # If some number of tokens had a value for the feature of None, then don't do any maximizing.
    elif None in count:
        return
    # Otherwise, remove pronunciations from the unresolved tokens that don't have the selected value for feature.
    else:
        for token, value in best_features:
            # It is possible for resolve_rhyme to return None, so make sure we have a value before we do anything.
            if value:
                token.cull_pronunciations(feature, value)


########################################################################################################################
# Sight
########################################################################################################################

def get_acrostics(input_string):
    def find_next_word(letters):
        c = 1
        words = []
        # All single letters are in the dictionary, but they aren't words, so if the first letter isn't 'a' or 'i' then
        # skip matching the first letter.
        if not letters[0] == 'a' and not letters[0] == 'i':
            if len(letters) > 1:
                c += 1
            # If we don't have a next letter to skip to, then stop.
            else:
                return words
        # Loop through the input string in segments of increasing length checking if any are words. Add matched words to
        # words, which is the output.
        while c <= len(letters):
            if config.enchant_english_dictionary.check(letters[:c]):
                words.append(letters[:c])
            c += 1
        return words

    final_readings = []
    # Create a list of the words that could start an accrostic.
    readings = [[word] for word in find_next_word(input_string)]
    # Keep looping until we run out of readings.
    while readings:
        for index, reading in enumerate(readings):
            # If the current reading is the length of the entire input string, then add it to output and remove it from
            # readings.
            if len(''.join(reading)) == len(input_string):
                final_readings.append(reading)
                del readings[index]
                continue
            # Get the set of next possible words for the string remaining when it has been trimmed to reflect the
            # current words in reading.
            next_words = find_next_word(input_string[len(''.join(reading)):])
            # If we got no words, then delete the current reading as it cannot be completed.
            if len(next_words) == 0:
                del readings[index]
            # If we got a single word, then add it to the end of the current reading.
            elif len(next_words) == 1:
                readings[index].append(next_words[0])
            # If we got multiple words, split the reading off into multiple readings that continue from each.
            elif len(next_words) >= 1:
                current = reading[:]
                readings[index].append(next_words[0])
                for word in next_words[1:]:
                    readings.append(current + [word])
    return final_readings
