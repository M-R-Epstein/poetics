from poetics import config as config


def predict_scan(scans):
    scan_counts = []
    scan_counts_single = []
    predicted_scan = ''
    predicted_scan_single = ''
    if len(scans[0]) < 1:
        return '', ''
    else:
        # Add the appropriate number of elements to track stress appearance by syllable
        # scan_counts_single separately tracks stress appearance for single syllable words
        for x in range(0, len(scans[0])):
            scan_counts.append([int(0), int(0)])
            scan_counts_single.append([int(0), int(0)])
        # Increment counts for stress appearance by syllable position
        for line in scans:
            for index, stress in enumerate(line):
                if stress == '1' or stress == '0':
                    scan_counts[index][int(stress)] += 1
                if stress == '3' or stress == '4':
                    scan_counts_single[index][int(stress) - 3] += 1
        # Note: Columns where we have no data to indicate stress/lack are currently defaulting to unstressed
        # Create a predicted scan based on most common stress/lack at position in lines for multi-syllable words
        for index, position in enumerate(scan_counts):
            if max(position) > 0:
                max_value = max(position)
                predicted_scan += str(position.index(max_value))
            # If we have no data for a column, we mark it with 9
            else:
                predicted_scan += '9'
        # Do the same for single syllable words
        for index, position in enumerate(scan_counts_single):
            if max(scan_counts_single[index]) > 0:
                max_value = max(position)
                predicted_scan_single += str(position.index(max_value))
            # If we have no data for a column, we mark it with 9
            else:
                predicted_scan_single += '9'
        merged = ''
        for index, position in enumerate(predicted_scan):
            if position == '9':
                merged += predicted_scan_single[index]
            else:
                merged += position
        return predicted_scan, merged


# Checks how well a calculated most common stress pattern for the lines of a poem matches standard metres
def check_metres(predicted, merged):
    from Levenshtein import distance, ratio
    foot_patterns = []
    plausible_meters = []

    # If the length of our scan is divisble by 2, add patterns for repeated 2 syllable feet
    if len(predicted) % 2 == 0:
        for foot in config.metrical_feet_2:
            foot_patterns.append(foot * (len(predicted) // 2))
    # If the length of our scan is divisible by 3, add patterns for repeated 3 syllable feet
    if len(predicted) % 3 == 0:
        for foot in config.metrical_feet_3:
            foot_patterns.append(foot * (len(predicted) // 3))
    # If the length of our scan is divisible by 4, add patterns for repeated 4 syllable feet
    if len(predicted) % 4 == 0:
        for foot in config.metrical_feet_4:
            foot_patterns.append(foot * (len(predicted) // 4))
    # If we haven't got any patterns yet, generate some possibilities
    # Length must be odd and indivisible by 3 or 4 for this to happen
    if not foot_patterns:
        for foot in config.metrical_feet_2:
            # Add repeated 2 beat metrical feet with an additional stressed/unstressed syllable for comparison
            foot_patterns.append((foot * (len(predicted) // 2)) + '1')
            foot_patterns.append((foot * (len(predicted) // 2)) + '0')
            foot_patterns.append('1' + (foot * (len(predicted) // 2)))
            foot_patterns.append('0' + (foot * (len(predicted) // 2)))

    # See if Levenshtein ratio suggests that any of our patterns are a good match for our multi-word prediction
    # 0.8 seems to be a reasonable ratio value to set as a floor, may need more testing
    for pattern in foot_patterns:
        if ratio(pattern, predicted) >= 0.8:
            plausible_meters.append(pattern)

    # If we didn't find a good match, then check against the pattern that considers 1 syllable words
    if not plausible_meters:
        for pattern in foot_patterns:
            if ratio(pattern, merged) >= 0.7:
                plausible_meters.append(pattern)

    if len(plausible_meters) == 1:
        return plausible_meters[0]
    # If we get multiple plausible patterns, use Levenshtein distance to find the best match
    elif len(plausible_meters) > 1:
        distances = {}
        for index, pattern in enumerate(plausible_meters):
            distances[pattern] = distance(plausible_meters[index], predicted)
        return min(distances, key=distances.get)
    else:
        return ''


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
