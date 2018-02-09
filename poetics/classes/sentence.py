import logging
import nltk
from poetics.translations import tokenize
from collections import Counter


class Sentence:
    def __init__(self, text, parent=None):
        self.parent = parent
        self.plaintext = text
        self.tokenized_text = []
        self.word_indexes = ()

        self.pos = []

        self.tokenized_text = tokenize(text)

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
        from poetics.utilities import get_distance_groups

        def index_and_count(sound_set_list, group_distance):
            out = []
            # Creates a counter that counts the number of occurances of each sound in sound_set_list.
            sound_count = Counter([s for sound_set in sound_set_list for s in sound_set])
            # Iterates through all sounds in soundcount that appeared more than one time.
            for key in [key for key, value in sound_count.items() if value > 1]:
                # Creates a list of the indexes of the occurances of the present key in sound_set_list.
                indexes = [index for index, sounds in enumerate(sound_set_list) for s in sounds
                           if key == s]
                # Uses a generator function to get a list of the largest possible groups, of minimum length 2, of
                # indexes where each consecutive index is within group_distance of the previous index .
                grouped_indexes = [num for num in get_distance_groups(indexes, 5, group_distance)]
                # Append to output.
                if grouped_indexes:
                    out.append((key, grouped_indexes))
            return out

        if self.tokenized_text and self.parent:
            # Retrieve lists of sounds from word objects.
            for word in self.tokenized_text:
                self.word_init_consonants.append(self.parent.words[word].word_init_consonants)
                self.stressed_vowels.append(self.parent.words[word].stressed_vowels)
                self.stress_init_consonants.append(self.parent.words[word].stress_initial_consonants)
                self.stress_final_consonants.append(self.parent.words[word].stress_final_consonants)
                self.stress_bracket_consonants.append(self.parent.words[word].stress_bracket_consonants)

            # Get the maximum distance used to decide if features are too far away to count as e.g. alliterating.
            # Currently using the average words per line for this distance, with a minimum distance of 5.
            max_feature_distance = max(self.parent.avg_words_per_line, 5)

            # Returns instances of matching word_init_consonants that are no more than avg_word_per_line apart.
            # Returned as a list of tuples where each tuple is (matching consonant, [word indexes]).
            self.alliteration = index_and_count(self.word_init_consonants, max_feature_distance)

            # Same for stressed vowels
            self.assonance = index_and_count(self.stressed_vowels, max_feature_distance)

            # Same for stress init consonants
            self.stressed_alliteration = index_and_count(self.stress_init_consonants, max_feature_distance)

            # Same for stress final consonants
            self.consonance = index_and_count(self.stress_final_consonants, max_feature_distance)

            # Same for stress bracket consonants
            self.bracket_consonance = index_and_count(self.stress_bracket_consonants, max_feature_distance)

        else:
            return False

    def print_rhyme(self):

        def get_printable_sound_sets(feature, tokenized_text):
            sound_sets = []
            for sound, groups in feature:
                word_sets = []
                for indexes in groups:
                    words = [tokenized_text[index] for index in indexes]
                    word_sets.append(', '.join(words))
                sound_set = '; '.join(word_sets)
                sound_sets.append(sound + ': ' + sound_set)
            return ' | '.join(sound_sets)

        allit_out = get_printable_sound_sets(self.alliteration, self.tokenized_text)
        assonance_out = get_printable_sound_sets(self.assonance, self.tokenized_text)
        stress_allit_out = get_printable_sound_sets(self.stressed_alliteration, self.tokenized_text)
        consonance_out = get_printable_sound_sets(self.consonance, self.tokenized_text)
        bracket_out = get_printable_sound_sets(self.bracket_consonance, self.tokenized_text)

        features = {'alliteration': allit_out,
                    'assonance': assonance_out,
                    'stressed alliteration': stress_allit_out,
                    'consonance': consonance_out,
                    'bracket consonance': bracket_out}

        logging.info('Sentence: %s', self.plaintext)
        not_found = []
        # Log features that were found, add the rest to not_found.
        for name, var in features.items():
            if var:
                logging.info('%s: %s', name.title(), var)
            else:
                not_found.append(name)

        # Log features that weren't found if there are any.
        if not_found:
            if len(not_found) > 2:
                not_found = ', or '.join([', '.join(not_found[:-1]), not_found[-1]])
            else:
                not_found = ''.join(' or '.join(not_found) if len(not_found) > 1 else not_found)
        logging.info('Found no instances of %s.', not_found)
