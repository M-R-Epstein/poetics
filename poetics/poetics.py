import logging

from poetics import config as config


def create_poem(filename, title=None, author=None, directory=config.poem_directory):
    import re
    from poetics.classes.poem import Poem

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


def process_poems(directory=config.poem_directory, outputfile='output.csv'):
    import os
    import re
    from poetics.classes.poem import Poem

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
            poem.get_rhymes()
            poem.get_scansion()
            poem.get_meter()
            poem.get_pos()
            poem.record(outputfile)
