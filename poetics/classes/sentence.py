import logging
import nltk
from poetics.translations import tokenize
from collections import Counter


class Sentence:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.plaintext = text
        self.tokenized_text = None
        self.word_indexes = ()

        self.pos = []

        self.tokenized_text = tokenize(text)

        self.word_init_consonants = []
        self.alliteration = []

        self.stressed_vowels = []
        self.stress_initial_consonants = []
        self.stress_final_consonants = []

    def get_pos(self):
        if self.pos:
            return self.pos
        else:
            if self.tokenized_text:
                pos_list = nltk.pos_tag(self.tokenized_text)
                for pos in pos_list:
                    self.pos.append(pos[1])
            else:
                return False

    def get_rhymes(self):
        if self.tokenized_text and self.parent:
            # Retrieve appropriate sounds from word objects
            for word in self.tokenized_text:
                self.word_init_consonants.append(self.parent.words[word].word_init_consonants)
                self.stressed_vowels.append(self.parent.words[word].stressed_vowels)
                self.stress_initial_consonants.append(self.parent.words[word].stress_initial_consonants)
                self.stress_final_consonants.append(self.parent.words[word].stress_final_consonants)

            # Count the appearance of word initial consonants
            sound_count = Counter()
            for sound_set in self.word_init_consonants:
                for sound in sound_set:
                    sound_count[sound] += 1
            # Loop through word initial consonants that appeared multiple times to get the indexes of the relevant words
            for key in [key for key, value in sound_count.items() if value > 1]:
                self.alliteration.append((key, [index for index, sounds in enumerate(self.word_init_consonants)
                                                for sound in sounds
                                                if key == sound]))
            return self.alliteration
        else:
            return False

    def print_rhyme(self):
        out = []
        for sound, indexes in self.alliteration:
            word_list = []
            for index in indexes:
                word_list.append(self.tokenized_text[index])
            out.append(sound + ': ' + ', '.join(word_list))

        logging.info('Sentence: %s', self.plaintext)
        if out:
            logging.info('Alliteration: %s', ' | '.join(out))
        else:
            logging.info('No instances of alliteration found')
