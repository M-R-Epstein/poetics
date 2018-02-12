from poetics.conversions import tokenize, get_sound_set_groups
from poetics.logging import print_sound_set


class Stanza:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.plaintext = text
        self.tokenized_text = tokenize(text)
        self.word_indexes = ()

        self.word_init_consonants = []
        self.alliteration = None

        self.stressed_vowels = []
        self.assonance = None

        self.stress_init_consonants = []
        self.str_alliteration = None

        self.stress_final_consonants = []
        self.consonance = None

        self.stress_bracket_consonants = []
        self.brct_consonance = None

    def get_rhymes(self):
        # Get all relevant word features for words in stanza.
        if self.tokenized_text and self.parent:
            # Retrieve lists of sounds from word objects.
            for word in self.tokenized_text:
                self.word_init_consonants.append(self.parent.words[word].word_init_consonants)
                self.stressed_vowels.append(self.parent.words[word].stressed_vowels)
                self.stress_init_consonants.append(self.parent.words[word].stress_initial_consonants)
                self.stress_final_consonants.append(self.parent.words[word].stress_final_consonants)
                self.stress_bracket_consonants.append(self.parent.words[word].stress_bracket_consonants)

        # Get feature groups for rhyme-like features
        max_distance = max(self.parent.avg_words_per_line, 5)
        self.alliteration = get_sound_set_groups(self.word_init_consonants, self.tokenized_text, max_distance)
        self.assonance = get_sound_set_groups(self.stressed_vowels, self.tokenized_text, max_distance)
        self.str_alliteration = get_sound_set_groups(self.stress_init_consonants, self.tokenized_text, max_distance)
        self.consonance = get_sound_set_groups(self.stress_final_consonants, self.tokenized_text, max_distance)
        self.brct_consonance = get_sound_set_groups(self.stress_bracket_consonants, self.tokenized_text, max_distance)

    def print_rhyme(self):
        if self.alliteration:
            print_sound_set('Alliteration', self.alliteration, self.tokenized_text)
        if self.str_alliteration:
            print_sound_set('Stressed Alliteration', self.str_alliteration, self.tokenized_text)
        if self.assonance:
            print_sound_set('Assonance', self.assonance, self.tokenized_text)
        if self.consonance:
            print_sound_set('Consonance', self.consonance, self.tokenized_text)
        if self.brct_consonance:
            print_sound_set('Bracket Consonance', self.brct_consonance, self.tokenized_text)
