import logging
import re
from collections import Counter

from nltk.corpus import wordnet

from poetics.lookups import get_phonetic, get_rhymes


class Word:
    def __init__(self, word, pronunciations=None, parent=None):
        self.parent = parent
        self.plaintext = word

        self.pronunciations = []
        self.syl_pronunciations = pronunciations
        self.stresses = []

        self.p_rhymes = []
        self.word_init_consonants = []
        self.stressed_vowels = []
        self.stress_initial_consonants = []
        self.stress_final_consonants = []
        self.stress_bracket_consonants = []

        self.pos = Counter()
        self.wordnet_pos = Counter()
        self.synsets = {}

        # Get a pronunciation if the user hasn't provided one already.
        if self.syl_pronunciations:
            logging.info("Pronunciation for \"%s\" provided as \"%s\"", word, self.syl_pronunciations[0])
            # If the user did provide one, assign it appropriately
            self.pronunciations.append(re.sub(' - ', ' ', self.syl_pronunciations[0]).split(' '))
        else:
            self.pronunciations, self.syl_pronunciations = get_phonetic(word)

        if self.pronunciations:
            stress_list = []
            for index, pronunciation in enumerate(self.pronunciations):
                # Joins all of the sounds together into a single string per pronunciation
                joined = ''.join(sound for pronunciation in self.pronunciations[index] for sound in pronunciation)
                # Filters to only keep digits
                stress = ''.join(filter(lambda x: x.isdigit(), joined)).replace('2', '0')
                stress_list.append(stress)
            self.stresses = list(set(stress_list))
            (self.p_rhymes, self.word_init_consonants, self.stressed_vowels, self.stress_initial_consonants,
             self.stress_final_consonants, self.stress_bracket_consonants) = get_rhymes(self.pronunciations,
                                                                                        self.syl_pronunciations)


# Places (lists of) synsets in self.synsets under their pos key.
def get_synsets(self):
    for pos in self.wordnet_pos:
        returned = wordnet.synsets(self.plaintext, pos=pos)
        # Note: Should probably try specifying no part of speech if we get no return. Depends on quality of tagger.
        # TODO: Need to check out Morphy for handling word forms for wordnet
        logging.debug('Search for %s as %s returned:\n %s', self.plaintext, pos, returned)
        if returned:
            self.synsets[pos] = returned
