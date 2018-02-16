# poetics
## Requirements
coloredlogs==8.0 (optional)  
nltk==3.2.5  
nltk corpora: cmudict, wordnet, words  
nltk models: averaged_perceptron_tagger  
pyenchant==2.0.0  
python-Levenshtein==0.12.0  
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
>Detects rhymes and rhyming scheme, and attempts to identify rhyming scheme.

```python
get_scansion()  
```
>Calculates a best-guess at the poem's scansion.

```python
get_meter()
```  
> Attempts to identify meter.

```python
get_pos()
```
>Tags parts of speech.  

```python
get_synsets()
```
>Gets wordnet synsets for words.  

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
poem = poetics.poetics.create_poem('when my light is spent-john milton.txt')
poem.get_rhymes()
poem.get_pos()
poem.get_scansion()
poem.get_meter()
poem.record()

# Batch operations.
poetics.process_poems()
```