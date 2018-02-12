import csv
import json

from nltk.corpus import cmudict

from poetics.text.syllabify.syllabifier import load_language, stringify, syllabify
import poetics.config as config


# Writes a wordlist from CMUdict to text/wordlist.txt
def write_cmu_wordlist():

    wordlist = cmudict.words()

    with open('text/wordlist.txt', 'w') as file:
        for index, items in enumerate(wordlist):
            wordlist[index] = wordlist[index] + "\n"
        file.writelines(wordlist)


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

    with open('text/wordlistfreq.txt', 'w') as file:
        file.writelines(output)


# Syllabifies cmudict and writes it as cmudict_syllabified.json
def syllabify_cmudict():

    def syllable_gen(entries):
        for entry, pronunciations in entries.items():
            pron_out = []
            for pronunciation in pronunciations:
                pron_out.append(stringify(syllabify(language, pronunciation)))
            yield (entry, pron_out)

    cmu_dict = cmudict.dict()
    language = load_language(config.directory + "text/syllabify/english.cfg")

    syllabified_dict = {entry: pronunciations for entry, pronunciations in syllable_gen(cmu_dict)}

    with open(config.directory + '/text/cmudict_syllabified.json', 'w') as file:
        json.dump(syllabified_dict, file, sort_keys=True, separators=(',', ':'))


def write_json_cmudict():
    cmu_dict = cmudict.dict()
    with open(config.directory + '/text/cmudict.json', 'w') as file:
        json.dump(cmu_dict, file, sort_keys=True, separators=(',', ':'))
