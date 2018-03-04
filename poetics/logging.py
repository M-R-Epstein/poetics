import logging
import re


# Logs the provided string as a level 1 header.
def header1(head):
    width = 50
    top = ('=' * width)
    bot = ('=' * width)
    whitespace = ' ' * ((width - len(head))//2)
    logging.info(top)
    logging.info('%s%s', whitespace, head)
    logging.info(bot)


# Logs the provided string as a two-line level 1 header.
def header1d(head1, head2):
    width = 50
    top = ('=' * width)
    bot = ('=' * width)
    whitespace1 = ' ' * ((width - len(head1))//2)
    whitespace2 = ' ' * ((width - len(head2))//2)
    logging.info(top)
    logging.info('%s%s', whitespace1, head1)
    logging.info('%s%s', whitespace2, head2)
    logging.info(bot)


# Logs the provided string as a level 2 header.
def header2(head):
    width = 50 - (len(head) + 2)
    left = '=' * (width // 2)
    right = '=' * ((width // 2) + (width % 2 > 0))
    logging.info("%s %s %s", left, head, right)


# Logs the provided string as a level 3 header.
def header3(head):
    width = 50 - (len(head) + 2)
    left = '-' * (width // 2)
    right = '-' * ((width // 2) + (width % 2 > 0))
    logging.info("%s %s %s", left, head, right)


# Joins a list in proper grammatical fashion (with oxford comma).
def join_list_proper(lst, term='and'):
    if len(lst) == 1:
        return lst[0]
    elif len(lst) == 2:
        return lst[0] + ' ' + term + ' ' + lst[1]
    elif len(lst) > 2:
        return ', '.join(lst[0:-1]) + ', ' + term + ' ' + lst[-1]


# Converts a scansion made up of 0's and 1's into a readable form.
def convert_scansion(scansion):
    converted_scan = []
    for scan in scansion:
        if not scan:
            converted_scan.append(None)
        else:
            converted = scan.replace('0', 'u').replace('1', '/')
            converted = re.sub("(̲?[u/])(?=̲?[u/])", '\g<1> ', converted, )
            converted_scan.append(converted)
    return converted_scan


# Takes a list of tags and a list of tokenized words and attempts to align them in a readable form in the log.
# If above = True, then the tags go above the text instead of under it.
def tags_with_text(token_tuples, line_num=None, above=False, logger=logging.info):
    line_out = ''
    offset = 0
    # For untagged tokens, add a number of spaces to line out equal to its length.
    for token, tag in token_tuples:
        if not tag:
            line_out += ' ' * len(token)
        else:
            # The .count portion is to account for zero length characters (presently combining underline).
            diff = len(token) - (len(tag) - tag.count('̲'))
            offdiff = diff + offset
            if offdiff > 0:
                # Puts spaces equal to half (rounded down) the difference between tag/word length before tag
                # Puts spaces equal to half (rounded up) the difference between tag/word length after tag
                line_out += (' ' * (offdiff // 2)) \
                            + tag \
                            + (' ' * (offdiff // 2 + (offdiff % 2 > 0)))
                offset = 0
            else:
                line_out += tag
                # Offset is just keeping track of how far we are pushed to the right by tag length>word length
                offset += diff
    # Output each line with the tags over/under
    if above is True:
        logger(line_out)
    if line_num:
        logger("%s (%s)", ''.join([token for token, tag in token_tuples]), line_num)
    else:
        logger(''.join([token for token, tag in token_tuples]))
    if above is False:
        logger(line_out)


# Takes a sound set and prints it.
def print_sound_set(name, feature, tokenized_text):
    sound_sets = []
    for sound, groups in feature.items():
        word_sets = []
        for indexes in groups:
            words = [tokenized_text[index] for index in indexes]
            word_sets.append(', '.join(words))
        sound_set = '; '.join(word_sets)
        sound_sets.append(sound + ': ' + sound_set)
    header3(name)
    for sset in sound_sets:
        logging.info(sset)


