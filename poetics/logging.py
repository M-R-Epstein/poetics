import logging


def convert_scansion(scansion):
    converted_scan = []
    for scan in scansion:
        converted = scan.replace('0', 'u')
        converted = converted.replace('1', '/')
        converted_scan.append(converted)
    return converted_scan


# Takes a list of tags and a list of tokenized words and attempts to align them in a readable form in the log.
def tags_with_text(tokenized_text, tags, line_num=None, above=False):
    line_out = ''
    offset = 0
    # Use a bunch of nonsense to center the tags under the words
    for index, word in enumerate(tokenized_text):
        dif = len(tokenized_text[index]) - len(tags[index])
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
