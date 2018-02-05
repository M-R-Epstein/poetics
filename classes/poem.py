import logging
from classes.word import Word
from classes.line import Line
from classes.sentence import Sentence
from collections import Counter
from collections import OrderedDict
import re
from nltk import tokenize

simple_pos = {'CC': 'CC', 'CD': 'DG', 'DT': 'DT', 'EX': 'V', 'FW': 'FW', 'IN': 'P', 'JJ': 'AJ', 'JJR': 'AJ',
              'JJS': 'AJ', 'LS': 'LST', 'MD': 'V', 'NN': 'N', 'NNS': 'N', 'NNP': 'N', 'NNPS': 'N', 'PDT': 'DT',
              'POS': 'PN', 'PRP': 'PN', 'PRP$': 'PN', 'RB': 'AV', 'RBR': 'AV', 'RBS': 'AV', 'RP': 'PRT', 'TO': 'V',
              'UH': 'INT', 'VB': 'V', 'VBD': 'V', 'VBG': 'V', 'VBN': 'V', 'VBP': 'V', 'VBZ': 'V', 'WDT': 'DT',
              'WP': 'PN', 'WP$': 'PN', 'WRB': 'AV'}


class Poem:
    def __init__(self, text, title='Unknown Poem', author='Unknown'):

        self.title = title
        self.author = author
        self.lines = []
        self.line_indexes = []
        self.sentences = []

        self.words = {}
        self.wordlist = []
        self.unrecognized_words = []
        self.provided_pronunciations = {}
        self.rhyme_scheme = ''
        self.direct_scansion = []
        self.joined_direct_scansion = []
        self.joined_scansion = []
        self.predicted_scan = ''
        self.matched_scan = ''
        self.best_scansion = []
        self.meter = None

        self.pos_count = Counter()
        self.simple_pos_count = Counter()

        # Note: Will probably need some concept of stanzas at some point
        # Loop through lines of the text checking to see if any of them have a pronunciation provided
        for index, line in enumerate(text):
            found_pronunciations = re.findall("[\w\']+{[A-Z0-9\s-]+}", line)
            for pronunciation in found_pronunciations:
                split = pronunciation.split("{")
                pronunciation = [split[1].replace('}', '')]
                self.provided_pronunciations[split[0]] = pronunciation
            if found_pronunciations:
                text[index] = re.sub("{[A-Z0-9\s]+}", "", text[index])

        # Creates sentence objects for each sentence.
        joined_text = re.sub('\n', '', ' '.join(text))
        sentences = tokenize.sent_tokenize(joined_text)
        for sentence in sentences:
            self.sentences.append(Sentence(sentence, self))

        # Creates Line objects for each line
        for line in text:
            self.lines.append(Line(line, self))

        # Create word indexes for assigning calculations on the sentence level to calculations on the line level
        wordcount_lines = 0
        for line in self.lines:
            min_index = wordcount_lines + 1
            wordcount_lines += len(line.tokenized_text)
            line.word_indexes = (min_index, wordcount_lines)
            self.line_indexes.append(line.word_indexes)

        # Create the same indexes for sentences
        wordcount_sentences = 0
        for sentence in self.sentences:
            min_index = wordcount_sentences + 1
            wordcount_sentences += len(sentence.tokenized_text)
            sentence.word_indexes = (min_index, wordcount_sentences)

        # List comprehension to pull out words from lines. Turns the list into a set and then back to remove duplicates.
        self.wordlist = list(set([
            self.lines[index].tokenized_text[index2] for index, line in enumerate(self.lines)
            if self.lines[index].tokenized_text
            for index2, word in enumerate(self.lines[index].tokenized_text)]))

        # Creates a dictionary of words for which the value corresponding to each word string (key) is the object
        # representing that word with the poem as parent. Assigns pronunciation if one was provided.
        for word in self.wordlist:
            if word in self.provided_pronunciations:
                self.words[word] = Word(word, self.provided_pronunciations[word], self)
            else:
                self.words[word] = Word(word, parent=self)

        # Iterates through the words to add any unrecognized words to unrecognized_words
        for word in self.words:
            if not self.words[word].pronunciations:
                self.unrecognized_words.append(word)
        # Logs unrecognized words if any were found
        if len(self.unrecognized_words) > 0:
            logging.warning("Unrecognized words: %s", ", ".join(self.unrecognized_words))

    def get_rhymes(self):
        from utilities import name_rhyme
        # If we don't have a rhyming scheme, figure one out
        if not self.rhyme_scheme:
            # Get the rhyme candidates for each line
            for line in self.lines:
                line.get_rhymes()

            # Loop through lines with only one rhyme candidate, set them as that line's rhyme, and increment a counter
            rhyme_counts = Counter()
            for line in self.lines:
                if len(line.rhyme_candidates) == 1:
                    rhyme_counts[line.rhyme_candidates[0]] += 1
                    line.rhyme = line.rhyme_candidates[0]

            # ToDo: Handle multiple lines that only rhyme with eachother but each have multiple pronunciations
            # Chooses the candidate rhyme that has appeared most often elsewhere for lines with multiple candidates.
            # If none of the candidate rhymes have ever appeared elsewhere, selects the first one.
            for line in self.lines:
                appearance_count = []
                if len(line.rhyme_candidates) > 1:
                    for candidate in line.rhyme_candidates:
                        appearance_count.append(rhyme_counts[candidate])
                    line.rhyme = line.rhyme_candidates[appearance_count.index(max(appearance_count))]

            # Creates an ordered dictionary that stores the appearances of rhymes in the poem in order
            rhyme_order = OrderedDict()
            for line in self.lines:
                if line.rhyme:
                    rhyme_order[line.rhyme] = None

            # Goes through the dictionary and assigns each rhyme a letter
            rhyme_keys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            for index, rhyme in enumerate(rhyme_order):
                if index < 52:
                    rhyme_order[rhyme] = rhyme_keys[index]
                # If we somehow have more than 52 rhymes, starts using pairs of letters and so on
                else:
                    rhyme_order[rhyme] = rhyme_keys[index % 52] * ((index // 52) + 1)

            # Loop through our lines adding the appropriate key to our rhyme scheme. Add a space for rhymeless lines.
            for index, line in enumerate(self.lines):
                if self.lines[index].rhyme:
                    self.rhyme_scheme += rhyme_order[self.lines[index].rhyme]
                else:
                    self.rhyme_scheme += ' '

            for sentence in self.sentences:
                sentence.get_rhymes()

            # Get the rhyming scheme name, return it
            scheme_name = name_rhyme(self.rhyme_scheme)

            logging.info("Rhyming Scheme: %s", self.rhyme_scheme)
            if scheme_name:
                logging.info("Apparent form: %s", scheme_name)
            for sentence in self.sentences:
                sentence.print_rhyme()
            return self.rhyme_scheme

        # If we do have a rhyming scheme already, return it
        else:
            scheme_name = name_rhyme(self.rhyme_scheme)
            logging.info("Rhyming Scheme: %s", self.rhyme_scheme)
            if scheme_name:
                logging.info("Apparent Form: %s", scheme_name)
            return self.rhyme_scheme

    def get_scansion(self):
        from utilities import print_scansion, check_metres

        if not self.joined_scansion:
            scan_counts = []
            # If we don't have a scansion calculated then request a scansion from each line
            for line in self.lines:
                self.direct_scansion.append(line.get_scansion())
            # Make a version of scansion where each line is a string instead of a list of word stresses
            for index, line in enumerate(self.direct_scansion):
                self.joined_scansion.append(''.join(self.direct_scansion[index]))
            self.joined_direct_scansion = self.joined_scansion
            # Create a list of lines that are not blank
            non_blank_lines = [item for item in self.joined_scansion if len(item) > 0]

            # TODO: Need to handle variance in syllables per line. Break lines into groups by length, probably.
            # Create a predicted scan after checking if all lines are the same length
            if len(max(non_blank_lines, key=len)) == len(min(non_blank_lines, key=len)):
                # Add the appropriate number of elements to track stress appearance by syllable
                for x in range(0, len(self.joined_scansion[0])):
                    scan_counts.append([int(0), int(0)])
                # Increment counts for stress appearance by syllable position
                for line in self.joined_scansion:
                    for index, stress in enumerate(line):
                        if stress == '1' or stress == '0':
                            scan_counts[index][int(stress)] += 1
                # Create a predicted scan based on most common stress/lack at position in lines
                for position in scan_counts:
                    max_value = max(position)
                    self.predicted_scan += str(position.index(max_value))

            # If we made a prediction, see if it is a close match to any known metres
            self.matched_scan = check_metres(self.predicted_scan)

            if self.predicted_scan:
                # If we found a well-matched metrical pattern, use it to resolve single syllable words
                if self.matched_scan:
                    for index, line in enumerate(self.joined_scansion):
                        line = ''
                        for index2, stress in enumerate(self.joined_scansion[index]):
                            if self.joined_scansion[index][index2] == '3':
                                line += self.matched_scan[index2]
                            else:
                                line += self.joined_scansion[index][index2]
                        self.best_scansion.append(line)
                    print_scansion(self.best_scansion)
                    return self.best_scansion
                # If we have a predicted scan but no well-matched metrical pattern, use the predicted scan
                else:
                    for index, line in enumerate(self.joined_scansion):
                        line = ''
                        for index2, stress in enumerate(self.joined_scansion[index]):
                            if self.joined_scansion[index][index2] == '3':
                                line += self.predicted_scan[index2]
                            else:
                                line += self.joined_scansion[index][index2]
                        self.best_scansion.append(line)
                    print_scansion(self.best_scansion)
                    return self.best_scansion
            else:
                print_scansion(self.joined_scansion)
                return self.joined_scansion
        # If we have already generated a scansion, return it
        else:
            if self.best_scansion:
                print_scansion(self.best_scansion)
                return self.best_scansion
            else:
                print_scansion(self.joined_scansion)
                return self.joined_scansion

    def get_meter(self):
        from utilities import name_meter
        if not self.meter:
            if self.matched_scan:
                self.meter = name_meter(self.matched_scan)
                logging.info("Apparent meter: %s", self.meter)
                return self.meter
            elif self.predicted_scan:
                self.meter = name_meter(self.predicted_scan)
                logging.info("Apparent meter: %s", self.meter)
                return self.meter
            else:
                if self.joined_scansion:
                    logging.info("Apparent meter: unknown")
                else:
                    logging.error("Scansion required to generate meter.")
                return None
        else:
            logging.info("Apparent meter: %s", self.meter)
            return self.meter

    def get_direct_scansion(self):
        from utilities import print_scansion
        if self.joined_scansion:
            print_scansion(self.joined_direct_scansion, 'Direct')
            return self.joined_direct_scansion
        else:
            self.get_scansion()
            print_scansion(self.joined_direct_scansion, 'Direct')
            return self.joined_direct_scansion

    # Gets parts of speech for sentences/lines/words
    def get_pos(self):
        from translations import convert_pos
        # Have each sentence get parts of speech
        for sentence in self.sentences:
            sentence.get_pos()

        # Create a single list of parts of speech so that we can iterate through it
        all_pos = []
        for sentence in self.sentences:
            all_pos.extend(sentence.pos)

        # Use indexes to assign parts of speech to lines
        i = 1
        for index, indexes in enumerate(self.line_indexes):
            while i <= indexes[1]:
                self.lines[index].pos.append(all_pos[i - 1])
                i += 1

        # Then feeds those parts of speech into the words which keep track of which parts of speech they appear as
        for line in self.lines:
            for index, part in enumerate(line.pos):
                self.words[line.tokenized_text[index]].pos[part] += 1
                # Also does the same thing for parts of speech relevant to wordnet
                wordnetpos = convert_pos(part)
                if wordnetpos:
                    self.words[line.tokenized_text[index]].wordnet_pos[wordnetpos] += 1
        # Save part of speech counts
        for line in self.lines:
            for pos in line.pos:
                self.pos_count[pos] += 1
        # Convert/save part of speech counts with simpler categories
        for pos in self.pos_count:
            simple_name = simple_pos[pos]
            self.simple_pos_count[simple_name] += self.pos_count.get(pos)

        logging.info("Parts of speech:")
        # This is an overcomplicated way to center the POS tag under the words for printing (by adding spaces)
        for line in self.lines:
            if line.tokenized_text and line.pos:
                simplified = []
                line_out = ''
                offset = 0
                # Create a list of human-readable POS tags
                for pos in line.pos:
                    simplified.append(simple_pos[pos])
                # Use a bunch of nonsense to center the tags under the words
                for index, word in enumerate(line.tokenized_text):
                    dif = len(line.tokenized_text[index]) - len(simplified[index])
                    offdif = dif + offset
                    if offdif > 0:
                        # Puts spaces equal to half (rounded down) the difference between tag/word length before tag
                        # Puts spaces equal to half (rounded up) the difference between tag/word length after tag
                        line_out += (' ' * (offdif // 2)) \
                                    + simplified[index] \
                                    + (' ' * (offdif // 2 + (offdif % 2 > 0))) \
                                    + ' '
                        offset = 0
                    else:
                        line_out += simplified[index] + ' '
                        # Offset is just keeping track of how far we are pushed to the right by tag length>word length
                        offset += dif
                # Output each line with the POS tags under it
                logging.info(' '.join(line.tokenized_text))
                logging.info(line_out)

    # Gets synsets for words
    def get_synsets(self):
        for word in self.words:
            self.words[word].get_synsets()

    def record(self):
        import csv
        field_headers = ['Title', 'Author', '# Lines', '# Words', 'Rhyme Scheme', 'Scansion', 'Meter', '# Noun',
                         '# Adj', '# Verb', '# Adv', '# Pron', '# Prep', '# Det']
        pos_out = ['NOUN', 'ADJ', 'VERB', 'ADV', 'PRON', 'PREP', 'DET']
        try:
            # Check to see if output already has any data in it
            with open(r'output.csv', newline='\n', encoding="utf-8") as file:
                contents = csv.reader(file)
                rows = sum(1 for _ in contents)
            # If output doesn't have any data, add a header row
            if rows == 0:
                with open(r'output.csv', 'a', newline='\n', encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(field_headers)

            output = list()
            output.append(self.title)
            output.append(self.author)
            output.append(len(self.lines))
            wordcount = 0
            for line in self.lines:
                wordcount += len(line.tokenized_text)
            output.append(wordcount)
            output.append(self.rhyme_scheme)
            output.append(self.matched_scan)
            output.append(self.meter)
            for pos in pos_out:
                output.append(self.simple_pos_count[pos])

            with open(r'output.csv', 'a', newline='\n', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(output)

            logging.info("Data for \"%s\" succesfully appended to output.csv.", self.title)

        except IOError as error:
            logging.exception("Failed to record data. %s for file %s [Error Number %s].", error.strerror,
                              error.filename, error.errno, exc_info=False)
