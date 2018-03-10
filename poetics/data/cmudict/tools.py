import json
import logging
import os
import re

import poetics.config as config
from poetics.data.cmudict.syllabify.syllabifier import load_language, stringify, syllabify


cmu_raw_path = os.path.join(config.directory, config.cmudict_raw_path)
cmu_path = os.path.join(config.directory, config.cmudict_path)
cmu_wordlist_path = os.path.join(config.directory, config.cmudict_wordlist_path)
cmu_phonetic_path = os.path.join(config.directory, config.cmudict_phonetic_path)
alt_spellings_path = os.path.join(config.directory, config.alt_spellings_path)


# Processes a raw copy of cmudict (from https://github.com/cmusphinx/cmudict). Creates a .txt wordlist and a json
# copy of cmudict. Also adds spellings from alternate_spellings.json.
def process_raw_cmudict():
    with open(cmu_raw_path, encoding="utf-8") as f:
        raw_cmu = f.readlines()

    with open(alt_spellings_path, encoding="utf-8") as f:
        alt_spellings = json.load(f)

    # Turn raw data in dictionary.
    regex = re.compile('\(\d+\)')
    out_dict = {}
    for line in raw_cmu:
        split = line.split()
        if '#' in split:
            split = split[:split.index("#")]
        word = regex.sub('', split[0])
        if word not in out_dict:
            out_dict[word] = []
        out_dict[word].append(split[1:])

    #  Add words from alternate_spellings.
    for key, value in alt_spellings.items():
        out_dict[key] = out_dict[value]

    # Write json copy of cmudict.
    with open(cmu_path, 'w', encoding="utf-8") as f:
        json.dump(out_dict, f, sort_keys=True, separators=(',', ':'))

    # Write wordlist (used by pyEnchant).
    wordlist = sorted([*out_dict])
    with open(cmu_wordlist_path, 'w', encoding="utf-8") as f:
        f.writelines(line + '\n' for line in wordlist)


# Takes standard version of cmudict and rewrites each pronunciation as a series of syllables which each store stress,
# onset, nucleus, coda.
def phoneticize_cmudict():

    def syllable_gen(entries):
        for entry, prons in entries.items():
            pron_out = []
            for pron in prons:
                pron_out.append(stringify(syllabify(language, pron)))
            yield (entry, pron_out)

    with open(cmu_path, encoding="utf-8") as f:
        cdict = json.load(f)

    language = load_language(config.directory + "/data/cmudict/syllabify/english.cfg")

    syll_dict = {entry: pronunciations for entry, pronunciations in syllable_gen(cdict)}

    vowels = ['AA', 'AE', 'AH', 'AO', 'AW', 'AX', 'AY', 'EH', 'ER', 'EY', 'IH', 'IX', 'IY', 'OW', 'OY', 'UH', 'UW']

    phoneticized_dict = {}
    for key, pronunciations in syll_dict.items():
        out_pronunciations = []
        for pronunciation in pronunciations:
            out_pronunciation = []
            syllables = pronunciation.split('-')
            for syllable in syllables:
                syllable_out = ["", "", "", ""]
                strip = syllable.strip()
                if "1" in strip:
                    syllable_out[0] = 1
                    strip = strip.replace("1", "")
                else:
                    syllable_out[0] = 0
                    strip = strip.replace("2", "")
                split = strip.split()
                onset = []
                coda = []
                try:
                    nucleus = next(phoneme for phoneme in split if phoneme in vowels)
                    syllable_out[2] = nucleus
                    nucleus_index = split.index(nucleus)
                    for phoneme in split[:nucleus_index]:
                        onset.append(phoneme)
                    syllable_out[1] = ' '.join(onset)
                    for phoneme in split[nucleus_index + 1:]:
                        coda.append(phoneme)
                    syllable_out[3] = ' '.join(coda)
                except StopIteration:
                    logging.error("No nucleus found for %s (%s)", key, syllable)
                    for phoneme in split:
                        onset.append(phoneme)
                    syllable_out[1] = ' '.join(onset)
                out_pronunciation.append(syllable_out)
            out_pronunciations.append(out_pronunciation)
        phoneticized_dict[key] = out_pronunciations

    with open(cmu_phonetic_path, 'w', encoding="utf-8") as f:
        json.dump(phoneticized_dict, f, sort_keys=True, separators=(',', ':'))


# Adds some line breaks to the json cmudicts to make them less awful to deal with.
def pretty_cmudicts():
    with open(cmu_path, encoding="utf-8") as data:
        raw_simple = data.read()

    with open(cmu_path, 'w', encoding="utf-8") as f:
        f.write(re.sub('\]\],', ']],\n', raw_simple))

    with open(cmu_phonetic_path, encoding="utf-8") as data:
        raw_phonetic = data.read()

    with open(cmu_phonetic_path, 'w', encoding="utf-8") as f:
        f.write(re.sub('\]\]\],', ']]],\n', raw_phonetic))


if __name__ == "__main__":
    process_raw_cmudict()
    phoneticize_cmudict()
    pretty_cmudicts()
