# Poetics  
- [Introduction](#introduction)
- [About](#about)
  - [Getting started](#getting-started)
  - [Requirements](#requirements)
  - [Usage](#usage)
    - [create_poem()](#create_poem)
    - [Poem methods](#poem-methods)
      - [get_rhymes()](#get_rhymes)
      - [get_sonic_features()](#get_sonic_features)
      - [get_sight_features()](#get_sight_features)
      - [get_pos()](#get_pos)
      - [get_scansion()](#get_scansion)
      - [get_meter()](#get_meter)
      - [get_meter_v_scansion()](#get_meter_v_scansion)
      - [get_form()](#get_form)
      - [record()](#record)
    - [process_poems()](#process_poems)
- [License](#license)

---

# Introduction  
Poetics does things with poems. Some kind of actual introduction goes here. 

---
# About
## [Getting started](example.py)
```python
import poetics

poem = poetics.create_poem('when my light is spent-john milton.txt')

poem.get_rhymes()
poem.get_sonic_features()
poem.get_sight_features()
poem.get_pos()
poem.get_scansion()
poem.get_meter()
poem.get_meter_v_scan()
poem.get_form()
poem.record()
```  

## [Requirements](requirements.txt)  
* **[coloredlogs](https://pypi.python.org/pypi/coloredlogs)** (optional)  
* **[nltk](https://pypi.python.org/pypi/nltk)**  
* **[pyenchant](https://pypi.python.org/pypi/pyenchant)**  
* **[python-Levenshtein](https://pypi.python.org/pypi/python-Levenshtein/)**  
* **[spaCy](https://pypi.python.org/pypi/spacy)**  

## Usage
### create_poem()
```python 
create_poem(filename, title=None, author=None, directory=config.poem_directory)
```
Makes a `Poem` object. `file` should be the name of a text file with a poem in it.  `directory` optionally specifies the directory 
that the file is in (defaults to `poem_directory` set in [config.py](/poetics/config.py)).

`create_poem` will automatically assign a title and author to the poem if the name of the text file provided is formatted as `<poem name>-<author name>.txt` (e.g. `song on may morning-john milton.txt`).
`title` and `author` can optionally be entered manually to provide a title for the poem and a name for the poem's author.


### Poem methods  
#### get_rhymes()  
```python
get_rhymes(self)
``` 
Looks for rhyme schemes for the poem (as a whole) and for stanzas individually. Rhyme types checked are rich rhyme, perfect rhyme, near rhyme, assonance, consonance, bracket consonance, stressed-syllable alliteration, and word-initial alliteration. Potential rhyme schemes are evaluated for line initial and line final words.

#### get_sonic_features()
```python
get_sonic_features(self)
``` 
Gets stanza internal sonic features.

#### get_sight_features()
```python
get_sight_features(self)
``` 
Attempts to identify sight-level features of the poem (e.g. acrostics).

#### get_pos()
```python
get_pos(self)
```
Gets part of speech tags for the poem.

#### get_scansion()  
```python
get_scansion(self)  
```
Gets a scansion for the poem.

#### get_meter()
```python
get_meter(self)
```  
Gets a best guess at the poem's meter(s).

#### get_meter_v_scansion()  
```python
get_meter_v_scansion(self)  
```
Logs a comparison between the calculated meter and calculated scansion.

#### get_form()
```python
get_form(self)
```
Attempts to identify the poetic and stanzaic form(s) of the poem.

#### record()
```python
record(self, outputfile='output.csv')
```
Appends poem attributes to a csv file. `outputfile` optionally specifies a csv file to write to.
Defaults to `output.csv`.

### process_poems()
```python
process_poems(directory=config.poem_directory, outputfile='output.csv')
```
Runs the above mentioned methods on all poems in a directory (including its sub-directories), including `record`. 
`directory` defaults to `poem_directory` set in [config.py](/poetics/config.py). Output is written to `output_file` by default, also set in [config.py](/poetics/config.py). 


---
# License
Some kind of license.