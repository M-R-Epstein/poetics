import sys

import coloredlogs

import poetics

coloredlogs.install(level='INFO', fmt='%(asctime)s: %(message)s', datefmt='%H:%M:%S', stream=sys.__stdout__)

# Process all poems in the /poems folder. Optional argument to specify a directory, defaults to /poems otherwise.
poetics.process_poems()

# Single Poem operations.
# Optional arguments for create_poem() are title, author, and directory
poem = poetics.create_poem('when my light is spent-john milton.txt')
poem.get_rhymes()
poem.get_sonic_features()
poem.get_pos()
poem.get_scansion()
poem.get_meter_v_scan()
poem.get_meter()
poem.get_form()
poem.record()