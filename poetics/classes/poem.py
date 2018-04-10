import csv
import logging
import re

from poetics import config as config
from poetics.classes.line import Line
from poetics.classes.sentence import Sentence
from poetics.classes.stanza import Stanza
from poetics.classes.token import Token
from poetics.classes.word import Word
from poetics.conversions import tokenize, full_tokenize, feats_to_scheme, title_case
from poetics.logging import tags_with_text, convert_scansion, header1, header1d, header2, join_list_proper
from poetics.lookups import name_meter, name_poem
from poetics.patterning import check_meters, predict_scan, pattern_match_ratio, check_for_words, \
    maximize_token_matches, get_acrostics


class Poem:
    def __init__(self, text, title='Unknown Poem', author='Unknown'):
        self.title = title_case(title)
        self.author = title_case(author)
        self.form = None

        self.words = {}
        self.unrecognized_words = []
        self.provided_pronunciations = {}

        self.tokens = []
        self.word_tokens = []
        self.num_lines = 0
        self.lines = []
        self.avg_words_per_line = None
        self.sentences = []
        self.stanzas = []

        self.lines_by_syllable = {}
        self.scans = {}
        self.meters = {}

        # Lists of line-final and line-initial rhyme schemes.
        self.f_rhyme_schemes = {}
        self.i_rhyme_schemes = {}

        # Booleans tracking whether or not rhyme, pos, scansion, etc have already been calculated.
        self.got_rhyme = False
        self.got_pos = False
        self.got_scansion = False
        self.got_meter = False

        # Log title of poem and author
        header1d(self.title, self.author)

        # Loop through lines of the text checking to see if any of them have a pronunciation provided.
        for index, line in enumerate(text):
            found_pronunciations = re.findall("[\w\']+{[A-Z0-9\s-]+}", line)
            for pronunciation in found_pronunciations:
                split = pronunciation.split('{')
                pronunciation = split[1].replace('}', '')
                self.provided_pronunciations[split[0].lower()] = pronunciation
            if found_pronunciations:
                text[index] = re.sub("{[A-Z0-9\s-]+}", "", text[index])

            # Get rid of smart quotes, while we're at it.
            text[index] = re.sub('[‘’]', "'", text[index])
            text[index] = re.sub('[“”]', '"', text[index])

        # Gets word tokens.
        dict_tokens = [token for token in set(tokenize(''.join(text)))]
        # Creates a dictionary of words for which the value corresponding to each word string (key) is the object
        # representing that word with the poem as parent. Assigns pronunciation if one was provided in the text.
        for word in dict_tokens:
            if word in self.provided_pronunciations:
                self.words[word] = Word(word, self.provided_pronunciations[word], self)
            else:
                self.words[word] = Word(word, parent=self)

        # Break the text into tokens (including spaces and punctuation), and get token indexes for lines, sentences
        # and stanzas.
        tokens, line_indexes, sentence_indexes, stanza_indexes = full_tokenize(''.join(text))

        # Create a Token object for each token and add the tokens that are words to self.word_tokens.
        for index, token in enumerate(tokens):
            self.tokens.append(Token(token, index, self))
            self.word_tokens = [token for token in self.tokens if not token.is_punct and not token.is_wspace]

        # Create a Line object for each line.
        line_num = 1
        for start, stop in line_indexes:
            # Deals with numbering lines.
            if check_for_words(self.tokens[start:stop]):
                self.lines.append(Line(self.tokens[start:stop], line_num, self))
                line_num += 1
            else:
                self.lines.append(Line(self.tokens[start:stop], None, self))
        # Set num_lines to the number of non-blank lines.
        self.num_lines = line_num

        # Create a Sentence object for each sentence.
        for start, stop in sentence_indexes:
            self.sentences.append(Sentence(self.tokens[start:stop + 1], self))

        # Create a Stanza object for each stanza.
        for start, stop in stanza_indexes:
            # Assigns the correct lines to the correct stanzas.
            lines = [index for index, (start2, stop2) in enumerate(line_indexes) if start2 >= start and stop2 <= stop]
            self.stanzas.append(Stanza(self.tokens[start:stop], [self.lines[index] for index in lines], self))

        # Gets average words per line.
        words_per_line = []
        for line in self.lines:
            if not line.is_blank:
                words_per_line.append(len(line.word_tokens))
        self.avg_words_per_line = sum(words_per_line) // len(words_per_line)

        # Find words that failed to find pronunciations during their init, add them to unrecognized_words.
        for word in self.words:
            if not self.words[word].pronunciations:
                self.unrecognized_words.append(word)
        # Logs unrecognized words if any were found.
        if len(self.unrecognized_words) > 0:
            logging.error("Unrecognized words: %s", ", ".join(self.unrecognized_words))

    def get_rhymes(self):
        # List of features that correspond to rhyme types.
        features = ['p_rhyme', 'r_rhyme', 'str_vowel', 'str_fin_con', 'str_bkt_cons', 'str_ini_con', 'word_ini_con']

        # Have final/initial words in each line cull pronunciations based on maximizing rhyme/assonance/etc.
        final_words = [line.final_word for line in self.lines if not line.is_blank]
        init_words = [line.initial_word for line in self.lines if not line.is_blank]
        for feature in features:
            maximize_token_matches(final_words, feature)
            maximize_token_matches(init_words, feature)

        # Have stanzas get rhyme schemes.
        for stanza in self.stanzas:
            stanza.get_rhymes()

        # Creates a threshold that is used to determine if a given rhyme type should have a scheme generated. If the
        # number of unique entries (letters) in the given scheme would be higher than the threshold, then no scheme
        # is generated. The threshold is set as half the number of lines rounded up. I.e., if a poem with 15 or 16
        # non-blank lines would result in a rhyme scheme that used 9 or more unique letters, no scheme would be
        # generated.
        threshold = (self.num_lines // 2) + (self.num_lines % 2 > 0)

        # Generate schemes for each feature.
        for feature in features:
            f_scheme = feats_to_scheme([' ' if line.is_blank else getattr(line.final_word.pronunciations[0], feature)
                                        for line in self.lines], False, False, threshold)
            i_scheme = feats_to_scheme([' ' if line.is_blank else getattr(line.initial_word.pronunciations[0], feature)
                                        for line in self.lines], False, False, threshold)
            # If a scheme was returned (feats_to_scheme will return None if the number of unique entries exceeded
            # threshold), then add it to the poem's list of line-final (f_) or line-initial (i_) schemes.
            if f_scheme:
                self.f_rhyme_schemes[feature] = f_scheme
            if i_scheme:
                self.i_rhyme_schemes[feature] = i_scheme

        # Logs the generated line-final schemes.
        header1("Rhyme")
        for feature, scheme in self.f_rhyme_schemes.items():
            logging.info('%s Scheme: %s', config.rhyme_scheme_names[feature][0], scheme)
            stanza_schemes = [stanza.f_rhyme_schemes[feature] for stanza in self.stanzas
                              if stanza.f_rhyme_schemes[feature]]
            if len(stanza_schemes) > 1:
                logging.info("Stanza %s Schemes: %s", config.rhyme_scheme_names[feature][0], ', '.join(stanza_schemes))

        # Logs the generated line-initial schemes.
        for feature, scheme in self.i_rhyme_schemes.items():
            logging.info('%s Scheme: %s', config.rhyme_scheme_names[feature][1], scheme)
            stanza_schemes = [stanza.i_rhyme_schemes[feature] for stanza in self.stanzas
                              if stanza.i_rhyme_schemes[feature]]
            if len(stanza_schemes) > 1:
                logging.info("Stanza %s Schemes: %s", config.rhyme_scheme_names[feature][1], ', '.join(stanza_schemes))

        # Set a boolean for rhyme having been calculated.
        self.got_rhyme = True

    def get_sonic_features(self):
        # Has stanzas get their sonic features.
        for stanza in self.stanzas:
            stanza.get_sonic_features()
        # Have stanzas report their sonic features.
        header1("Sonic Features")
        for index, stanza in enumerate(self.stanzas):
            header2('Stanza %s (%s...)' % (index + 1, ' '.join([token.token for token in stanza.word_tokens[0:4]])))
            stanza.print_sonic_features()

    def get_rhetorical_features(self):
        return

    # Gets sight features of the poem.
    def get_sight_features(self):
        i_chars = ''.join([line.initial_word.token[0] for line in self.lines if not line.is_blank]).lower()
        f_chars = ''.join([line.final_word.token[-1] for line in self.lines if not line.is_blank]).lower()
        i_acros = get_acrostics(i_chars)
        f_acros = get_acrostics(f_chars)
        header1("Sight Features")
        if i_acros:
            header2("Initial Acrostics")
            for reading in i_acros:
                logging.info(' '.join(reading))
        if f_acros:
            header2("Final Acrosstics")
            for reading in f_acros:
                logging.info(' '.join(reading))

    # Gets parts of speech for word tokens.
    def get_pos(self):
        # Have each sentence get parts of speech
        for sentence in self.sentences:
            sentence.get_pos()
        # Log parts of speech by line.
        header1('Parts of speech')
        for line in self.lines:
            if line.is_blank:
                logging.info('')
            else:
                token_tuples = [(token.token, token.simple_pos) for token in line.tokens]
                tags_with_text(token_tuples, line.num)
        # Set a boolean for pos having been calculated.
        self.got_pos = True

    def get_scansion(self):
        # Get parts of speech if we haven't already.
        if not self.got_pos:
            logging.warning("Parts of speech required for scansion. Generating parts of speech...")
            self.get_pos()
        # Have each line get its syllable count.
        for line in self.lines:
            if not line.is_blank:
                line.get_length()
                # Sort lines by syllable count for lines that don't have multiple possible lengths.
                if not isinstance(line.syllables_base, int):
                    length = line.syllables
                    if length in self.lines_by_syllable:
                        self.lines_by_syllable[length].append(line)
                    else:
                        self.lines_by_syllable[length] = []
                        self.lines_by_syllable[length].append(line)

        # Create a list of line lengths sorted so that the more common lengths are earlier in the list.
        line_len_count = sorted([(key, len(lines)) for key, lines in self.lines_by_syllable.items()],
                                key=lambda tup: tup[1], reverse=True)
        # Have lines with multiple possible lengths resolve their length.
        for line in self.lines:
            if not line.is_blank:
                if isinstance(line.syllables_base, int):
                    line.set_length(line_len_count)
                    # Add the newly resolved multi length line to lines_by_syllable.
                    length = line.syllables
                    if length in self.lines_by_syllable:
                        self.lines_by_syllable[length].append(line)
                    else:
                        self.lines_by_syllable[length] = []
                        self.lines_by_syllable[length].append(line)
        # Have single syllable tokens set their stress tendency.
        for token in self.word_tokens:
            token.set_stress_tendency()
        # Have lines get an initial stress pattern.
        for line in self.lines:
            if not line.is_blank:
                line.get_stress()
        # Get scans for each line length.
        for key, lines in self.lines_by_syllable.items():
            scans = [line.stress for line in lines]
            predicted, predicted_single = predict_scan(key, scans)
            predicted_merged, best_match = check_meters(key, predicted, predicted_single)
            self.scans[key] = (predicted, predicted_single, predicted_merged, best_match)

        # Choose stress for single syllable words and words that have multiple stress patterns.
        for line in self.lines:
            if not line.is_blank:
                position = 0
                best = self.scans[line.syllables][3]
                pattern = self.scans[line.syllables][3]
                # If we have no best_match, we use predicted_merged.
                if not pattern:
                    pattern = self.scans[line.syllables][2]
                # Loop through word tokens in lines.
                for token in line.word_tokens:
                    # Resolves words with multiple possible stress patterns based on best_match or predicted_merged
                    # if no best_match is available.
                    if len(token.pronunciations[0].stress) > 1:
                        ratios = []
                        stresses = [pronunciation.stress for pronunciation in token.pronunciations]
                        for stress in stresses:
                            ratios.append(pattern_match_ratio(stress, pattern[position:position + len(stress)]))
                        best_index = ratios.index(max(ratios))
                        token.cull_pronunciations('stress', stresses[best_index])
                        position += len(stresses[best_index])
                    # Resolves single syllable words using best_match or stress tendency if we have no best_match.
                    else:
                        if token.stress_tendency == ['S'] or token.stress_tendency == ['W']:
                            if not best:
                                token.stress_override = '1'
                                position += 1
                            else:
                                token.stress_override = best[position]
                                position += 1
                        # Note: words with neutral tendency resolve as unstressed if we have no best_match.
                        elif token.stress_tendency == ['U'] or token.stress_tendency == ['N']:
                            if not best:
                                token.stress_override = '0'
                                position += 1
                            else:
                                token.stress_override = best[position]
                                position += 1

        # Log scansion.
        header1('Scansion')
        for line in self.lines:
            if line.is_blank:
                logging.info('')
            else:
                tokens = [token.token for token in line.tokens]
                stress = [token.get_stress() for token in line.tokens]
                tags_with_text(list(zip(tokens, convert_scansion(stress))), line.num, True)
        # Adds warnings to the log for the scansion of lines with a syllable length that had few examples
        unreliable_list = []
        for syllables, lines in self.lines_by_syllable.items():
            if len(lines) < 4:
                unreliable_list.append((syllables, len(lines)))
        if unreliable_list:
            unreliable_list.sort()
            logging.warning("The scansion for %s syllable lines may be unreliable due to limited examples (%s).",
                            join_list_proper([str(syllables) for syllables, count in unreliable_list]),
                            ', '.join([str(count) for syllables, count in unreliable_list]))
        # Set a boolean for scansion having been calculated.
        self.got_scansion = True

    def get_meter(self):
        if not self.got_scansion:
            logging.warning("Scansion required for meter. Generating scansion...")
            self.get_scansion()
        if not self.meters:
            for length, scans in self.scans.items():
                if scans[3]:
                    meter, repetitions = name_meter(scans[3])
                    name = ' '.join([item for item in [meter, repetitions] if item])
                    self.meters[length] = (meter, repetitions, name)
                else:
                    meter, repetitions = name_meter(scans[2])
                    name = ' '.join([item for item in [meter, repetitions] if item])
                    self.meters[length] = (meter, repetitions, name)
        # Get sorted lists of non-zero length meter names that were recognized/not for logging
        meters = sorted([(length, name) for length, (meter, repetitions, name) in self.meters.items() if length > 0])
        # Log 'em
        if meters:
            header2("Meter")
            logging.info("Apparent meter(s): %s",
                         ', '.join([name + ' (' + str(length) + ')' for length, name in meters]))
            # Adds warnings to the log for the meter of lines with a syllable length that had few examples
            unreliable_list = []
            for syllables, indexes in self.lines_by_syllable.items():
                if len(indexes) < 4:
                    unreliable_list.append((syllables, len(indexes)))
            if unreliable_list:
                unreliable_list.sort()
                logging.warning("The meter for %s syllable lines may be unreliable due to limited examples (%s).",
                                join_list_proper([str(syllables) for syllables, count in unreliable_list]),
                                ', '.join([str(count) for syllables, count in unreliable_list]))
        # Set a boolean for meter having been calculated.
        self.got_meter = True

    def get_meter_v_scan(self):
        if not self.got_scansion:
            logging.warning("Scansion required for comparison. Generating scansion...")
            self.get_scansion()
        header1("Scansion vs Meter")
        lines_missing_meter = False
        for line in self.lines:
            tokens = [token.token for token in line.tokens]
            meter = self.scans[line.syllables][3] if line.syllables in self.scans else None
            if not line.is_blank:
                if meter:
                    line_stress = []
                    position = 0
                    for token in line.tokens:
                        stress = token.get_stress()
                        if stress:
                            word_stress = ''
                            for pos in stress:
                                if pos == meter[position]:
                                    word_stress += pos
                                    position += 1
                                else:
                                    word_stress += '̲' + pos
                                    position += 1
                            line_stress.append(word_stress)
                        else:
                            line_stress.append(None)
                    tags_with_text(list(zip(tokens, convert_scansion(line_stress))), line.num, True)
                # Handle lines without a meter.
                else:
                    line_stress = [token.get_stress() for token in line.tokens]
                    tags_with_text(list(zip(tokens, convert_scansion(line_stress))),
                                   str(line.num) + '*', True, logging.warning)
                    lines_missing_meter = True
            else:
                logging.info('')
        if lines_missing_meter:
            logging.warning("No meter available for lines marked with *.")

    def get_form(self):
        # If we haven't generated scansion yet, warn the user and do so.
        if not self.got_scansion:
            logging.warning("Scansion required for form identification. Generating scansion...")
            self.get_scansion()
        # If we haven't generated rhyme yet, warn the user and do so.
        if not self.got_rhyme:
            logging.warning("Rhyme required for form identification. Generating rhymes...")
            self.get_rhymes()
        # If we haven't generated meter yet, warn the user and do so.
        if not self.got_meter:
            logging.warning("Meter required for form identification. Generating meter...")
            self.get_meter()

        stanza_forms_out = {}
        for index, stanza in enumerate(self.stanzas):
            stanza.get_form()
            stanza_type = join_list_proper(stanza.form, 'or')
            if stanza_type not in stanza_forms_out:
                stanza_forms_out[stanza_type] = []
            stanza_forms_out[stanza_type].append(str(index + 1))

        poem_forms_out = []
        unique_forms = list(set([tuple(stanza.form) for stanza in self.stanzas]))
        # If we only have one stanza we return the appropriate first entries in the config.poem_forms_stanzaic dict.
        if len(self.stanzas) == 1:
            stanza_forms = self.stanzas[0].form
            for form in stanza_forms:
                if form in config.poem_forms_stanzaic:
                    poem_forms_out.append(config.poem_forms_stanzaic[form][0] or form)
                else:
                    poem_forms_out.append("Unrecognized form")
        else:
            # Get possible names
            poem_forms_out.extend(name_poem(self.f_rhyme_schemes.get('p_rhyme'),
                                            [length for stanza in self.stanzas for length in stanza.line_lengths],
                                            sum([len(stanza.lines) for stanza in self.stanzas])))
            # If all of the stanzas have the same form(s), but we have multiples, return the appropriate second entries.
            if len(unique_forms) == 1:
                for form in unique_forms[0]:
                    if form in config.poem_forms_stanzaic:
                        poem_forms_out.append(config.poem_forms_stanzaic[form][1] or form)
        self.form = poem_forms_out or ["Unrecognized form"]

        poem_out = join_list_proper(self.form)
        stanza_out = [stanza + ' (' + ', '.join(lines) + ')' for stanza, lines in stanza_forms_out.items()]

        stanza_plural = ''
        if len(stanza_out) > 1:
            stanza_plural = 's'

        header2("Form")
        logging.info("Poetic Form: %s", poem_out)
        logging.info("Stanzaic Form%s: %s", stanza_plural, '; '.join(stanza_out))

    # Records poem attributes to csv.
    # TODO: should record the rest of the poem's attributes.
    def record(self, outputfile=config.output_file):
        if not self.got_rhyme:
            logging.warning("Rhyme required for recording. Generating rhyme...")
            self.get_pos()
        if not self.got_pos:
            logging.warning("Parts of speech required for recording. Generating parts of speech...")
            self.get_pos()
        if not self.got_scansion:
            logging.warning("Scansion required for recording. Generating scansion...")
            self.get_pos()
        if not self.got_meter:
            logging.warning("Meter required for recording. Generating meter...")
            self.get_pos()

        field_headers = ['Title', 'Author', '# Lines', '# Words', 'Perfect Rhyme Scheme']
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
            output.append(self.title)  # Title
            output.append(self.author)  # Author
            output.append(len(self.lines))  # Line count
            output.append(len(self.word_tokens))  # Word count
            output.append(self.f_rhyme_schemes.get('p_rhyme'))

            with open(outputfile, 'a', newline='\n', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(output)

            logging.info("Data for \"%s\" succesfully appended to %s", self.title, outputfile)

        except IOError as error:
            logging.exception("Failed to record data. %s for file %s [Error Number %s].", error.strerror,
                              error.filename, error.errno, exc_info=False)
