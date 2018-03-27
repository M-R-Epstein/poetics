import json
import os

import enchant
import spacy

directory = os.path.dirname(__file__)

########################################################################################################################
# Configuration Variables
########################################################################################################################
# Poem directory.
poem_directory = os.path.split(directory)[0] + '/poems'
# Default output file.
output_file = os.path.split(directory)[0] + 'output.csv'

# Path of the spacy model to use.
spacy_model_dir = os.path.join(directory, 'data/spacy/en_core_web_sm')

# Path of raw cmudict. From https://github.com/cmusphinx/cmudict.
cmudict_raw_path = os.path.join(directory, 'data/cmudict/cmudict.txt')
# Path of json version of cmudict.
cmudict_path = os.path.join(directory, 'data/cmudict/cmudict.json')
# Path of cmudict wordlist (used by pyEnchant).
cmudict_wordlist_path = os.path.join(directory, 'data/cmudict/wordlist.txt')
# Path of phoneticized version of cmudict.
cmudict_phonetic_path = os.path.join(directory, 'data/cmudict/phoneticized.json')

# Path of alternate spellings file.
alt_spellings_path = os.path.join(directory, 'data/alternate_spellings.json')
# Path of poem forms file.
poem_forms_path = os.path.join(directory, 'data/poem_forms.json')
# Path of sonic features file.
sonic_features_path = os.path.join(directory, 'data/sonic_features.json')
# Path of stanza forms file.
stanza_forms_path = os.path.join(directory, 'data/stanza_forms.json')


########################################################################################################################
# Dictionaries
########################################################################################################################
# Used to reformat specific part of speech tags as shorter, less specific (more readable) tags.
short_pos_dict = {
    'VB': 'V',  # base form verb
    'VBD': 'V', # past tense verb
    'VBG': 'V',  # gerund or present participle verb
    'VBN': 'V',  # past participle verb
    'VBZ': 'V',  # 3rd person singular present verb
    'VBP': 'V',  # non-3rd person singular present verb
    'MD': 'V',  # modal auxiliary verb
    'BES': 'V',  # auxiliary be
    'HVS': 'V',  # have
    'NN': 'N',  # singular or mass noun
    'NN$': 'N$',  # posessive singular or mass noun
    'NNS': 'N',  # plural noun
    'NNS$': 'N$',  # posessive plural noun
    'NNP': 'N',  # singular proper noun
    'NNP$': 'N$',  # posessive singular proper noun
    'NNPS': 'N',  # plural proper noun
    'NNPS$': 'N$',  # posessive plural proper noun
    'PRP': 'PN',  # personal pronoun
    'WP': 'PN',  # personal wh-pronoun
    'PRP$': 'PN$',  # posessive pronoun
    'WP$': 'PN$',  # posessive wh-pronoun
    'RB': 'AV',  # adverb
    'RBR': 'AV',  # comparative adverb
    'RBS': 'AV',  # superlative adverb
    'WRB': 'AV',  # wh-adverb
    'JJ': 'AJ',  # adjective
    'JJR': 'AJ',  # comparitive adjective
    'JJS': 'AJ',  # superlative adjective
    'AFX': 'AJ',  # affix
    'PDT': 'PDT',  # predeterminer
    'DT': 'DT',  # determiner
    'WDT': 'DT',  # wh-determiner
    'CC': 'CC',  # coordinating conjunction
    'IN': 'IN',  # subordinating conjunction or preposition
    'EX': 'EX',  # existential there
    'TO': 'TO',  # infinitival to
    'RP': 'RP',  # particle
    'POS': '$',  # posessive ending
    'GW': '?',  # word from multi-word expression
    'UH': 'UH',  # interjection
    'FW': 'FW',  # foreign word
    'CD': '#',  # cardinal number
    '$': 'SYM',  # currency
    '#': 'SYM',  # pound sign
    'SYM': 'SYM',  # symbol
    'ADD': 'MAIL',  # email address
    '.': '.',  # sentence terminator
    ',': '.',  # comma
    '-LRB-': '.',  # left round bracket
    '-RRB-': '.',  # right round bracket
    '``': '.',  # opening quotation mark
    '""': '.',  # closing quotation mark
    "''": '.',  # closing quotation mark
    ':': '.',  # colon or ellipsis
    'HYPH': '.',  # hyphen
    'LS': '.',  # list marker
    'NFP': '.',  # superfluous punctuation
    'SP': 'SP',  # whitespace
    '_SP': 'SP',  # whitespace
    'XX': '?',  # unknown
    'NIL': ''  # untagged
    }

# Pronunciation features to scheme names. Used for naming rhyme schemes generated from a pronunciation feature
# (i.e., str_vowel, the pronunciation's stressed vowel sound, corresponds to assonance). The value for each entry
# is the name of the scheme when line-final and then the name of the scheme when line-initial.
rhyme_scheme_names = {'p_rhyme': ('Perfect Rhyme', 'Perfect Head Rhyme'), 'r_rhyme': ('Rich Rhyme', 'Rich Head Rhyme'),
                      'str_vowel': ('Assonance', 'Head Assonance'), 'str_fin_con': ('Consonance', 'Head Consonance'),
                      'str_bkt_cons': ('Bracket Consonance', 'Head Bracket Consonance'),
                      'str_ini_con': ('Alliteration', 'Head Alliteration'),
                      'word_ini_con': ('Word Initial Alliteration', 'Head Word Initial Alliteration')}

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
stress_pos = ['VB', 'VBD', 'VBG', 'VBN', 'VBZ', 'VBP', 'MD', 'BES', 'HVS', 'NN', 'NNS', 'NNP', 'NNPS']
# Weak stress tendency parts of speech tags. Adverbs and adjectives.
weak_stress_pos = ['RB', 'RBR', 'RBS', 'WRB', 'JJ', 'JJR', 'JJS', 'AFX']
# Neutral stress tendency parts of speech tags. Pronouns.
neutral_stress_pos = ['PRP', 'PRP$', 'WP', 'WP$']
# All other parts of speech are treated as having an unstressed tendency.
# These words are treated as unstressed tendency independent of part of speech tag.
unstressed_words = ["a", "am", "an", "and", "are", "as", "but", "by", "can", "for", "if", "is", "it", "its", "it's",
                    "may", "nor", "of", "or", "so", "such", "than", "the", "them", "there", "this", "those", "though",
                    "to", "was", "were", "will", "with"]

# Word segments that can form the head of a conjunction.
conj_heads = ["i", "you", "he", "she", "it", "we", "they", "who", "what", "when", "where", "why", "how", "there",
              "that", "ca", "could", "do", "does", "did", "had", "may", "might", "must", "need", "ought", "sha",
              "should", "wo", "would", "ai", "are", "is", "was", "were", "have", "has", "dare", "y'", "y", "not",
              "can", "gon", "got", "let"]
# Word segments that can form the tail of a conjunction or the middle segment of a double-conjunction.
conj_tails = ["all", "d", "ll", "na", "not", "nt", "n't", "re", "s", "ta", "ve"]


########################################################################################################################
# Loading
########################################################################################################################
spacy_model = spacy.load(spacy_model_dir)

enchant_dictionary = enchant.request_pwl_dict(cmudict_wordlist_path)

enchant_english_dictionary = enchant.Dict("en_US")

with open(cmudict_phonetic_path) as file:
    phoneticized_dict = json.load(file)

with open(poem_forms_path) as file:
    poem_forms_file = json.load(file)
poem_forms = poem_forms_file["forms"]
poem_forms_repeating = poem_forms_file["repeating_forms"]
poem_forms_stanzaic = poem_forms_file["by_stanza"]

with open(stanza_forms_path) as file:
    stanza_forms = json.load(file)

with open(sonic_features_path) as file:
    sonic_features_file = json.load(file)
word_endings = sonic_features_file["endings"]
onomatopoetic_words = sonic_features_file["onomatopoeia"]