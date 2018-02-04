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
Makes a poem object. File should be a text file with a poem in it.  

**Poem Methods:**  
```python
 get_rhyming_scheme()
``` 
>Detects rhymes and rhyming scheme, and attempts to identify rhyming scheme. Returns rhyming scheme.  

```python
get_scansion()  
```
Calculates a best-guess at the poem's scansion. Returns scansion.  

```python
get_direct_scansion()
```
>Provides scansion directly from cmudict pronunciations. Returns scansion.  

```python
get_meter()
```  
> Attempts to identify meter. Returns name of meter.  

```python
get_pos()
```
>Tags parts of speech.  

```python
get_synsets()
```
>Gets wordnet synsets for words.  

```python
record()
```
>Appends poem attributes to output.csv.  

### process_poems()
```python
process_poems(directory=poem_directory)
```
Batch processes a directory full of poems.

## Usage
```python
import coloredlogs
import sys
from utilities import create_poem, process_poems

coloredlogs.install(level='INFO', fmt='%(asctime)s: %(message)s', datefmt='%H:%M:%S', stream=sys.stdout)

# Single Poem operations.
poem = create_poem('when my light is spent-john milton.txt')
poem.get_rhyming_scheme()
poem.get_scansion()
poem.get_direct_scansion()
poem.get_meter()
poem.get_pos()
poem.record()

# Batch operations.
process_poems()
```