import logging
import nltk
from translations import get_phonetic, get_rhymes
from collections import Counter

cmudict = nltk.corpus.cmudict.dict()


class Word:
    def __init__(self, word, pronunciations=None, parent=None):
        self.parent = parent
        self.plaintext = word
        self.pronunciations = pronunciations
        self.stresses = []
        self.rhymes = []
        self.pos = Counter()
        self.wordnet_pos = Counter()
        self.synsets = {}

        # Get a pronunciation if the user hasn't provided one already.
        if self.pronunciations:
            logging.info("Pronunciation for \"%s\" provided as \"%s\"", word, ' '.join(self.pronunciations[0]))
        else:
            self.pronunciations = get_phonetic(word)

        if self.pronunciations:
            for index, pronunciation in enumerate(self.pronunciations):
                # Joins all of the sounds together into a single string per pronunciation
                joined = ''.join(sound for pronunciation in self.pronunciations[index] for sound in pronunciation)
                # Filters to only keep digits
                stress = ''.join(filter(lambda x: x.isdigit(), joined))
                if len(stress) == 1:
                    self.stresses.append('3')
                else:
                    self.stresses.append(stress)
                # Sets the digit only versions as our stresses

                # Gets rhymes
                self.rhymes = get_rhymes(self.pronunciations)

    # Places (lists of) synsets in self.synsets under their pos key
    def get_synsets(self):
        from nltk.corpus import wordnet
        for pos in self.wordnet_pos:
            returned = wordnet.synsets(self.plaintext, pos=pos)
            # Note: Should probably try specifying no part of speech if we get no return. Depends on quality of tagger.
            # TODO: Need to check out Morphy for handling word forms not in wordnet
            logging.debug('Search for %s as %s returned:\n %s', self.plaintext, pos, returned)
            if returned:
                self.synsets[pos] = returned
