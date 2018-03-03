import csv
import json
import logging
import os

from nltk.corpus import cmudict

import poetics.config as config
from poetics.text.syllabify.syllabifier import load_language, stringify, syllabify

with open(os.path.join(config.directory, config.cmudict_path)) as file:
    cmu_dict = json.load(file)

with open(os.path.join(config.directory, config.syllabified_path)) as file:
    syllabified_dict = json.load(file)


# Writes a wordlist from CMUdict to text/wordlist.txt
def write_cmu_wordlist():

    wordlist = cmudict.words()

    with open('text/wordlist.txt', 'w') as f:
        for index, items in enumerate(wordlist):
            wordlist[index] = wordlist[index] + "\n"
        f.writelines(wordlist)


# Pulls out the words from frequencylist that are present in CMUDict and writes a sorted list to text/wordlistfreq.txt
def write_cmu_wordlist_frequencies():
    wordlist = cmudict.words()

    frequency_source = {}
    frequency_list = {}
    output = []

    with open('text/frequencylist.txt') as data:
        as_csv = csv.reader(data, delimiter='\t')
        for row in as_csv:
            frequency_source[row[0]] = row[1]

    for word in wordlist:
        if word in frequency_source:
            frequency_list[word] = int(frequency_source[word])

    # Create a sorted version of our dictionary
    sort = [(k, frequency_list[k]) for k in sorted(frequency_list, key=frequency_list.get, reverse=True)]

    # Prepare output lines
    for item in sort:
        output.append(item[0] + "\t" + str(item[1]) + "\n")

    with open('text/wordlistfreq.txt', 'w') as f:
        f.writelines(output)


# Syllabifies cmudict and writes it as cmudict_syllabified.json
def syllabify_cmudict():

    def syllable_gen(entries):
        for entry, pronunciations in entries.items():
            pron_out = []
            for pronunciation in pronunciations:
                pron_out.append(stringify(syllabify(language, pronunciation)))
            yield (entry, pron_out)

    cdict = cmudict.dict()
    language = load_language(config.directory + "text/syllabify/english.cfg")

    syll_dict = {entry: pronunciations for entry, pronunciations in syllable_gen(cdict)}

    with open(config.directory + '/text/cmudict_syllabified.json', 'w') as f:
        json.dump(syll_dict, f, sort_keys=True, separators=(',', ':'))


def phoneticize_cmudict():
    vowels = ['AA', 'AE', 'AH', 'AO', 'AW', 'AX', 'AY', 'EH', 'ER', 'EY', 'IH', 'IX', 'IY', 'OW', 'OY', 'UH', 'UW']
    s_dict = syllabified_dict

    phoneticized_dict = {}
    for key, pronunciations in s_dict.items():
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

    with open(config.directory + '/text/cmudict_phoneticized.json', 'w') as f:
        json.dump(phoneticized_dict, f, sort_keys=True, separators=(',', ':'))


def write_json_cmudict():
    cm_dict = cmudict.dict()
    with open(config.directory + '/text/cmudict.json', 'w') as f:
        json.dump(cm_dict, f, sort_keys=True, separators=(',', ':'))
