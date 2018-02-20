import logging
from collections import OrderedDict

from poetics.conversions import tokenize, get_sound_set_groups
from poetics.logging import print_sound_set
from poetics.patterning import assign_letters_to_dict
from poetics.lookups import name_stanza


class Stanza:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.plaintext = text
        self.tokenized_text = tokenize(text)
        self.word_indexes = ()

        self.lines = []
        self.line_count = []
        self.line_lengths = None
        self.meters = None
        self.form = None

        self.line_rhymes = []
        self.rhyme_scheme = None
        self.line_asso = []
        self.asso_scheme = None
        self.line_cons = []
        self.cons_scheme = None
        self.line_i_rhymes = []
        self.i_rhyme_scheme = None

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
        for line in self.lines:
            self.line_rhymes.append(line.rhyme)
            self.line_asso.append(line.assonance)
            self.line_cons.append(line.consonance)
            self.line_i_rhymes.append(line.i_rhyme)

        # Creates ordered dicts of unique feature appearances.
        rhyme_order = OrderedDict.fromkeys(self.line_rhymes)
        asso_order = OrderedDict.fromkeys(self.line_asso)
        cons_order = OrderedDict.fromkeys(self.line_cons)
        i_rhyme_order = OrderedDict.fromkeys(self.line_i_rhymes)

        # Assigns letters to the ordered dicts.
        rhyme_order = assign_letters_to_dict(rhyme_order, True)
        asso_order = assign_letters_to_dict(asso_order, True)
        cons_order = assign_letters_to_dict(cons_order, True)
        i_rhyme_order = assign_letters_to_dict(i_rhyme_order, True)

        # Sets rhyme scheme to the appropriate sequence of letters.
        self.rhyme_scheme = ''.join([rhyme_order[rhyme] for rhyme in self.line_rhymes])
        self.asso_scheme = ''.join([asso_order[asso] for asso in self.line_asso])
        self.cons_scheme = ''.join([cons_order[cons] for cons in self.line_cons])
        self.i_rhyme_scheme = ''.join([i_rhyme_order[i_rhyme] for i_rhyme in self.line_i_rhymes])

    def get_form(self):
        # If we haven't generated scansion yet, warn the user and do so.
        if not self.parent.scans:
            logging.warning("Scansion required for form identification. Generating scansion...")
            self.parent.get_scansion()
        # If we haven't generated rhyme yet, warn the user and do so.
        if not self.line_rhymes:
            logging.warning("Rhyme required for form identification. Generating rhymes...")
            self.parent.get_rhymes()
        # If we haven't generated meter yet, warn the user and do so.
        if not self.parent.meters:
            logging.warning("Meter required for form identification. Generating meter...")
            self.parent.get_meter()

        length_list = []
        # Create a list of syllables per line.
        for line in self.lines:
            length_list.append(str(len(''.join(line.final_scansion))))
        # If they are all the same length, line_lengths is set to that one length.
        if len(set(length_list)) == 1:
            self.line_lengths = length_list[0]
            self.meters = [meter for length, (meter, repetitions, name) in self.parent.meters.items()
                           if length == int(length_list[0])][0]
        # Otherwise, a space separated list of lengths.
        else:
            self.line_lengths = ' '.join(length_list)
            meter_list = []
            for length in length_list:
                meter_list.append(self.parent.meters[int(length)][0])
            self.meters = ' '.join(meter_list)

        self.form = name_stanza(self.rhyme_scheme, self.line_lengths, self.meters, self.line_count)

    def get_sonic_features(self):
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

    def print_sonic_features(self):
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
