import logging
import re
from itertools import product

import poetics.config as config
from poetics.conversions import tokenize, split_by_tokens


class Line:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.line_num = None
        self.plaintext = text.rstrip()
        self.tokenized_text = []
        self.split_by_tokens = []
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
        self.final_scansion = []
        self.stress = []
        self.syllables = 0
        self.syllables_base = 0
        self.multi_length = False

        # Don't bother tokenizing or finding first/last words if there aren't any letters in the plaintext
        if re.search('[a-zA-Z]', self.plaintext):
            self.tokenized_text = tokenize(text)
            self.initial_word = self.tokenized_text[0]
            self.final_word = self.tokenized_text[-1]
            self.split_by_tokens = split_by_tokens(self.tokenized_text, self.plaintext)

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

    # Gets stress patterns for all tokenized words in line.
    def get_stress(self):
        if not self.pos:
            logging.warning("Parts of speech required for scansion. Generating parts of speech...")
            self.parent.get_pos()
        for index, word in enumerate(self.tokenized_text):
            self.stress.append(self.parent.words[word].stresses)

    # Gets the number of syllables in the line, noting if there are multiple possible syllable lengths.
    def get_length(self):
        syllables = 0
        for index, stress in enumerate(self.stress):
            syll_lengths = [len(stress) for stress in self.stress[index]]
            # If all stress patterns indicate the same number of syllables, add it to our count.
            if max(syll_lengths) == min(syll_lengths):
                syllables += syll_lengths[0]
            # Otherwise, don't add it to our count, and set multi_length to indicate the line has variable length.
            else:
                self.multi_length = True
        # If the line isn't marked on variable length, then its final syllable count is what we counted.
        if not self.multi_length:
            self.syllables = syllables
        # If not, what we counted is the base syllable length not accounting for words that might vary.
        else:
            self.syllables_base = syllables

    # Resolves stresses and syllable counts for lines that had multiple length possibilities.
    def set_length(self, length_count):
        multi_length_words = []
        for index, stress in enumerate(self.stress):
            syll_lengths = [len(stress) for stress in self.stress[index]]
            if not max(syll_lengths) == min(syll_lengths):
                multi_length_words.append((index, syll_lengths))
        # If there's only one multi-length word, combinations is just the lengths of that word.
        if len(multi_length_words) == 1:
            combinations = [[length] for key, lengths in multi_length_words for length in lengths]
        # Otherwise, create a list of all possible combinations of stress lengths in the line.
        else:
            combinations = [pros for pros in product(*[lengths for key, lengths in multi_length_words])]
        # Loop through our most likely line lengths and gets matches.
        matches = []
        for length, count in length_count:
            matches = [combination for combination in combinations if sum(combination, self.syllables_base) == length]
            if matches:
                break
        # If we got no matches, then we use the first stress length for each multi-length word.
        if not matches:
            for index, (word_index, stresses) in enumerate(multi_length_words):
                self.stress[word_index] = [stress for stress in self.stress[word_index]
                                           if len(stress) == len(self.stress[word_index][0])]
        # If we got a match, then get rid of stress patterns that are the wrong length for each word.
        # Note: currently uses the first combination if we get multiple possibile combinations.
        else:
            for index, (word_index, stresses) in enumerate(multi_length_words):
                self.stress[word_index] = [stress for stress in self.stress[word_index]
                                           if len(stress) == matches[0][index]]
        # Set the line length.
        for key, lengths in multi_length_words:
            self.syllables += len(self.stress[key][0])
        self.syllables += self.syllables_base

    def get_scansion(self):
        if self.stress:
            for index, stress in enumerate(self.stress):
                if len(stress[0]) == 1:
                    # Sets the stress of the word as unstressed (0) if it's in the unstressed override list.
                    if self.tokenized_text[index] in config.unstressed_words:
                        self.stress[index] = ['U']
                    # Set as stressed (1) if its part of speech is in the stress tendency list.
                    elif self.pos[index] in config.stress_pos:
                        self.stress[index] = ['S']
                    # If the word's part of speech is in the weak stress tendency list, then set it as W.
                    elif self.pos[index] in config.weak_stress_pos:
                        self.stress[index] = ['W']
                    # If the word's part of speech  is in the neutral stress tendency list, then set it as N.
                    elif self.pos[index] in config.neutral_stress_pos:
                        self.stress[index] = ['N']
                    # Otherwise, set as unstressed.
                    else:
                        self.stress[index] = ['U']
        else:
            return ''
