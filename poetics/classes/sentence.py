import logging
import re

import poetics.config as config
from poetics.conversions import tokenize


class Sentence:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.plaintext = text
        self.tokenized_text = tokenize(text)
        self.word_indexes = ()

        self.pos = []

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
                    else:
                        # If not, check if the key is in the token (accounts for possessives and stuff).
                        match = re.match(key, token_list[index])
                        if match:
                            yield value
                            index += 1
                        match = re.match(token_list[index], key)
                        if match:
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
                    logging.error("Failure matching part of speech tags to tokens for %s:\n%s", self, self.plaintext)

        return self.pos
