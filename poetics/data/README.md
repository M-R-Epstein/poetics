# Data Specifications
- [alternate_forms.json](#alternate_formsjson)  
- [poem_forms.json](#poem_formsjson)  
  * [Forms](#forms)  
  * [Repeating forms](#repeating-forms)  
  * [Names by stanza](#names-by-stanza)  
- [sonic_features.json](#sonic_featuresjson)
  * [Endings](#endings)  
  * [onomatopoeias](#onomatopoeias)  
- [stanza_forms.json](#stanza_formsjson)

---
# [alternate_spellings.json](alternate_spellings.json)
A dictionary of alternate spellings for words. Used to map spellings that aren't in CMUDict to spellings that are.
```json 
"absinth":"absinthe",
"accessorise":"accessorize",
"accessorised":"accessorized"
```
Each `key: value` pair has a `key` which is _not_ in CMUDict and a `value` that _is_ in CMUDict. Based on data from 
[Varcon](http://wordlist.aspell.net/varcon/).




# [poem_forms.json](poem_forms.json)
Made up of two lists and a dictionary: poem forms, repeating poem forms, and names by stanza.

## Forms
Provides the identification features for poetic forms.
```json 
["French sonnet", ["ABBAABBACCDEDE", "ABBAABBACCDCCD", "ABBAABBACCDEED"], ["10", "12"], 14],
["Bragi", ["ABCCBACBAABC"], ["6 8 10 10 8 6 10 8 6 6 8 10"], 12]
```
### Components  
#### Form name (`str`)  
Name of the poetic form.

#### Rhyme schemes (`list[str]`)  
A list of the possible rhyme schemes (without spaces for stanza breaks).

#### Syllables (`list[str]`)  
Listing of possible syllable per line arrangements as strings, with values separated by spaces. If a single value is 
provided, this value is interpreted as applying to all lines. So `["10", "12"]`, as above, indicates that a _French 
sonnet_ either has all lines of 10 syllables or all lines of 12 syllables. For _Bragi_, the number of syllables has
been specified for each individual line.

#### Line count (`int`)  
The number of lines in the form.  

## Repeating forms
Provides the identification features for poetic forms with repeating elements.
```json 
["Carol","AA","bbbA","","","",""],
["Terza Rima","","a2ba2","a2a2","","",""],
["Brevee","","aabccb","","","2 2 4 2 2 4",""]
```
#### Form name (`str`)  
The name of the poetic form

#### Rhyme head (`str`)  
This is the initial segment, which is not repeated, of the rhyme scheme for the form. Because this segment is 
always the same, it should consist of capital letters (`AA` in _Carol_, for example).  

#### Rhyme core (`str`)  
This is the segment of the rhyme scheme that can be repeated any number of times. This segment uses 
a similar syntax to standard rhyme notation schemes: capital letters are always the same in all repetitions;
lower case letters are replaced with the next available letter in the alphabet in each repetition; and lower 
case letters which are followed by a digit copy the letter from the preceeding stanza in the position 
specified by the  digit.  

In the case of _Terza Rima_, this segment is `a2ba2`. For the first instance of the repeating segment, all 
positions marked with `a` will be replaced with the next available letter in the alphabet, and then all positions marked
with `b` and so on. This would result in `ABA`. In the next repetition, `b` would be replaced with the next available letter in the alphabet
(`C`)*, but both instances of `a2` would be replaced with the second letter from the previous repetition (`B`) which results in 
`BCB`. Additional repetitions would result in `ABA BCB CDC DED` and so on.

###### *If there are more repetitions than there are available letters, letters are repeated with a following lower-case letter (e.g., Aa Ab Ac). 

#### Rhyme tail (`str`)  
This is the final segment, which is not repeated, of the rhyme scheme for the form. This segment 
uses the same syntax as the rhyme core, with digits referencing the final repetition of the core. E.g., this segment is
`a2a2` for a _Terza Rima_, so with four repetitions of its core (`ABA BCB CDC DED`) the tail would be `EE` as the second 
position from the previous segment is `E`.

#### Syllables head (`str`)  
This is the initial segment, which is not repeated, of the syllable per line scheme for a given form.
This is recorded as a string of integers separated by spaces corresponding to the syllable counts for each line.

#### Syllables core (`str`)  
This is the segment of the syllable per line scheme for a given form that is repeated. Recorded in the same
fashion as the head. 

#### Syllables tail (`str`)  
This is the final segment, which is not repeated, of the syllable per line scheme for a given form.
Recorded in the same fashion as the head.  

## Names by stanza
A dictionary that provides the name that should be assigned to a poem which is made up exclusively of a single type of 
stanza.
```json 
"Ballade Stanza": ["Huitain", "Ballade Stanzas"],
"Heroic Sonnet": ["", "Heroic Sonnets"]
```
#### Stanza type (`str`)  
The key for each entry is the name of the stanzaic form.  

#### Single stanza poetic form (`str`)  
Indicates the name that should be assigned to a poem's form if it is entire made up of a single instance
of a kind of stanza. Can be empty (`""`), in which case the name of the stanza form will be used.

#### Multiple stanza poetic form (`str`)**   
Indicates the name that should be assigned to a poem's form if it is exclusively composed of multiple stanazas 
of the given type. Can be empty (`""`), in which case the name of the stanza form will be used.

---

# [sonic_features.json](sonic_features.json)
Made up of two lists: endings, and onomatopoeias.
## Endings
A dictionary of word endings for use in identifying near rhyme. Each entry is keyed with a simple (non-syllabified) string with space-separated phonemes
which correspond to a given word ending. The values are a string identifying that particular ending for matching purposes.
This is a dictionary rather than a list because cmudict records certain word endings inconsistently.
```json 
"AH JH": "age",
"AH JH AH Z": "ages",
"AH G AO G": "agog",
"AH G AO G Z": "agogs",
```
## Onomatopoeias
A list of words that are (or are potentially) onomatopoetic.
```json 
"beep",
"beeped",
"beeping",
"beeps",
"belch",
```
---

# [stanza_forms.json](stanza_forms.json)
A list of stanzaic forms and their attributes for identification.
```json 
["Count Up", [], ["1 2 3 4 5 6 7 8 9 10"], [], 10],
["Short Couplet", ["aa"], ["8"], ["iambic", "trochaic"], 2],
["Sapphic Stanza", [], [], ["sapphic sapphic sapphic adonic"], 4],
["Sextilla", ["aabccb", "ababcc"], ["8"], [], 16]
```
#### Components 
#### Form name (`str`)  
The name of the stanzaic form.  

#### Rhyme schemes (`list[str]`)  
A list of the possible rhyme schemes in a stanza of the form. Can be empty.

#### Syllables (`list[str]`)  
A list of the possible arrangements of syllables per line in the form. A sequence of integers
separated by spaces (as in _Count Up_) is interpreted as a sequence of syllable counts per line.
A single integer (as in _Short Couplet_) is interpreted as indicating that all lines should be of the given length.
 Can be empty.

#### Meters (`list[str]`)  
A list of the possible meters for the form. As with syllables, if a single meter is included, it is 
interpreted as applying to all lines of the stanza. If multiple meters are included, separated by spaces,
then this is interepreted as a sequence of meters for each line in the stanza. Valid values can be either
one of the **values** from `classic_meters` in `poetics/config.py`, or one of the **keys** from `metrical_foot_adj`
in the same file. Can be empty.

#### Line count (`int`)  
The number of lines in the form.