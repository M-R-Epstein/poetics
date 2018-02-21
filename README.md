# poetics
## Requirements
coloredlogs==9.0 (optional)  
nltk==3.2.5  
nltk corpora: cmudict, wordnet, words  
pyenchant==2.0.0  
python-Levenshtein==0.12.0  
spacy==>2.0.0,<3.0.0  
model: en_core_web_sm  
## Info
### create_poem()
```python 
create_poem(file, title=None, author=None, directory=poem_directory) 
```
Makes a poem object. File should be a text file with a poem in it.  Default directory is /poems.

**Poem Methods:**  
```python
 get_rhymes()
``` 
>Gets poem and stanza end rhyme scheme(s), head rhyme scheme(s), end assonance scheme(s), and end consonance scheme(s). 

```python
 get_sonic_features()
``` 
>Gets stanza internal alliteration (word initial), stressed alliteration (stressed syllable initial), assonance, consonance, and bracket consonance.

```python
get_pos()
```
>Gets part of speech tags. 

```python
get_scansion()  
```
>Calculates scansion.

```python
get_meter_v_scansion()  
```
>Gets a comparison between the calculated scansion and the apparent meter(s).

```python
get_meter()
```  
> Identifies the apparent meters.

```python
get_form()
```
>Attempts to identify poetic and stanzaic forms.

```python
record(outputfile='output.csv')
```
>Appends poem attributes to a csv file. Accepts a csv file as an argument, defaults to output.csv.

### process_poems()
```python
process_poems(directory=poem_directory)
```
Batch processes a directory full of poems. Default directory is /poems.

## Usage
```python
import poetics

# Single Poem operations.
poem = poetics.create_poem('William Blake/Songs of Innocence/the chimney sweeper-william blake.txt')
poem.get_rhymes()
poem.get_sonic_features()
poem.get_pos()
poem.get_scansion()
poem.get_meter_v_scan()
poem.get_meter()
poem.get_form()

# Batch operations.
poetics.process_poems()
```