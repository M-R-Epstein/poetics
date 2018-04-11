from itertools import product


class Line:
    def __init__(self, tokens, num, parent=None):
        self.parent = parent
        self.tokens = tokens
        self.word_tokens = [token for token in tokens if not token.is_punct and not token.is_wspace]
        self.is_blank = False
        self.num = num

        self.initial_word = None
        self.final_word = None

        self.syllables = None
        self.syllables_base = None

        self.stress = []

        if self.word_tokens:
            self.initial_word = self.word_tokens[0]
            self.final_word = self.word_tokens[-1]
        else:
            self.is_blank = True

    def __str__(self) -> str:
        return ''.join([token.token for token in self.tokens])

    def __repr__(self) -> str:
        if self.is_blank:
            return '%s (Blank Line)' % super().__repr__()
        else:
            return '%s (%s: %s)' % (super().__repr__(), str(self.num),
                                    ' '.join([token.token for token in self.word_tokens[0:2]]))

    # Gets the syllable count for the line, or the base syllable count if the line has an uncertain count.
    def get_length(self):
        syllables = 0
        multi_length = False
        for token in self.word_tokens:
            if token.s_syllables:
                if token.pronunciations:
                    syllables += len(token.pronunciations[0].syllables)
            else:
                multi_length = True
        # If the line isn't marked as variable length, then its final syllable count is what we counted.
        if not multi_length:
            self.syllables = syllables
        # Otherwise, what we counted is the base syllable length not accounting for words that might vary.
        else:
            self.syllables_base = syllables

    # Resolves syllable counts for lines that had multiple length possibilities.
    def set_length(self, length_count):
        multi_length_tokens = []
        # Creates a list that stores tuples containing tokens with multiple possible lengths and their possible lengths.
        for token in [token for token in self.word_tokens if not token.s_syllables]:
            lengths = [len(pronunciation.stress) for pronunciation in token.pronunciations]
            if not max(lengths) == min(lengths):
                multi_length_tokens.append((token, lengths))
        # If only one token had variable lengths, then we set combinations of lengths to those lengths.
        if len(multi_length_tokens) == 1:
            combinations = [[length] for key, lengths in multi_length_tokens for length in lengths]
        # Otherwise, combinations is set to all possible combinations of the lengths of variable length syllables.
        else:
            combinations = [pros for pros in product(*[lengths for key, lengths in multi_length_tokens])]
        # Go through the ordered list of line lengths that was provided as length_count and see if any combinations
        # match a given length. Stop after the first length for which we find matches, as length_count is sorted.
        matches = []
        for length, count in length_count:
            matches = [combination for combination in combinations if sum(combination, self.syllables_base) == length]
            if matches:
                break
        # If we have no matches, use the length of the first pronunciation of each word to cull pronunciations of
        # other lengths.
        # Note: if we got no matches, then we currently use the length of the first pronunciation.
        if not matches:
            for token, lengths in multi_length_tokens:
                token.cull_pronunciations('syllables', lengths[0])
        # Otherwise, use the lengths indicated by our matching.
        # Note: currently uses the first combination if we get multiple possibile combinations.
        else:
            for index, (token, lengths) in enumerate(multi_length_tokens):
                token.cull_pronunciations('syllables', matches[0][index])

        # Set the line length.
        syllables = 0
        for token, lengths in multi_length_tokens:
            syllables += len(token.pronunciations[0].syllables)
        syllables += self.syllables_base
        self.syllables = syllables

    # Gets stress patterns for all word tokens in line.
    def get_stress(self):
        for token in self.word_tokens:
            if token.stress_tendency:
                self.stress.append(token.stress_tendency)
            else:
                self.stress.append([pronunciation.stress for pronunciation in token.pronunciations])
