import re

from poetics.conversions import tokenize


class Line:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.plaintext = text
        self.tokenized_text = []
        self.word_indexes = ()

        self.initial_word = None
        self.final_word = None

        self.pos = []

        self.rhyme_candidates = []
        self.rhyme = None
        self.asso_candidates = []
        self.assonance = None
        self.cons_candidates = []
        self.consonance = None

        # i_ as short for initial
        self.i_rhyme_candidates = []
        self.i_rhyme = None
        self.i_asso_candidates = []
        self.i_assonance = None
        self.i_cons_candidates = []
        self.i_consonance = None

        self.scansion = []

        # Don't bother tokenizing or finding first/last words if there aren't any letters in the plaintext
        if re.search('[a-zA-Z]', self.plaintext):
            self.tokenized_text = tokenize(text)
            self.initial_word = self.tokenized_text[0]
            self.final_word = self.tokenized_text[-1]

    def get_rhymes(self):
        # Note: initial assonance/consonance are not used for anything presently.
        if self.parent:
            if self.final_word:
                self.rhyme_candidates = self.parent.words[self.final_word].p_rhymes
                self.asso_candidates = self.parent.words[self.final_word].stressed_vowels
                self.cons_candidates = self.parent.words[self.final_word].stress_final_consonants
            if self.initial_word:
                self.i_rhyme_candidates = self.parent.words[self.initial_word].p_rhymes
                self.i_asso_candidates = self.parent.words[self.final_word].stressed_vowels
                self.i_cons_candidates = self.parent.words[self.final_word].stress_final_consonants
            # If there is only one candidate for any given feature, set the feature to that candidate.
            if len(self.rhyme_candidates) == 1:
                self.rhyme = self.rhyme_candidates[0]
            if len(self.asso_candidates) == 1:
                self.assonance = self.asso_candidates[0]
            if len(self.cons_candidates) == 1:
                self.consonance = self.cons_candidates[0]
            if len(self.i_rhyme_candidates) == 1:
                self.i_rhyme = self.i_rhyme_candidates[0]
            if len(self.i_asso_candidates) == 1:
                self.i_assonance = self.i_asso_candidates[0]
            if len(self.i_cons_candidates) == 1:
                self.i_consonance = self.i_cons_candidates[0]

    def get_scansion(self):
        if self.tokenized_text:
            for word in self.tokenized_text:
                # If there is only one (unique) stress pattern, then use that.
                if self.parent.words[word].stresses:
                    if len(set(self.parent.words[word].stresses)) == 1:
                        self.scansion.append(self.parent.words[word].stresses[0].replace('2', '0'))
                    # Note: May want a better solution for words with multiple possible stress patterns.
                    # Note: This mostly seems to occur in words that are ambigious w/o stress (present)
                    # If there are multiple (unique) stress patterns, currently uses the first one.
                    elif len(set(self.parent.words[word].stresses)) > 1:
                        self.scansion.append(self.parent.words[word].stresses[0].replace('2', '0'))
                    # Put in a question mark if we have no stress pattern
                    else:
                        self.scansion.append('?')
                else:
                    self.scansion.append('?')
            return self.scansion
        else:
            return ''
