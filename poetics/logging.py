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


# Logs the provided string as a level 2 header.
def header2(head):
    width = 50 - (len(head) + 2)
    left = '=' * (width // 2)
    right = '=' * ((width // 2) + (width % 2 > 0))
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
        converted = scan.replace('0', 'u').replace('1', '/')
        converted = re.sub("(̲?[u/])(?=[u/])", '\g<1> ', converted, )
        converted_scan.append(converted)
    return converted_scan


# Takes a list of tags and a list of tokenized words and attempts to align them in a readable form in the log.
# If above = True, then the tags go above the text instead of under it.
def tags_with_text(tokenized_text, tags, line_num=None, above=False):
    line_out = ''
    offset = 0
    for index, word in enumerate(tokenized_text):
        # the .count portion is to account for zero length characters (presently combining underline is the only one).
        dif = len(tokenized_text[index]) - (len(tags[index]) - tags[index].count('̲'))
        offdif = dif + offset
        if offdif > 0:
            # Puts spaces equal to half (rounded down) the difference between tag/word length before tag
            # Puts spaces equal to half (rounded up) the difference between tag/word length after tag
            line_out += (' ' * (offdif // 2)) \
                        + tags[index] \
                        + (' ' * (offdif // 2 + (offdif % 2 > 0))) \
                        + ' '
            offset = 0
        else:
            line_out += tags[index] + ' '
            # Offset is just keeping track of how far we are pushed to the right by tag length>word length
            offset += dif
    # Output each line with the tags over/under
    if above is True:
        logging.info(line_out)
    if line_num:
        logging.info("%s (%s)", ' '.join(tokenized_text), line_num)
    else:
        logging.info(' '.join(tokenized_text))
    if above is False:
        logging.info(line_out)


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
    logging.info('%s: %s', name, ' | '.join(sound_sets))
