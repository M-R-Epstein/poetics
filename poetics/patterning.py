from poetics import config as config


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
        predicted_ratios.append(pattern_match_ratio(clean_predicted, clean_pattern))
        predicted_single_ratios.append(pattern_match_ratio(clean_predicted_single, clean_pattern_single))
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
    if max(appearance_count) > 1:
        return candidates[appearance_count.index(max(appearance_count))]
    # If not, pick a rhyme based on how many unresolved lines it matches with (if any).
    else:
        return candidates[appearance_count_mult.index(max(appearance_count_mult))]


# Assigns letters to features in an ordered dict.
def assign_letters_to_dict(ordered_dict):
    keys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    for index, feature in enumerate(ordered_dict):
        if index < 52:
            ordered_dict[feature] = keys[index]
        # If we somehow have more than 52 rhymes, starts using pairs of letters and so on
        else:
            ordered_dict[feature] = keys[index % 52] * ((index // 52) + 1)
    return ordered_dict
