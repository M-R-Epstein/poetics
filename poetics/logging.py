import logging


# Logs a scansion in a readable form.
def print_scansion(scansion, prefix=''):
    if prefix:
        prefix = prefix + ' '
    # Business with index_mod is to handle line numbers while accounting for blanks.
    index_mod = 1
    logging.info("%sScansion:", prefix)
    # Reformats 3/4 (stressed/unstressed single syllable words).
    for index, scan in enumerate(scansion):
        scansion[index] = scansion[index].replace("3", "̲0")
        scansion[index] = scansion[index].replace("4", "̲1")
        if scan == '':
            logging.info('')
            index_mod -= 1
        else:
            logging.info("%s (%s)", scansion[index], index + index_mod)


# Takes a list of tags and a list of tokenized words and attempts to align them in a readable form in the log.
def tags_under_text(tokenized_text, tags):
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
    # Output each line with the POS tags under it
    logging.info(' '.join(tokenized_text))
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
