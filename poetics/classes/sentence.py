import logging
import re

import poetics.config as config


class Sentence:
    def __init__(self, tokens, parent=None):
        self.parent = parent
        self.tokens = tokens
        self.word_tokens = [token for token in tokens if not token.is_punct and not token.is_wspace]

    def __str__(self) -> str:
        return ''.join([token.token for token in self.tokens])

    def __repr__(self) -> str:
        return '%s (%s)' % (super().__repr__(), ' '.join([token.token for token in self.word_tokens[0:2]]))

    def get_pos(self):
        # TODO: Needs testing for abbreviations.
        text = ''.join([token.token for token in self.tokens])
        # Removes newlines and decapitalizes the first words of successive lines (spaCy tends to regard capitalized
        # words that aren't sentence initial as proper nouns).
        text = re.sub("\n\s*(\W)*(\S)", lambda m: " " + (m.group(1) or "") + m.group(2).lower(), text)
        # Create spaCy doc.
        sentence = config.spacy_model(text)

        # Creates a list of the indexes of tokens that conjunctions should be merged into. conjunction_index stores
        # these as a list of lists each of which contains [<conjunction index>, <merge target index>].
        conjunction_index = []
        for index, token_index in enumerate(sentence[1:]):
            # Catches any conjunctions that begin with an apostrophe and are preceeded by a word token that isn't
            # punctuation and that doesn't have trailing whitespace.
            if (token_index.text[0] == "'"
                and not sentence[index].whitespace_
                and not sentence[index].is_punct):
                conjunction_index.append([token_index.i, sentence[index].i])
            # Catches remaining conjunctions based on the conjunction being in conj_tails, the preceeding token being
            # either in conj_heads or conj_tails (to account for three-part conjunctions like doesn't've), and the
            # preceeding token not having trailing whitespace.
            if (token_index.lower_ in config.conj_tails
                and (sentence[index].lower_ in config.conj_heads or sentence[index].lower_ in config.conj_tails)
                and not sentence[index].whitespace_):
                conjunction_index.append([token_index.i, sentence[index].i])

        # Iterates through conjunction_index executing the merges.  This is done in reverse because with a three-part
        # conjunction, we want to merge the third part into the second part and then the second part into the base.
        # Indexes that are merged from are replaced with empty lists to maintain indexing.
        merged_index = [[token.i] for token in sentence]
        for conj_i, word_i, in reversed(conjunction_index):
            merged_index[word_i].extend(merged_index[conj_i])
            merged_index[conj_i] = []

        # Creates the final list of tokens along with the attributes that should belong to them. Iterates exclusively
        # through a list of the indexes of tokens that are words because we don't need any data from puncutation tokens.
        word_data = []
        for index, token_index in enumerate([token.i for token in sentence if not token.is_punct and not token.is_space]):
            token = []
            tag = []
            dep = []
            lemma = []
            # If the list in merged_index at the current token_index is two or more items long, then other words were
            # merged into it, so it is appended to our final list.
            if len(merged_index[token_index]) > 1:
                for word_index in merged_index[token_index]:
                        token.append(sentence[word_index].text)
                        tag.append(sentence[word_index].tag_)
                        dep.append(sentence[word_index].dep_)
                        lemma.append(sentence[word_index].lemma_)
            # If the list in merged_index at the current token_index is empty, then we merged from it, so skip it.
            elif not merged_index[token_index]:
                continue
            # In all other cases, we just use token_index to get the appropriate attributes.
            else:
                token.append(sentence[token_index].text)
                tag.append(sentence[token_index].tag_)
                dep.append(sentence[token_index].dep_)
                lemma.append(sentence[token_index].lemma_)
            # Merges posessive tags into noun tags.
            if len(tag) > 1:
                if tag[0] in ['NN', 'NNS', 'NNP', 'NNPS'] and tag[1] == 'POS':
                    tag[0] = tag[0] + '$'
                    del tag[1]
            word_data.append([''.join(token), tag, dep, lemma])
        if not len(word_data) == len(self.word_tokens):
            logging.error("Error matching tags to tokens for %s.", self.__repr__())
        else:
            for index, word in enumerate(word_data):
                self.word_tokens[index].set_pos(word[1])
                self.word_tokens[index].set_dependency(word[2])
                self.word_tokens[index].set_lemma(word[3])