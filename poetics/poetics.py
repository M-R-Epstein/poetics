import logging
import os
import re

from poetics import config as config
from poetics.classes.poem import Poem


def create_poem(filename, title=None, author=None, directory=config.poem_directory):
    with open(directory + '/' + filename, encoding="utf-8") as data:
        read_data = data.readlines()

    if not title:
        # If the file is in a directory name the poem the entire name of the text file (minus .txt).
        if '/' in filename or '\\' in filename:
            title = re.search(r"(?<=[\\/])[^\\/]+(?=\.txt)", filename).group(0)
            if not title:
                title = "Unknown poem"
                logging.warning("Title for \"%s\" set as \"Unknown poem\". Title detection failed.", filename)
        # Otherwise, assume that the file is named <title>-<author>.txt.
        else:
            title = re.search(".+(?=-)", filename).group(0)
            if not title:
                title = "Unknown poem"
                logging.warning("Title for \"%s\" set as \"Unknown poem\". Please format filenames as "
                                "\"title-author.txt\" for title detection for poems inside of the root poems directory,"
                                " or provide a title as an argument to create_poem()." , filename)

    if not author:
        # If the file is in a directory, use the name of the highest level subdirectory of the poems directory as the
        # author name.
        if '/' in filename or '\\' in filename:
            author = re.search(r"[^\\/]+", filename).group(0)
            if not author:
                author = "Unknown Poet"
                logging.warning("Author for \"%s\" set as \"Unknown poet\". Author detection failed.", filename)
        # Otherwise, assume that the file is named <title>-<author>.txt.
        else:
            author = re.search("(?<=-).+(?=\.txt)", filename).group(0)
            if not author:
                author = "Unknown Poet"
                logging.warning("Author for \"%s\" set as \"Unknown poet\". Please format filenames as "
                                "\"title-author.txt\" for author name detection for poems inside of the root poems "
                                "directory, or provide the author's name. as an argument to create_poem().", filename)

    return Poem(read_data, title, author)


def process_poems(directory=config.poem_directory, outputfile=config.output_file):
    # Does the provided directory exist?
    if not os.path.isdir(directory):
        logging.warning("\"%s\" is not a valid directory.", directory)
        return None
    # Does the provided directory have any files in it?
    if not os.listdir(directory):
        logging.warning("Directory \"%s\" contains no files.", directory)
        return None

    for dirpath, dirnames, filenames in os.walk(directory):
        relative_path = os.path.relpath(dirpath, directory)
        for filename in filenames:
            # Handles root directory
            if relative_path == ".":
                file = filename
            else:
                file = os.path.join(relative_path, filename)
            poem = create_poem(file)
            poem.get_rhymes()
            poem.get_sonic_features()
            poem.get_pos()
            poem.get_scansion()
            poem.get_meter()
            poem.get_form()
            poem.record(outputfile)
