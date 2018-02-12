import csv
import logging
import re
from collections import Counter
from collections import OrderedDict

from nltk import tokenize

from poetics import config as config
from poetics.classes.line import Line
from poetics.classes.sentence import Sentence
from poetics.classes.stanza import Stanza
from poetics.classes.word import Word
from poetics.conversions import convert_pos
from poetics.logging import print_scansion, tags_under_text
from poetics.lookups import name_rhyme, name_meter
from poetics.patterning import check_metres, predict_scan, resolve_rhyme, assign_letters_to_dict


class Poem:
    def __init__(self, text, title='Unknown Poem', author='Unknown'):

        self.title = title
        self.author = author

        self.stanzas = []

        self.lines = []
        self.line_indexes = []
        self.avg_words_per_line = 0

        self.sentences = []

        self.words = {}
        self.wordlist = []
        self.unrecognized_words = []
        self.provided_pronunciations = {}

        self.rhyme_scheme = None
        self.asso_scheme = None
        self.cons_scheme = None
        self.i_rhyme_scheme = None

        self.direct_scansion = []
        self.joined_direct_scansion = []
        self.joined_scansion = []
        self.sorted_scansion = {}
        self.scans = {}
        self.meters = []

        self.pos_count = Counter()
        self.simple_pos_count = Counter()

        # Note: May need some concept of stanzas at some point
        # Loop through lines of the text checking to see if any of them have a pronunciation provided.
        for index, line in enumerate(text):
            found_pronunciations = re.findall("[\w\']+{[A-Z0-9\s-]+}", line)
            for pronunciation in found_pronunciations:
                split = pronunciation.split("{")
                pronunciation = [split[1].replace('}', '')]
                self.provided_pronunciations[split[0]] = pronunciation
            if found_pronunciations:
                text[index] = re.sub("{[A-Z0-9\s-]+}", "", text[index])

        # Creates Line objects for each line.
        for line in text:
            self.lines.append(Line(line, self))
        # Create word indexes for passing information between lines/stanzas/sentences.
        wordcount = 0
        for line in self.lines:
            # Tracks minimum bound for current line.
            min_index = wordcount + 1
            # Finds upper bound of line by adding the length of the current line to the existing wordcount.
            wordcount += len(line.tokenized_text)
            line.word_indexes = (min_index, wordcount)
            self.line_indexes.append(line.word_indexes)
        # Get a list of the number of words per line, ignoring lines without any tokenized text, and then an average.
        line_lengths = [len(line.tokenized_text) for line in self.lines if line.tokenized_text]
        self.avg_words_per_line = round(sum(line_lengths) / len(line_lengths))

        # Splits full text into stanzas based on blank lines.
        stanza_text = re.split('\n\s*[\n]+', ''.join(text))
        # Creates Stanza objects for each stanza.
        for stanza in stanza_text:
            self.stanzas.append(Stanza(stanza, self))
        # Create word indexes for passing information between lines/stanzas/sentences.
        wordcount = 0
        for stanza in self.stanzas:
            min_index = wordcount + 1
            wordcount += len(stanza.tokenized_text)
            stanza.word_indexes = (min_index, wordcount)

        # Creates fully joined text w/o linebreaks.
        joined_text = re.sub('\n', '', ' '.join(text))
        # Uses NLTK tokenizer to split joined text into sentences.
        sentence_text = tokenize.sent_tokenize(joined_text)
        # Creates a Sentence object for each sentence.
        for sentence in sentence_text:
            self.sentences.append(Sentence(sentence, self))
        # Create word indexes for passing information between lines/stanzas/sentences.
        wordcount = 0
        for sentence in self.sentences:
            min_index = wordcount + 1
            wordcount += len(sentence.tokenized_text)
            sentence.word_indexes = (min_index, wordcount)

        # List comprehension to pull out words from lines. Turns the list into a set and then back to remove duplicates.
        self.wordlist = list(set([
            self.lines[index].tokenized_text[index2] for index, line in enumerate(self.lines)
            if self.lines[index].tokenized_text
            for index2, word in enumerate(self.lines[index].tokenized_text)]))
        # Creates a dictionary of words for which the value corresponding to each word string (key) is the object
        # representing that word with the poem as parent. Assigns pronunciation if one was provided in the text.
        for word in self.wordlist:
            if word in self.provided_pronunciations:
                self.words[word] = Word(word, self.provided_pronunciations[word], self)
            else:
                self.words[word] = Word(word, parent=self)

        # Find words that failed to find pronunciations during their init, add them to unrecognized_words.
        for word in self.words:
            if not self.words[word].pronunciations:
                self.unrecognized_words.append(word)
        # Logs unrecognized words if any were found.
        if len(self.unrecognized_words) > 0:
            logging.warning("Unrecognized words: %s", ", ".join(self.unrecognized_words))

    def get_rhymes(self):
        # If we don't have a rhyming scheme, figure one out
        if not self.rhyme_scheme:
            # Get the rhyme candidates for each line
            for line in self.lines:
                line.get_rhymes()

            # List of rhymes with multiple rhyme candidates.
            multi_feature_lines = [line for line in self.lines if len(line.rhyme_candidates) > 1]
            # Then figure out the best rhymes for each.
            for line in multi_feature_lines:
                line.rhyme = resolve_rhyme(line.rhyme_candidates,
                                           # Counter of the rhymes for lines that only had one candidate.
                                           Counter([line.rhyme for line in self.lines if line.rhyme]),
                                           # Counter of the appearances of rhymes in lines with multiple candidates.
                                           Counter(c for line in multi_feature_lines for c in line.rhyme_candidates))
            # Assonance.
            multi_feature_lines = [line for line in self.lines if len(line.asso_candidates) > 1]
            for line in multi_feature_lines:
                line.assonance = resolve_rhyme(line.asso_candidates,
                                               Counter([line.assonance for line in self.lines if line.assonance]),
                                               Counter(c for line in multi_feature_lines for c in line.asso_candidates))
            # Consonance
            multi_feature_lines = [line for line in self.lines if len(line.cons_candidates) > 1]
            for line in multi_feature_lines:
                line.consonance = resolve_rhyme(line.con_candidates,
                                                Counter([line.consonance for line in self.lines if line.consonance]),
                                                Counter(
                                                    c for line in multi_feature_lines for c in line.cons_candidates))
            # Head rhyme
            multi_feature_lines = [line for line in self.lines if len(line.i_rhyme_candidates) > 1]
            for line in multi_feature_lines:
                line.i_rhyme = resolve_rhyme(line.i_rhyme_candidates,
                                             Counter([line.i_rhyme for line in self.lines if line.i_rhyme]),
                                             Counter(
                                                 c for line in multi_feature_lines for c in line.i_rhyme_candidates))

            # Creates ordered dicts of unique feature appearances.
            rhyme_order = OrderedDict.fromkeys(line.rhyme for line in self.lines if line.rhyme)
            asso_order = OrderedDict.fromkeys(line.assonance for line in self.lines if line.assonance)
            cons_order = OrderedDict.fromkeys(line.consonance for line in self.lines if line.consonance)
            i_rhyme_order = OrderedDict.fromkeys(line.i_rhyme for line in self.lines if line.i_rhyme)

            # Uses half the number of lines +1 to set the max number of unique features for a feature to count as
            # having some kind of pattern. So, for example, a 16 or 15 line poem would need no more than 8 rhymes.
            max_sets = ((len(self.lines) // 2) + 1)
            if not len(rhyme_order) > max_sets:
                # Assigns letters to the ordered dicts.
                rhyme_order = assign_letters_to_dict(rhyme_order)
                # Sets rhyme scheme to the appropriate sequence of letters.
                self.rhyme_scheme = ''.join([' ' if not line.rhyme else rhyme_order[line.rhyme] for line in self.lines])
            if not len(asso_order) > max_sets:
                asso_order = assign_letters_to_dict(asso_order)
                self.asso_scheme = ''.join(
                    [' ' if not line.assonance else asso_order[line.assonance] for line in self.lines])
            if not len(cons_order) > max_sets:
                cons_order = assign_letters_to_dict(cons_order)
                self.cons_scheme = ''.join(
                    [' ' if not line.consonance else cons_order[line.consonance] for line in self.lines])
            if not len(i_rhyme_order) > max_sets:
                i_rhyme_order = assign_letters_to_dict(i_rhyme_order)
                self.i_rhyme_scheme = ''.join(
                    [' ' if not line.i_rhyme else i_rhyme_order[line.i_rhyme] for line in self.lines])
            # Has stanzas get their rhyme-like features.
            for stanza in self.stanzas:
                stanza.get_rhymes()

        # Log the rhyming scheme if we have one.
        if self.rhyme_scheme:
            scheme_name = name_rhyme(self.rhyme_scheme)
            logging.info("Rhyming Scheme: %s", self.rhyme_scheme)
            if scheme_name:
                logging.info("Apparent form: %s", scheme_name)
        # Try assonance scheme and then consonance scheme if we didn't.
        elif self.asso_scheme:
            logging.info("Assonance Scheme: %s", self.asso_scheme)
        elif self.cons_scheme:
            logging.info("Consonance Scheme: %s", self.cons_scheme)
        # Print line initial rhyme scheme if we got one.
        if self.i_rhyme_scheme:
            logging.info("Head Rhyming Scheme: %s", self.i_rhyme_scheme)

        # Have stanzas report their rhyme like features.
        for index, stanza in enumerate(self.stanzas):
            logging.info('Stanza %s:\n%s', index + 1, stanza.plaintext)
            stanza.print_rhyme()

        return self.rhyme_scheme

    def get_scansion(self):

        if not self.joined_scansion:
            # If we don't have a scansion calculated then request a scansion from each line
            for line in self.lines:
                self.direct_scansion.append(line.get_scansion())
            # Make a version of scansion where each line is a string instead of a list of word stresses
            for index, line in enumerate(self.direct_scansion):
                self.joined_scansion.append(''.join(self.direct_scansion[index]))

            # Store a direct scansion before we do anything with it
            self.joined_direct_scansion = list(self.joined_scansion)

            # Make a dictionary object that sorts lines into groups by their scan length
            for index, scan in enumerate(self.joined_scansion):
                length = len(scan)
                if length in self.sorted_scansion:
                    self.sorted_scansion[length].append((index, scan))
                else:
                    self.sorted_scansion[length] = []
                    self.sorted_scansion[length].append((index, scan))

            # Create another similar dict of scan predictions and matches by length
            for length, lines in self.sorted_scansion.items():
                scans = [line[1] for line in lines]
                predicted, merged = predict_scan(scans)
                best_match = check_metres(predicted, merged)
                self.scans[length] = (predicted, merged, best_match)

            for length, scans in self.scans.items():
                line_indexes = [entry[0] for entry in self.sorted_scansion[length]]
                # If we found a well-matched metrical pattern for a given line length, we use it for 1 syllable words
                if scans[2]:
                    for index in line_indexes:
                        final_scan = ''
                        for index2, stress in enumerate(self.joined_scansion[index]):
                            if int(stress) > 2:
                                final_scan += scans[2][index2]
                            else:
                                final_scan += self.joined_scansion[index][index2]
                        self.joined_scansion[index] = final_scan
                # If we can't get a match, then just use the direct scansion.
                else:
                    for index in line_indexes:
                        final_scan = ''
                        for index2, stress in enumerate(self.joined_direct_scansion[index]):
                            if int(stress) > 2:
                                final_scan += str(int(stress) - 3)
                            else:
                                final_scan += stress
                        self.joined_scansion[index] = final_scan

        print_scansion(self.joined_scansion)
        return self.joined_scansion

    def get_meter(self):
        if not self.meters:
            for length, scans in self.scans.items():
                if scans[2]:
                    self.meters.append((length, name_meter(scans[2])))
                else:
                    self.meters.append((length, name_meter(scans[0])))
        # Get sorted lists of non-zero length meter names that were recognized/not for logging
        meters = sorted([(length, name) for length, name in self.meters if length > 0])
        # Log 'em
        if meters:
            logging.info("Apparent meter(s): %s", ', '.join([name + ' (' + str(length) + ')'
                                                             for length, name in meters]))
        return self.meters

    def get_direct_scansion(self):

        if not self.joined_scansion:
            self.get_scansion()
        print_scansion(self.joined_direct_scansion, 'Direct')
        return self.joined_direct_scansion

    # Gets parts of speech for sentences/lines/words
    def get_pos(self):

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
            simple_name = config.short_pos_dict[pos]
            self.simple_pos_count[simple_name] += self.pos_count.get(pos)

        logging.info("Parts of speech:")
        for line in self.lines:
            if line.tokenized_text and line.pos:
                simplified = []
                # Create a list of simplied tags for each line.
                for pos in line.pos:
                    simplified.append(config.short_pos_dict[pos])
                tags_under_text(line.tokenized_text, simplified)

    # Gets synsets for words
    def get_synsets(self):
        for word in self.words:
            self.words[word].get_synsets()

    def record(self, outputfile=config.output_file):

        field_headers = ['Title', 'Author', '# Lines', '# Words', 'Rhyme Scheme', 'Scansion', 'Meter', '# Noun',
                         '# Adj', '# Verb', '# Adv', '# Pron', '# Prep', '# Det']
        pos_out = ['NOUN', 'ADJ', 'VERB', 'ADV', 'PRON', 'PREP', 'DET']
        try:
            # Check to see if output already has any data in it
            with open(outputfile, 'r', newline='\n', encoding="utf-8") as file:
                contents = csv.reader(file)
                rows = sum(1 for _ in contents)
            # If output doesn't have any data, add a header row
            if rows == 0:
                with open(outputfile, 'a', newline='\n', encoding="utf-8") as file:
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
            output.append(self.scans)
            output.append(self.meters)
            for pos in pos_out:
                output.append(self.simple_pos_count[pos])

            with open(outputfile, 'a', newline='\n', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(output)

            logging.info("Data for \"%s\" succesfully appended to %s", self.title, outputfile)

        except IOError as error:
            logging.exception("Failed to record data. %s for file %s [Error Number %s].", error.strerror,
                              error.filename, error.errno, exc_info=False)
