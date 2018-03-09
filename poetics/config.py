import json
import os

import enchant
import spacy

directory = os.path.dirname(__file__)

########################################################################################################################
# Configuration Variables
########################################################################################################################
# Poem directory.
poem_directory = '/poems'
# Default output file.
output_file = 'output.csv'
# Name of spacy model to use.
spacy_model_dir = 'data/spacy/en_core_web_sm'
# Location for json version of cmudict.
cmudict_path = 'data/cmudict.json'
# Location for syllabified version of cmudict.
syllabified_path = 'data/cmudict_syllabified.json'
# Location for phoneticized version of cmudict.
phoneticized_path = 'data/cmudict_phoneticized.json'
# Location for poem form lists.
poem_forms_path = 'data/poem_forms.json'
# Location for stanza forms list.
stanza_forms_path = 'data/stanza_forms.json'
# Path for cmudict wordlist.
cmudict_wordlist_path = 'data/wordlist.txt'

########################################################################################################################
# Dictionaries
########################################################################################################################
# Used to reformat specific part of speech tags as shorter, less specific (more readable) tags.
short_pos_dict = {'NIL': '\"', 'AFX': 'AJ', 'JJ': 'AJ', 'JJR': 'AJ', 'JJS': 'AJ', 'PDT': 'AJ', 'PRP$': 'AJ',
                  'WDT': 'AJ', 'WP$': 'AJ', 'IN': 'ADP', 'EX': 'AV', 'RB': 'AV', 'RBR': 'AV', 'RBS': 'AV', 'WRB': 'AV',
                  'CC': 'CC', 'DT': 'DT', 'UH': 'UH', 'NN': 'N', 'NNS': 'N', 'WP': 'N', 'CD': '#', 'POS': 'RT',
                  'RP': 'RT', 'TO': 'RT', 'PRP': 'PRP', 'NNP': 'PRN', 'NNPS': 'PRN', '_SP': 'SP', 'SP': 'SP', '#': 'SM',
                  'SYM': 'SM', 'MD': 'V', 'VB': 'V', 'VBD': 'V', 'VBG': 'V', 'VBN': 'V', 'VBP': 'V', 'VBZ': 'V',
                  'BES': 'V', 'HVS': 'V', 'FW': 'X', 'ADD': 'X', 'GW': 'X', 'XX': 'X', '.': '?'}
# Rhyme pattern names.
rhyme_patterns = {'AAA': 'Tercet', 'ABA': 'Tercet', 'AAAA': 'Tanaga', 'AABA': 'Rubaiyat', 'AABB': 'Clerihew',
                  'ABBA': 'Enclosed', 'ABCB': 'Simple 4-Line', 'AABBA': 'Limerick', 'ABABB': 'Cinquain',
                  'AAABAB': 'Scottish Stanza', 'AABAAB': 'Caudate Stanza', 'AABCCB': 'Boy Named Sue',
                  'AABCCD': 'Boy Named Sue', 'ABCBBB': 'The Raven Stanza', 'ABAABBA': 'Rondelet',
                  'ABABBCC': 'Rhyme Royal', 'ABABCBC': 'Canopus', 'AAABCCCB': 'Ochtfochlach',
                  'ABAAABAB': 'Rondeau or Triolet', 'ABABABCC': 'Ottava Rima', 'ABBACCAB': 'Coraline',
                  'ABACADABA': 'Magic 9', 'ABABBCBCC': 'Spenserian Stanza', 'ABABCDECDE': 'Keatsian Ode',
                  'ABBABAABBA': 'Chaucerian Roundel', 'ABBAABBAABBAA': 'Ballata, Balete, Or Dansa',
                  'ABCABCDEFDEFD': 'Raconteur', 'ABABBCBCCDCDEE': 'Spenserian Sonnet', 'ABABCDCDEFEFGG': 'Sonnet',
                  'ABBAABBACDCDCD': 'Petrarchan Sonnet', 'ABBAABBACDECDE': 'Petrarchan Sonnet',
                  'AAABBCCCBBDDDBB': 'Triple Rebel Round', 'AABBBCCBBBDDBBB': 'Triple Rebel Round',
                  'AABABBCBCCDCDDDD': 'Stopping By Woods On A Snowy Evening Form', 'ABABCCCCDDEEFFFF': 'Flung',
                  'ABABCCDDEDEDDEDE': 'Chant Royal', 'ABCABCDEFDEFGHIGG': 'Melodic',
                  'ABABCCDDEDECCDDEDE': 'Chant Royal', 'BCBACDEFABCBACDEFGG': 'Individualtean',
                  'ABCCABADEFFEDGGHHIII': 'Fantasy', 'ABABBCCDCDABABBCCDCDABABBCCDCDCCDCD': 'Ballade Supreme',
                  'ABCDEFFAEBDCCFDABEECBFADDEACFBBDFECADEF': 'Sestina'}
# Classical meters
classic_meters = {'1010011001100101': 'choriamb', '10100101010': 'hendecasyllabe', '10100101011': 'hendecasyllabe',
                  '11100101010': 'hendecasyllabe', '11100101011': 'hendecasyllabe', '01010101011': 'hendecasyllabe',
                  '01010101010': 'hendecasyllabe', '10101001010': 'sapphic', '10111001010': 'sapphic',
                  '10101001011': 'sapphic', '10111001011': 'sapphic', '10010': 'adonic', '10011': 'adonic',
                  '10010011001001': 'classical pentameter', '11010100100': 'alcaic hendecasyllabe',
                  '110101010': 'alcaic enneasyllable', '1001001010': 'alcaic decasyllable',
                  '10010010010010011': 'classical heroic'}
# Length 2 metrical foot dictionary.
metrical_feet_2 = {'00': 'pyrrhic', '01': 'iamb', '10': 'trochee', '11': 'spondee'}
# Length 3 metrical foot dictionary.
metrical_feet_3 = {'000': 'tribrach', '001': 'anapest', '010': 'amphibrach', '011': 'bacchius', '100': 'dactyl',
                   '101': 'cretic', '110': 'antibacchius', '111': 'molossus'}
# Length 4 metrical foot dictionary. Does not include feet that are simply a repeated length 2 foot.
metrical_feet_4 = {'1000': 'primus paeon', '0100': 'secundus paeon', '0010': 'tertius paeon', '0001': 'quartus paeon',
                   '1100': 'double trochee', '0011': 'double iamb', '1001': 'choriamb', '0110': 'antispast',
                   '0111': 'first epitrite', '1011': 'second epitrite', '1101': 'third epitrite',
                   '1110': 'fourth epitrite'}
# Metrical foot adjective forms.
metrical_foot_adj = {'pyrrhic': 'pyrrhic', 'iamb': 'iambic', 'trochee': 'trochaic', 'spondee': 'spondaic',
                     'tribrach': 'tribrachic', 'anapest': 'anapestic', 'amphibrach': 'amphibrachic',
                     'bacchius': 'bacchiac', 'dactyl': 'dactylic', 'cretic': 'cretic', 'antibacchius': 'antibacchiac',
                     'molossus': 'molossic', 'tetrabrach': 'tetrabrachic', 'primus paeon': 'primus paeonic',
                     'secundus paeon': 'secundus paeonic', 'tertius paeon': 'tertius paeonic',
                     'quartus paeon': 'quartus paeonic', 'double trochee': 'double trochaic',
                     'double iamb': 'double iambic', 'ditrochee': 'ditrochaic', 'diiamb': 'diiambic',
                     'choriamb': 'choriambic', 'antispast': 'antispastic', 'first epitrite': 'first epitritic',
                     'second epitrite': 'second epitritic', 'third epitrite': 'third epitritic',
                     'fourth epitrite': 'fourth epitritic', 'dispondee': 'dispondaic'}
# Meter names in order of foot count.
meter_names = ['monometer', 'dimeter', 'trimeter', 'tetrameter', 'pentameter', 'hexameter', 'heptameter',
               'octameter', 'nonameter', 'decameter', 'undecameter', 'dodecameter', 'tridecameter', 'tetradecameter',
               'pentadecameter', 'hexadecameter', 'heptadecameter', 'octadecameter', 'nonadecameter', 'icosameter',
               'henicosameter', 'docosameter', 'tricosameter', 'tetracosameter', 'pentacosameter', 'hexacosameter',
               'heptacosameter', 'octacosameter', 'nonacosameter', 'triacontameter']
# Stanza names by length.
stanza_length_names = ['single', 'couplet', 'tercet', 'quatrain', 'quintet', 'sestet', 'septet', 'octave', 'nine',
                       'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
                       'nineteen', 'twenty', 'twenty-one', 'twenty-two', 'twenty-three', 'twenty-four', 'twenty-five',
                       'twenty-six', 'twenty-seven', 'twenty-eight', 'twenty-nine', 'thirty', 'thirty-one',
                       'thirty-two', 'thirty-three', 'thirty-four', 'thirty-five', 'thirty-six', 'thirty-seven',
                       'thirty-eight', 'thirty-nine', 'forty', 'forty-one', 'forty-two', 'forty-three', 'forty-four',
                       'forty-five', 'forty-six', 'forty-seven', 'forty-eight', 'forty-nine', 'fifty', 'fifty-one',
                       'fifty-two', 'fifty-three', 'fifty-four', 'fifty-five', 'fifty-six', 'fifty-seven',
                       'fifty-eight', 'fifty-nine', 'sixty', 'sixty-one', 'sixty-two', 'sixty-three', 'sixty-four',
                       'sixty-five', 'sixty-six', 'sixty-seven', 'sixty-eight', 'sixty-nine', 'seventy', 'seventy-one',
                       'seventy-two', 'seventy-three', 'seventy-four', 'seventy-five', 'seventy-six', 'seventy-seven',
                       'seventy-eight', 'seventy-nine', 'eighty', 'eighty-one', 'eighty-two', 'eighty-three',
                       'eighty-four', 'eighty-five', 'eighty-six', 'eighty-seven', 'eighty-eight', 'eighty-nine',
                       'ninety', 'ninety-one', 'ninety-two', 'ninety-three', 'ninety-four', 'ninety-five', 'ninety-six',
                       'ninety-seven', 'ninety-eight', 'ninety-nine', 'one hundred']
# Lists for determining stress estimation of single syllable words based on part of speech tag.
# Stress tendency parts of speech tags. Verbs and nouns.
stress_pos = ['BES', 'MD', 'NN', 'NNP', 'NNPS', 'NNS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
# Weak stress tendency parts of speech tags. Adjective and adverbs.
weak_stress_pos = ['AFX', 'EX', 'HVS', 'JJ', 'JJR', 'JJS', 'PDT', 'RB', 'RBR', 'RBS', 'WRB']
# Neutral stress tendency parts of speech tags. Pronouns.
neutral_stress_pos = ['PRP', 'PRP$', 'WP', 'WP$']
# All other parts of speech are treated as having an unstressed tendency.
# These words are treated as unstressed tendency independent of part of speech tag.
unstressed_words = ["a", "am", "an", "and", "are", "as", "but", "by", "can", "for", "if", "is", "it", "its", "it's",
                    "may", "nor", "of", "or", "so", "such", "than", "the", "them", "there", "this", "those", "though",
                    "to", "was", "were", "will", "with"]

########################################################################################################################
# Loading
########################################################################################################################
spacy_model = spacy.load(os.path.join(directory, spacy_model_dir))
enchant_dictionary = enchant.request_pwl_dict(os.path.join(directory, cmudict_wordlist_path))
enchant_english_dictionary = enchant.Dict("en_US")
with open(os.path.join(directory, phoneticized_path)) as file:
    phoneticized_dict = json.load(file)
with open(os.path.join(directory, poem_forms_path)) as file:
    poem_forms_file = json.load(file)
poem_forms = poem_forms_file[0]
poem_forms_repeating = poem_forms_file[1]
poem_forms_stanzaic = poem_forms_file[2]
with open(os.path.join(directory, stanza_forms_path)) as file:
    stanza_forms = json.load(file)
poem_directory = os.path.split(directory)[0] + poem_directory
