import logging

from poetics.lookups import get_pronunciations, check_onomatopoetic
from poetics.classes.pronunciation import Pronunciation
from poetics.stemmer import stem


class Word:
    def __init__(self, word, user_pronunciation=None, parent=None):
        self.parent = parent
        self.token = word
        self.stem = stem(word)
        self.pronunciations = None
        self.onomatopoetic = check_onomatopoetic(word)

        # Deal with user provided pronunciations.
        if user_pronunciation:
            vowels = ['AA', 'AE', 'AH', 'AO', 'AW', 'AX', 'AY', 'EH', 'ER', 'EY', 'IH', 'IX', 'IY', 'OW', 'OY', 'UH',
                      'UW']
            logging.info("Pronunciation for \"%s\" provided as \"%s\"", word, user_pronunciation)
            out_pronunciation = []
            f_pronunciations = []
            syllables = user_pronunciation.split('-')
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
                    for phoneme in split:
                        onset.append(phoneme)
                    syllable_out[1] = ' '.join(onset)
                out_pronunciation.append(syllable_out)
                f_pronunciations.append(Pronunciation(out_pronunciation, self))
                self.pronunciations = tuple(f_pronunciations)
        # If there isn't a user provided pronunciation, get a pronunciation.
        else:
            f_pronunciations = []
            pronunciations = get_pronunciations(word)
            for pronunciation in pronunciations:
                f_pronunciations.append(Pronunciation(pronunciation, self))
            self.pronunciations = tuple(f_pronunciations)

    def __str__(self) -> str:
        return self.token

    def __repr__(self) -> str:
        return '%s (%s)' % (super().__repr__(), self.token)
