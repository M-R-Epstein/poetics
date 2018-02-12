import logging

import poetics.config as config
from poetics.conversions import tokenize


class Sentence:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.plaintext = text
        self.tokenized_text = tokenize(text)
        self.word_indexes = ()

        self.pos = []

        self.word_init_consonants = []
        self.alliteration = []

        self.stressed_vowels = []
        self.assonance = []

        self.stress_init_consonants = []
        self.stressed_alliteration = []

        self.stress_final_consonants = []
        self.consonance = []

        self.stress_bracket_consonants = []
        self.bracket_consonance = []

    def get_pos(self):
        # Attempts to match pos tags to word tokens.
        def match_pos_to_tokens(token_list, tag_list):
            index = 0
            cap = len(token_list)
            # If we don't find a match for one of the keys in tag_list, then we try to match the next key to the token.
            for index2, (key, value) in enumerate(tag_list):
                if index < cap:
                    # If the key matches the token, we're good.
                    if key == token_list[index]:
                        yield value
                        index += 1
                    # If the next tag in the list is tagged posessive.
                    elif tag_list[index2 + 1][1] == 'POS':
                        # Then check if the key matches the beginning of the token.
                        if key == token_list[index][:len(key)]:
                            yield value
                            index += 1

        if not self.pos:
            if self.plaintext:
                sentence = config.spacy_model(self.plaintext)
                tuple_pos_list = [(token.text, token.tag_) for token in sentence if not token.is_punct]
                pos_list = [tag for tag in match_pos_to_tokens(self.tokenized_text, tuple_pos_list)]
                if len(pos_list) == len(self.tokenized_text):
                    self.pos = pos_list
                else:
                    logging.error("Failure matching part of speech tags to tokens for %s.", self)

        return self.pos
