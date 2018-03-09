"""P2TK syllabifier for python 3.x.
Modified from python 2.x P2TK syllabifier by Joshua Tauberer, based on code originally written by Charles Yang.

The syllabifier requires a language configuration which specifies the set of phonemes which are consonants and vowels
(syllable nuclei), as well as the set of permissible onsets.

Then call syllabify with a language configuration object and a word represented as a string (or list) of phonemes.

Returned is a data structure representing the syllabification. What you get is a list of syllables. Each syllable is a
tuple of (stress, onset, nucleus, coda). stress is None or an integer stress level attached to the nucleus phoneme on
input. onset, nucleus, and coda are lists of phonemes.

Example:
import syllabifier
language = syllabifier.English # or: syllabifier.load_language("english.cfg")
syllables = syllabifier.syllabify(language, "AO2 R G AH0 N AH0 Z EY1 SH AH0 N Z")

The syllables variable then holds the following:
[ (2, [],     ['AO'], ['R']),
  (0, ['G'],  ['AH'], []),
  (0, ['N'],  ['AH'], []),
  (1, ['Z'],  ['EY'], []),
  (0, ['SH'], ['AH'], ['N', 'Z'])]

You could process that result with this type of loop:

for stress, onset, nucleus, coda in syllables :
  print " ".join(onset), " ".join(nucleus), " ".join(coda)

You can also pass the result to stringify to get a nice printable representation of the syllables, with periods
separating syllables:
print syllabify.stringify(syllables)
"""
import logging


def load_language(filename):
    # This function loads up a language configuration file and returns the configuration to be passed to the
    # syllabify function.

    language = {"consonants": [], "vowels": [], "onsets": []}

    f = open(filename, "r")
    section = None
    for line in f:
        line = line.strip()
        if line in ("[consonants]", "[vowels]", "[onsets]"):
            section = line[1:-1]
        elif not section:
            logging.error("File must start with a section header such as [consonants].")
        elif section not in language:
            logging.error("Invalid section: %s", section)
        else:
            language[section].append(line)

    for section in "consonants", "vowels", "onsets":
        if len(language[section]) == 0:
            logging.error("File does not contain any consonants, vowels, or onsets.")

    return language


def syllabify(language, word):
    # Syllabifies the word, given a language configuration loaded with loadLanguage. word is either a string of phonemes
    # from the CMU pronouncing dictionary set (with optional stress numbers after vowels), or a Python list of phonemes,
    # e.g. "B AE1 T" or ["B", "AE1", "T"]'''

    if type(word) == str:
        word = word.split()

    syllables = []  # This is the returned data structure.

    internuclei = []  # This maintains a list of phonemes between nuclei.

    for phoneme in word:

        phoneme = phoneme.strip()
        if phoneme == "":
            continue
        stress = None
        if phoneme[-1].isdigit():
            stress = int(phoneme[-1])
            phoneme = phoneme[0:-1]

        if phoneme in language["vowels"]:
            # Split the consonants seen since the last nucleus into coda and onset.

            coda = None
            onset = None

            # If there is a period in the input, split there.
            if "." in internuclei:
                period = internuclei.index(".")
                coda = internuclei[:period]
                onset = internuclei[period + 1:]

            else:
                # Make the largest onset we can. The 'split' variable marks the break point.
                for split in range(0, len(internuclei) + 1):
                    coda = internuclei[:split]
                    onset = internuclei[split:]

                    # If we are looking at a valid onset, or if we're at the start of the word
                    # (in which case an invalid onset is better than a coda that doesn't follow
                    # a nucleus), or if we've gone through all of the onsets and we didn't find
                    # any that are valid, then split the nonvowels we've seen at this location.
                    if " ".join(onset) in language["onsets"] \
                            or len(syllables) == 0 \
                            or len(onset) == 0:
                        break

            # Tack the coda onto the coda of the last syllable. Can't do it if this
            # is the first syllable.
            if len(syllables) > 0:
                syllables[-1][3].extend(coda)

            # Make a new syllable out of the onset and nucleus.
            syllables.append((stress, onset, [phoneme], []))

            # At this point we've processed the internuclei list.
            internuclei = []

        elif phoneme not in language["consonants"] and phoneme != ".":
            logging.error("Invalid phoneme: %s in %s", phoneme, word)

        else:  # a consonant
            internuclei.append(phoneme)

    # Done looping through phonemes. We may have consonants left at the end.
    # We may have even not found a nucleus.
    if len(internuclei) > 0:
        if len(syllables) == 0:
            syllables.append((None, internuclei, [], []))
        else:
            syllables[-1][3].extend(internuclei)

    return syllables


def stringify(syllables):
    # This function takes a syllabification returned by syllabify and turns it into a string, with phonemes spearated by
    # spaces and syllables spearated by -.
    ret = []
    for syl in syllables:
        stress, onset, nucleus, coda = syl
        if stress and len(nucleus) != 0:
            nucleus[0] += str(stress)
        ret.append(" ".join(onset + nucleus + coda))
    return " - ".join(ret)
