import logging

poem_directory = 'poems'

rhyme_patterns = {'AAA': 'Tercet', 'ABA': 'Tercet', 'AAAA': 'Tanaga', 'AABA': 'Rubaiyat', 'AABB': 'Clerihew',
                  'ABBA': 'Enclosed', 'ABCB': 'Simple 4-Line', 'AABBA': 'Limerick', 'ABABB': 'Cinquain',
                  'AAABAB': 'Scottish Stanza', 'AABAAB': 'Caudate Stanza', 'AABCCB': 'Boy Named Sue',
                  'AABCCD': 'Boy Named Sue', 'ABCBBB': 'The Raven Stanza', 'ABAABBA': 'Rondelet',
                  'ABABBCC': 'Rhyme Royal', 'ABABCBC': 'Canopus', 'AAABCCCB': 'Ochtfochlach',
                  'ABAAABAB': 'Rondeau or Triolet', 'ABABABCC': 'Ottava Rima', 'ABBACCAB': 'Coraline',
                  'ABACADABA': 'Magic 9', 'ABABCDECDE': 'Keatsian Ode', 'ABBABAABBA': 'Chaucerian Roundel',
                  'ABBAABBAABBAA': 'Ballata, Balete, Or Dansa', 'ABCABCDEFDEFD': 'Raconteur',
                  'ABABBCBCCDCDEE': 'Spenserian Sonnet', 'ABABCDCDEFEFGG': 'Sonnet',
                  'ABBAABBACDCDCD': 'Petrarchan Sonnet', 'ABBAABBACDECDE': 'Petrarchan Sonnet',
                  'AAABBCCCBBDDDBB': 'Triple Rebel Round', 'AABBBCCBBBDDBBB': 'Triple Rebel Round',
                  'AABABBCBCCDCDDDD': 'Stopping By Woods On A Snowy Evening Form', 'ABABCCCCDDEEFFFF': 'Flung',
                  'ABABCCDDEDEDDEDE': 'Chant Royal', 'ABCABCDEFDEFGHIGG': 'Melodic',
                  'ABABCCDDEDECCDDEDE': 'Chant Royal', 'BCBACDEFABCBACDEFGG': 'Individualtean',
                  'ABCCABADEFFEDGGHHIII': 'Fantasy', 'ABABBCCDCDABABBCCDCDABABBCCDCDCCDCD': 'Ballade Supreme',
                  'ABCDEFFAEBDCCFDABEECBFADDEACFBBDFECADEF': 'Sestina'}

metrical_feet_2 = {'00': 'pyrrhic', '01': 'iamb', '10': 'trochee', '11': 'spondee'}
metrical_feet_3 = {'000': 'tribrach', '001': 'anapest', '010': 'amphibrach', '011': 'bacchius', '100': 'dactyl',
                   '101': 'cretic', '110': 'antibacchius', '111': 'molossus'}
metrical_feet_4 = {'0000': 'tetrabrach', '1000': 'primus paeon', '0100': 'secundus paeon', '0010': 'tertius paeon',
                   '0001': 'quartus paeon', '1100': 'double trochee', '0011': 'double iamb', '1010': 'ditrochee',
                   '0101': 'diiamb', '1001': 'choriamb', '0110': 'antispast', '0111': 'first epitrite',
                   '1011': 'second epitrite', '1101': 'third epitrite', '1110': 'fourth epitrite',
                   '1111': 'dispondee'}
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
meter_names = ['monometer', 'dimeter', 'trimeter', 'tetrameter', 'pentameter', 'hexameter', 'heptameter',
               'octameter', 'nonameter', 'decameter', 'undecameter', 'dodecameter', 'tridecameter', 'tetradecameter',
               'pentadecameter', 'hexadecameter', 'heptadecameter', 'octadecameter', 'nonadecameter', 'icosameter']


# Writes a wordlist from CMUdict to text/wordlist.txt
def write_cmu_wordlist():
    import nltk
    cmudict = nltk.corpus.cmudict

    wordlist = cmudict.words()

    with open('text/wordlist.txt', 'w') as file:
        for index, items in enumerate(wordlist):
            wordlist[index] = wordlist[index] + "\n"
        file.writelines(wordlist)


# Pulls out the words from frequencylist that are present in CMUDict and writes a sorted list to text/wordlistfreq.txt
def write_cmu_wordlist_frequencies():
    import nltk
    import csv

    cmudict = nltk.corpus.cmudict
    wordlist = cmudict.words()

    frequency_source = {}
    frequency_list = {}
    output = []

    with open('text/frequencylist.txt') as data:
        as_csv = csv.reader(data, delimiter='\t')
        for row in as_csv:
            frequency_source[row[0]] = row[1]

    for word in wordlist:
        if word in frequency_source:
            frequency_list[word] = int(frequency_source[word])

    # Create a sorted version of our dictionary
    sort = [(k, frequency_list[k]) for k in sorted(frequency_list, key=frequency_list.get, reverse=True)]

    # Prepare output lines
    for item in sort:
        output.append(item[0] + "\t" + str(item[1]) + "\n")

    with open('text/wordlistfreq.txt', 'w') as file:
        file.writelines(output)


# Logs a scansion in a readable form
def print_scansion(scansion, prefix=''):
    if prefix:
        prefix = prefix + ' '
    # Business with index_mod is to handle line numbers while account for blanks
    index_mod = 1
    logging.info("%sScansion:", prefix)
    for index, scan in enumerate(scansion):
        scansion[index] = scansion[index].replace("3", "?")
        if scan == '':
            logging.info('')
            index_mod -= 1
        else:
            logging.info("%s (%s)", scansion[index], index + index_mod)


# Checks how well a calculated most common stress pattern for the lines of a poem matches standard metres
def check_metres(predicted):
    from Levenshtein import distance, ratio
    foot_patterns = []
    plausible_meters = []

    # If the length of our scan is divisble by 2, add patterns for repeated 2 syllable feet
    if len(predicted) % 2 == 0:
        for foot in metrical_feet_2:
            meter = foot * (len(predicted) // 2)
            foot_patterns.append(meter)
    # If the length of our scan is divisible by 3, add patterns for repeated 3 syllable feet
    if len(predicted) % 3 == 0:
        for foot in metrical_feet_3:
            meter = foot * (len(predicted) // 3)
            foot_patterns.append(meter)
    # If the length of our scan is divisible by 4, add patterns for repeated 4 syllable feet
    if len(predicted) % 4 == 0:
        for foot in metrical_feet_4:
            meter = foot * (len(predicted) // 4)
            foot_patterns.append(meter)

    # See if Levenshtein ratio suggests that any of our patterns are a good match
    # Note: Not sure what minimum value is ideal for a meter to be considered a good match.
    for pattern in foot_patterns:
        if ratio(pattern, predicted) >= 0.9:
            plausible_meters.append(pattern)
    # If we only ended up with one plausible pattern, return it
    if len(plausible_meters) == 1:
        return plausible_meters[0]
    # If we get multiple plausible patterns, use Levenshtein distance to find the best match
    elif len(plausible_meters) > 1:
        distances = {}
        for index, pattern in enumerate(plausible_meters):
            distances[pattern] = distance(plausible_meters[index], predicted)
        return min(distances, key=distances.get)
    else:
        return ''


def name_meter(pattern):
    foot = None
    foot_name = None
    repetitions = None
    # Try to match a 2 syllable foot
    if len(pattern) % 2 == 0:
        split = [pattern[i:i + 2] for i in range(0, len(pattern), 2)]
        if len(set(split)) == 1:
            foot = split[0]
            foot_name = metrical_feet_2[foot]
            repetitions = len(pattern) // 2
    # Try to match a 3 syllable foot if no 2 syllable feet matched
    if not foot:
        if len(pattern) % 3 == 0:
            split = [pattern[i:i + 3] for i in range(0, len(pattern), 3)]
            if len(set(split)) == 1:
                foot = split[0]
                foot_name = metrical_feet_3[foot]
                repetitions = len(pattern) // 3
    # Try to match a 4 syllable foot if no 2 or 3 syllable feet matched
    if not foot:
        if len(pattern) % 4 == 0:
            split = [pattern[i:i + 4] for i in range(0, len(pattern), 4)]
            if len(set(split)) == 1:
                foot = split[0]
                foot_name = metrical_feet_4[foot]
                repetitions = len(pattern) // 4
    # Get a name
    if foot_name:
        if repetitions < 20:
            foot_adj = metrical_foot_adj[foot_name]
            meter = meter_names[repetitions - 1]
            return foot_adj + ' ' + meter
        else:
            return 'unknown'
    else:
        return 'unknown'


def name_rhyme(rhyme):
    if rhyme in rhyme_patterns:
        return rhyme_patterns[rhyme]
    else:
        return ''


def create_poem(filename, title=None, author=None, directory=poem_directory):
    import re
    from classes.poem import Poem

    with open(directory + '/' + filename) as data:
        read_data = data.readlines()

    if not title:
        title_search = re.search(".+(?=-)", filename)
        if title_search:
            title = title_search.group(0)
        else:
            title = "Unknown Poem"
            logging.warning("Title for \"%s\" set as \"Unknown Poem\". Please format filenames as "
                            "\"title-author.txt\" for title detection or provide a title.", filename)

    if not author:
        author_search = re.search("(?<=-).+(?=\.)", filename)
        if author_search:
            author = author_search.group(0)
        else:
            author = "Unknown Poet"
            logging.warning("Author for \"%s\" set as \"Unknown Poet\". Please format filenames as "
                            "\"title-author.txt\" for author name detection or provide the author's name.", filename)

    return Poem(read_data, title, author)


def process_poems(directory=poem_directory):
    import os
    import re
    from classes.poem import Poem

    # Does the provided directory exist?
    if not os.path.isdir(directory):
        logging.warning("\"%s\" is not a valid directory.", directory)
        return None
    # Does the provided directory have any files in it?
    if not os.listdir(directory):
        logging.warning("Directory \"%s\" contains no files.", directory)
        return None

    for root, dirs, files in os.walk(directory):
        for file in files:
            # Get poem name from file name
            name_search = re.search(".+(?=-)", file)
            if name_search:
                name = name_search.group(0)
            else:
                logging.warning("File \"%s\" skipped because its filename is invalid. Please format filenames as "
                                "\"title-author.txt\".", file)
                continue
            # Get author name from file name
            author_search = re.search("(?<=-).+(?=\.)", file)
            if author_search:
                author = author_search.group(0)
            else:
                logging.warning("File \"%s\" skipped because its filename is invalid. Please format filenames as "
                                "\"title-author.txt\".", file)
                continue
            # Read in data
            with open(directory + "/" + file) as data:
                read_data = data.readlines()

            # Create poem, do stuff, record
            poem = Poem(read_data, name, author)
            poem.get_rhyming_scheme()
            poem.get_scansion()
            poem.get_meter()
            poem.get_pos()
            poem.record()
