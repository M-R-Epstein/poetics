import re

import poetics.config as config


class Token:
    def __init__(self, token, index, parent=None):
        self.parent = parent
        self.index = index
        self.token = token
        self.is_punct = False
        self.is_wspace = False  # Whitespace boolean.

        self.stem = None
        self.pronunciations = None
        self.lemma = None

        self.pos = None
        self.pos_secondary = []
        self.simple_pos = None
        self.dependency = None

        self.stress_tendency = None
        self.stress_override = None

        # s_feature tracks if all pronunciations share a given feature.
        self.s_stress = None  # Stress pattern.
        self.s_syllables = None  # Number of syllables.
        self.s_str_vowel = None  # Vowel sound in the stressed syllable.
        self.s_str_ini_con = None  # First single consonant sound in the stressed syllable.
        self.s_str_fin_con = None  # Last single consonant sound in the stressed syllable.
        self.s_str_bkt_cons = None  # All consonant sounds in the stressed syllable.
        self.s_word_ini_con = None  # First single consonant sound in the word.
        self.s_p_rhyme = None  # Perfect rhyme.
        self.s_r_rhyme = None  # Rich rhyme.

        spaces = re.match("\s+", token)
        non_word = re.match("\W", token)
        if spaces:
            self.is_wspace = True
        elif non_word:
            self.is_punct = True
        # Get pronunciations from the matching word dict entry.
        if not self.is_punct and not self.is_wspace:
            self.pronunciations = list(parent.words[self.token.lower()].pronunciations[:])
            self.stem = parent.words[self.token.lower()].stem
            if len(self.pronunciations) == 1:
                self.s_stress = self.s_syllables = self.s_str_vowel = self.s_str_ini_con = self.s_str_fin_con = \
                    self.s_str_bkt_cons = self.s_word_ini_con = self.s_p_rhyme = self.s_r_rhyme = True
            else:
                self.check_features()

    def __str__(self) -> str:
        return self.token

    def __repr__(self) -> str:
        return '%s (%s)' % (super().__repr__(), self.token)

    # Set booleans that indicate if all instances of a given feature in the token's pronunciations match.
    def check_features(self):
        features = ['stress', 'str_vowel', 'str_ini_con', 'str_fin_con', 'str_bkt_cons', 'word_ini_con', 'p_rhyme',
                    'r_rhyme']

        if len(self.pronunciations) > 1:
            if len(set([len(pronunciation.syllables) for pronunciation in self.pronunciations])) > 1:
                self.s_syllables = False
            else:
                self.s_syllables = True

            for feature in features:
                if len(set([getattr(pronunciation, feature) for pronunciation in self.pronunciations])) > 1:
                    setattr(self, 's_' + feature, False)
                else:
                    setattr(self, 's_' + feature, True)
        else:
            self.s_stress = self.s_syllables = self.s_str_vowel = self.s_str_ini_con = self.s_str_fin_con = \
                self.s_str_bkt_cons = self.s_word_ini_con = self.s_p_rhyme = self.s_r_rhyme = True

    # Culls pronunciations where feature is not equal to pattern.
    def cull_pronunciations(self, feature, pattern):
        remove = []
        # Special case for syllables as syllables specifies the number of syllables rather than a form they must match.
        if feature == 'syllables':
            for pronunciation in self.pronunciations:
                if not len(pronunciation.syllables) == pattern:
                    remove.append(pronunciation)
        else:
            for pronunciation in self.pronunciations:
                if not getattr(pronunciation, feature) == pattern:
                    remove.append(pronunciation)
        for pronunciation in remove:
            self.pronunciations.remove(pronunciation)
        self.check_features()

    # Sets stress tendency based on part of speech.
    def set_stress_tendency(self):
        if len(self.pronunciations[0].stress) == 1:
            # Sets the stress tendency of the token as unstressed if it's in the unstressed override list.
            if self.token in config.unstressed_words:
                self.stress_tendency = ['U']
            # Set as stressed if its part of speech is in the stress tendency list.
            elif self.pos in config.stress_pos:
                self.stress_tendency = ['S']
            # Set as weak stressed if its part of speech is in the weak stress tendency list.
            elif self.pos in config.weak_stress_pos:
                self.stress_tendency = ['W']
            # Set as neutal if its part of speech is in the neutral stress tendency list.
            elif self.pos in config.neutral_stress_pos:
                self.stress_tendency = ['N']
            # Otherwise, set as unstressed.
            else:
                self.stress_tendency = ['U']

    # Returns None (for punctuation and whitespace), stress_override, or the stress of the first pronunciation.
    def get_stress(self):
        if self.is_punct or self.is_wspace:
            return None
        else:
            return self.stress_override or self.pronunciations[0].stress

    # Sets the token's PoS tags.
    def set_pos(self, tags):
        if len(tags) > 1:
            self.pos = tags[0]
            self.pos_secondary = tags[1:]
            self.simple_pos = config.short_pos_dict[tags[0]]
        else:
            self.pos = tags[0]
            self.simple_pos = config.short_pos_dict[tags[0]]

    # Sets the token's syntactic dependencies.
    def set_dependency(self, deps):
        self.dependency = deps

    # Sets the token's lemma.
    def set_lemma(self, lemmas):
        self.lemma = lemmas