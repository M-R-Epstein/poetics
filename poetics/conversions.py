import re

from collections import Counter


# Tokenizes text into individual words.
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

    # Split into individual words
    tokenized.extend([word for word in line.strip().split()])
    return tokenized


# Splits up the plaintext so that each item in the list ENDS with a token.
# The returned list may be one item longer than the input list because of trailing non-token text.
def split_by_tokens(tokens, plaintext):
    by_tokens = []
    for token in tokens:
        match = re.search(token, plaintext)
        by_tokens.append(plaintext[:match.end()])
        plaintext = plaintext[match.end():]
    if plaintext:
        by_tokens.append(plaintext)
    return by_tokens


# Converts parts of speech tags from tagger to those used by wordnet. Returns None if not relevant
def convert_pos(pos):
    relevant_letters = ['a', 'n', 'r', 'v']
    pos = pos.replace("J", "A").lower()
    if pos[0] in relevant_letters:
        return pos[0]
    else:
        return None


# Gets groups from a sound set.
def get_sound_set_groups(sound_list, tokenized_text, max_feature_distance):
    # Make a dictionary of sound appearances that are {Sound: [indexes of appearances]}.
    sound_set = index_unique_strings(sound_list, 2)
    output_dict = {}
    # Turn the sets of indexes into groups with a maximum distance between each consequitive member.
    for key, indexes in sound_set.items():
        groups = [num for num in get_distance_groups(indexes, max_feature_distance, 2)]
        # Test to make sure that those index groups correspond to at least two unique words.
        for index, group in enumerate(groups):
            words = [tokenized_text[index2].lower() for index2 in group]
            if len(set(words)) < 2:
                del(groups[index])
        # If any groups remain, add them to an output dictionary.
        if groups:
            output_dict[key] = groups
    return output_dict


# Yields max-length groups of integers, of min_length or longer, where each consecutive integer in a group is no more
# than distance apart.
def get_distance_groups(num_list, distance, min_length=1):
    group = []
    for index, num in enumerate(num_list):
        # If group is currently empty or the last number in group is within distance of num, append num to group.
        if not group or num - group[-1] <= distance:
            group.append(num)
            # If we're not on the last number in the list, then we move to the next one.
            # This check necessary because otherwise the last group will never be yielded.
            if index < len(num_list) - 1:
                continue
        # If we aren't within distance and group isn't empty (and so we never hit continue) then we yield group if
        # group is at least the minimum number of items long.
        if len(group) >= min_length:
            yield group
        # Then we take the current num, and put it in group alone for the next iteration.
        group = [num]


# Takes a list of strings and returns a dict of unique items and indexes of appearances.
# Handles lists of lists of strings or lists of strings (e.g. [['a', 'b'],['c', 'd']] or ['a', 'b']).
def index_unique_strings(input_list, min_count=None):
    min_count = min_count or 1
    out = {}
    if isinstance(input_list[0], list):
        count = Counter([string for item in input_list for string in item])
        for key in [key for key, value in count.items() if value >= min_count]:
            # Creates a list of the top-level indexes of the occurances of the present key.
            indexes = [index for index, item in enumerate(input_list) for string in item if key == string]
            # Adds the key and its indexes to output.
            out[key] = indexes
        return out
    else:
        count = Counter([string for string in input_list])
        for key in [key for key, value in count.items() if value >= min_count]:
            # Creates a list of the top-level indexes of the occurances of the present key.
            indexes = [index for index, string in enumerate(input_list) if key == string]
            # Adds the key and its indexes to output.
            out[key] = indexes
        return out
