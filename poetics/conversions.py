import re

from collections import Counter, OrderedDict

from poetics.patterning import assign_letters_to_dict


########################################################################################################################
# Tokenizing
########################################################################################################################
# Tokenizes text into words.
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
    tokenized.extend([word.lower() for word in line.strip().split()])
    return tokenized


# Generator for getting indexes of tokens in lines.
def get_line_indexes(token_list):
    start_index = 0
    for index, token in enumerate(token_list):
        if index == len(token_list) - 1:
            if token == '\n':
                yield(start_index, index)
            else:
                yield(start_index, index + 1)
        elif token == '\n':
            yield(start_index, index)
            start_index = index + 1


# Generator for getting indexes of tokens in sentences.
def get_sentence_indexes(token_list):
    terminators = ['.', '!', '?']
    start_index = 0
    for index, token in enumerate(token_list):
        if index == len(token_list) - 1:
            if index > start_index:
                yield(start_index, index)
        elif index == start_index and token == '\n':
            start_index += 1
        elif token in terminators:
            end_index = index
            for token2 in token_list[index:]:
                match = re.match("[^\w\'\s]+", token2)
                if match:
                    end_index += 1
                else:
                    break
            if index > start_index:
                yield(start_index, end_index)
            start_index = end_index + 1


# Generator for getting indexes of tokens in stanzas.
def get_stanza_indexes(token_list):
    start_index = 0
    for index, token in enumerate(token_list):
        if index == len(token_list) - 1:
            if token == '\n':
                yield(start_index, index)
            else:
                yield(start_index, index + 1)
        elif index == start_index and token == '\n':
            start_index += 1
        elif token == '\n':
            if token_list[index + 1] == '\n':
                if index > start_index:
                    yield (start_index, index)
                start_index = index + 1


# Tokenizes text and gets indexes of tokens belonging to lines, sentences, and stanzas.
def full_tokenize(text):
    # TODO: add exceptions for 'cause, 'em,, 'll, 'nuff, doin', goin', nothin', nothin', ol', somethin'

    # List of abbreviations that should be considered a single token.
    abbre = ('a\.m\.|p\.m\.|'
             '[vV][sS]\.|'
             '[eE]\.[gG]\.|[iI]\.[eE]\.|'
             'Mt\.|'
             'Mont\.|'
             'Bros\.|'
             '[cC]o\.|'
             'Corp\.|'
             'Inc\.|'
             'Ltd\.|'
             'Md\.|'
             'Dr\.|'
             'Ph\.|'
             'Rep\.|'
             'Rev\.|'
             'Sen\.|'
             'St\.|'
             'Messrs\.|'
             'Jr\.|'
             'Mr\.|'
             'Mrs\.|'
             'Ms\.|')

    # Pattern that splits tokens.
    pattern = ('(' + abbre +
               '[A-Z](?=\.)|'  # Any capital letter followed by a period.
               '[\'](?=[^\w])|'  # ' followed by a non-word character.
               '(?<=[^\w])\'|'  # ' preceeded by a non-word character.
               '\'\Z|\A\'|'  # ' at the start or end of the text.
               '[^\w\']|'  # Anything that isn't a word character or an apostrophe.
               '\s+'  # Any number of consecutive spaces.
               ')')

    tokens = [segment for segment in re.split(pattern, text) if segment]

    line_indexes = [index for index in get_line_indexes(tokens)]
    sentence_indexes = [index for index in get_sentence_indexes(tokens)]
    stanza_indexes = [index for index in get_stanza_indexes(tokens)]

    return tokens, line_indexes, sentence_indexes, stanza_indexes


########################################################################################################################
# Conversion
########################################################################################################################
# Converts parts of speech tags from tagger to those used by wordnet. Returns None if not relevant
def convert_pos(pos):
    relevant_letters = ['a', 'n', 'r', 'v']
    pos = pos.replace("J", "A").lower()
    if pos[0] in relevant_letters:
        return pos[0]
    else:
        return None


# Title cases titles/names. Does not handle subtitles presently.
# Future: handle roman numerals.
def title_case(text):
    decap = ['a', 'an', 'and', 'as', 'at', 'but', 'by', 'en', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'v',
             'v.', 'via', 'vs', 'vs.']
    words = re.split('[\t ]', text.title())
    for index, word in enumerate(words[1:]):
        if word.lower() in decap:
            words[index + 1] = word.lower()

    for index, word in enumerate(words):
        match = re.match('\w+\'\w+', word)
        if match:
            out_word = [word[0].upper()]
            out_word.extend([i.lower() for i in word[1:]])
            words[index] = ''.join(out_word)
    return ' '.join(words)


########################################################################################################################
# Grouping
########################################################################################################################
# Gets groups from a sound set.
def get_sound_set_groups(sound_list, tokenized_text, max_feature_distance):
    # Make a dictionary of sound appearances that are {Sound: [indexes of appearances]}.
    sound_set = index_unique_strings(sound_list, 2)
    output_dict = {}
    # Turn the sets of indexes into groups with a maximum distance between each consequitive member.
    for key, indexes in sound_set.items():
        groups = [num for num in get_distance_groups(indexes, max_feature_distance, 3)]
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


########################################################################################################################
# Indexing
########################################################################################################################
# Takes a list of strings and returns a dict of unique items and indexes of appearances.
# Handles lists of lists of strings or lists of strings (e.g. [['a', 'b'],['c', 'd']] or ['a', 'b']).
def index_unique_strings(input_list, min_count=None):
    min_count = min_count or 1
    out = {}
    if isinstance(input_list[0], list):
        count = Counter([string for item in input_list for string in item if string])
        for key in [key for key, value in count.items() if value >= min_count]:
            # Creates a list of the top-level indexes of the occurances of the present key.
            indexes = [index for index, item in enumerate(input_list) for string in item if key == string]
            # Adds the key and its indexes to output.
            out[key] = indexes
        return out
    else:
        count = Counter([string for string in input_list if string])
        for key in [key for key, value in count.items() if value >= min_count]:
            # Creates a list of the top-level indexes of the occurances of the present key.
            indexes = [index for index, string in enumerate(input_list) if key == string]
            # Adds the key and its indexes to output.
            out[key] = indexes
        return out


# Takes a list of features and turns it into a scheme.
def feats_to_scheme(features, lower=False, allow_blanks=False, max_unique=None):
    # If blanks aren't allowed, return None if any are present.
    if not allow_blanks:
        blanks = [feature for feature in features if not feature]
        if len(blanks) > 0:
            return None
    # Create an ordered dict of unique features that assigns each unique feature a letter.
    ordered_features = assign_letters_to_dict(OrderedDict.fromkeys([feature for feature in features
                                                                    if feature and not feature == ' ']), lower)
    # Return none if the number of features surpasses max unique.
    if max_unique:
        if len(ordered_features) > max_unique:
            return None
    # Return joined scheme
    return ''.join([' ' if not feature or feature == ' ' else ordered_features[feature] for feature in features])
