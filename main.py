import coloredlogs
import sys
from utilities import create_poem, process_poems

coloredlogs.install(level='INFO', fmt='%(asctime)s: %(message)s', datefmt='%H:%M:%S', stream=sys.stdout)

# Process all poems in the /poems folder. Optional argument to specify a directory, defaults to /poems otherwise.
#process_poems()


# Single Poem operations.
# Optional arguments for create_poem() are title, author, and directory
poem = create_poem('when my light is spent-john milton.txt')
poem.get_rhyming_scheme()
# poem.get_scansion()
# poem.get_direct_scansion()
# poem.get_meter()
# poem.get_pos()
# poem.record()



# ipa_dict = {'AA': 'ɑ', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔ', 'AW': 'aʊ', 'AX': 'ə', 'AXR': 'ɚ', 'AY': 'aɪ', 'EH': 'ɛ',
#             'ER': 'ɝ', 'EY': 'eɪ', 'IH': 'ɪ', 'IX': 'ɨ', 'IY': 'i', 'OW': 'oʊ', 'OY': 'ɔɪ', 'UH': 'ʊ', 'UW': 'u',
#             'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð', 'DX': 'ɾ', 'EL': 'l̩', 'EM': 'm̩', 'EN': 'n̩', 'F': 'f',
#             'G': 'ɡ', 'HH': 'h', 'H': 'h', 'JH': 'dʒ', 'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'NX': 'ɾ̃',
#             'P': 'p', 'Q': 'ʔ', 'R': 'ɹ', 'S': 's', 'SH': 'ʃ', 'T': 't', 'TH': 'θ', 'V': 'v', 'W': 'w', 'WH': 'ʍ',
#             'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'}
#
# stanza_names = ['monostitch', 'couplet', 'tercet', 'quatrain', 'cinquain', 'sestet', 'septet', 'octave']
#
# pos_shortnames = {'CC': 'coordinating conjunction', 'CD': 'cardinal digit', 'DT': 'determiner',
#                   'EX': 'existential there', 'FW': 'foreign word', 'IN': 'preposition/subordinating conjunction',
#                   'JJ': 'adjective', 'JJR': 'comparitive adjective', 'JJS': 'superlative adjective',
#                   'LS': 'list marker', 'MD': 'modal could, will', 'NN': 'singular noun', 'NNS': 'plural noun',
#                   'NNP': 'singular proper noun', 'NNPS': 'plural proper noun', 'PDT': 'predeterminer',
#                   'POS': 'posessive ending', 'PRP': 'personal pronoun', 'PRP$': 'posessive pronoun',
#                   'RB': 'adverb', 'RBR': 'comparitive adverb', 'RBS': 'superlative adverb', 'RP': 'particle',
#                   'TO': 'to go', 'UH': 'interjection', 'VB': 'verb', 'VBD': 'past tense verb',
#                   'VBG': 'gerund/present participle', 'VBN': 'past participle',
#                   'VBP': 'present, non third person verb', 'VBZ': 'present third person verb',
#                   'WDT': 'wh-determiner', 'WP': 'wh-pronoun', 'WP$': 'posessive wh-pronoun', 'WRB': 'wh-adverb'}

