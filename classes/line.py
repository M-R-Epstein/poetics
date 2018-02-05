from translations import tokenize
import re


class Line:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.plaintext = text
        self.tokenized_text = None
        self.word_indexes = ()

        self.initial_word = None
        self.final_word = None

        self.pos = []

        self.rhyme_candidates = []
        self.rhyme = None

        self.scansion = []

        # Don't bother tokenizing or finding first/last words if there aren't any letters in the plaintext
        if re.search('[a-zA-Z]', self.plaintext):
            self.tokenized_text = tokenize(text)
            self.initial_word = self.tokenized_text[0]
            self.final_word = self.tokenized_text[-1]

    def get_rhymes(self):
        if self.final_word and self.parent:
            self.rhyme_candidates = self.parent.words[self.final_word].p_rhymes
        else:
            return False

    def get_scansion(self):
        if self.tokenized_text:
            for word in self.tokenized_text:
                # If there is only one (unique) stress pattern, then use that.
                if self.parent.words[word].stresses:
                    if len(set(self.parent.words[word].stresses)) == 1:
                        self.scansion.append(self.parent.words[word].stresses[0].replace('2', '0'))
                    # ToDo: Need to decide what stress pattern to use based on the meter we are generating later
                    # ToDo: Easiest way might be to just use the first one unless we have a meter calculated
                    # ToDo: And then to recalculate scansion after all of that business
                    # ToDo: OR we could have the line store all possible scansions and then resolve them later
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

    # DEPRECATED: Gets the parts of speech for tokenized line. Now done on sentence level.
    # def get_pos(self):
    #     if self.pos:
    #         return self.pos
    #     else:
    #         if self.tokenized_text:
    #             pos_list = nltk.pos_tag(self.tokenized_text)
    #             for pos in pos_list:
    #                 self.pos.append(pos[1])
    #         else:
    #             return False
