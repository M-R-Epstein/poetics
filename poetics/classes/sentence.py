import logging
import re

import poetics.config as config


class Sentence:
    def __init__(self, tokens, parent=None):
        self.parent = parent
        self.tokens = tokens
        self.word_tokens = [token for token in tokens if not token.is_punct and not token.is_wspace]

    def get_pos(self):
        text = ''.join([token.token for token in self.tokens]).replace('\n', ' ')
        sentence = config.spacy_model(text)
        tuple_pos_list = [(token.text, token.tag_) for token in sentence if not token.is_punct]
        # Attempts to match pos tags to word tokens.
        index = 0
        cap = len(self.word_tokens)
        # If we don't find a match for one of the keys in tag_list, then we try to match the next key to the token.
        for index2, (key, value) in enumerate(tuple_pos_list):
            if index < cap:
                # If the key matches the token, we're good.
                if key == self.word_tokens[index].token:
                    self.word_tokens[index].pos = value
                    self.word_tokens[index].simple_pos = config.short_pos_dict[value]
                    index += 1
                else:
                    # If not, check if the key is in the token (accounts for possessives and stuff).
                    match = re.match(key, self.word_tokens[index].token)
                    if match:
                        self.word_tokens[index].pos = value
                        self.word_tokens[index].simple_pos = config.short_pos_dict[value]
                        index += 1
                    match = re.match(self.word_tokens[index].token, key)
                    if match:
                        self.word_tokens[index].pos = value
                        self.word_tokens[index].simple_pos = config.short_pos_dict[value]
                        index += 1
        # If we failed to find a pos tag for any token, log that.
        no_match = [token.token for token in self.word_tokens if not token.pos]
        if no_match:
            logging.error("Failure matching part of speech tags to tokens for %s:\n%s", self, no_match)
