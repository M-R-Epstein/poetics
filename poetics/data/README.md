# Data specifications

---

## poem_forms.json
Made up of two lists and a dictionary: poem forms, repeating poem forms, and poem names by stanza.

### Forms
Provides the identification features for poetic forms. Examples:
```json 
["French sonnet", ["ABBAABBACCDEDE", "ABBAABBACCDCCD", "ABBAABBACCDEED"], ["10", "12"], 14],
["Bragi", ["ABCCBACBAABC"], ["6 8 10 10 8 6 10 8 6 6 8 10"], 12]
```
####Components  
**Form name (`str`)**  
Name of the poetic form.

**Rhyme schemes (`list[str]`)**  
A list of the possible rhyme schemes (without spaces).

**Syllables (`list[str]`)**  
Listing of possible syllable per line arrangements as strings, with values separated by spaces. If a single value is 
provided, this value is interpreted as applying to all lines. So `["10", "12"]`, as above, indicates that a _French 
sonnet_ either has all lines of 10 syllables or all lines of 12 syllables. For _Bragi_, the number of syllables has
been specified for each individual line.

**Line count (`int`)**  
The number of lines in the form.  

### Repeating forms
Provides the identification features for poetic forms with repeating elements. For example:
```json 
["Terza Rima","","a2ba2","a2a2","","",""],
["Brevee","","aabccb","","","2 2 4 2 2 4",""]
```
**Form name (`str`)**  
The name of the poetic form

**Rhyme head (`str`)**  
This is the initial segment of the rhyme scheme for the form which is not repeated. Because this segment is 
always the same, it should consist of capital letters (`AA` for example).  

**Rhyme core (`str`)**  
This is the segment of the rhyme scheme for the form that is repeated any number of times. This segment uses 
a similar syntax to standard rhyme notation schemes. Capital letters are always the same in all  repetitions.
Lower case letters are replaced with the next available letter in the alphabet in each repetition. Lower 
case letters which are followed by a digit copy the letter from the preceeding stanza in the position 
specified by the  digit.  

In the case of Terza Rima (as above), this segment is `a2ba2`. For the first instance of the repeating segment, all 
positions marked with `a` will be replaced with the next available letter in the alphabet, and then all positions marked
with `b`. This would result in `ABA`. In the next repetition, `b` would be replaced with the next available letter (`C`)
but both instances of `a2` would be replaced with the second letter from the previous repetition (`B`) which results in 
`BCB`. A third repetition would result in `ABA BCB CDC`.

**Rhyme tail (`str`)**  
This is the final segment of the rhyme scheme for a given repetitious form which is not repeated. This segment 
uses the same syntax as the rhyme core, referencing the final repetition of the core.

**Syllables head (`str`)**  
This is the initial segment of the syllable per line scheme for a given form which is not repeated.
This is recorded as a string of integers separated by spaces indicating the syllable lengths.  

**Syllables core (`str`)**  
This is the segment of the syllable per line scheme for a given form that is repeated. Recorded in the same
fashion as the head.  

**Syllables tail (`str`)**  
This is the final segment of the syllable per line scheme for a given form which is not repeated.
Recorded in the same fashion as the head.  

### Poem names by stanza
A dictionary that provides the name that should be assigned to a poem which is made up exclusively of a single type of 
stanza.
```json 
"Ballade Stanza": ["Huitain", "Ballade Stanzas"],
"Heroic Sonnet": ["", "Heroic Sonnets"]
```
**Stanza type (`str`)**  
The key for each entry is the name of the stanzaic form.  

**Single stanza poetic form (`str`)**  
Indicates the name that should be assigned to a poem's form if it is entire made up of a single instance
of a kind of stanza. Can be empty (`""`), in which case the name of the stanza form will be used.

**Multiple stanza poetic form (`str`)**   
Indicates the name that should be assigned to a poem's form if it is exclusively composed of multiple stanazas 
of the given type. Can be empty (`""`), in which case the name of the stanza form will be used.

---

## stanza_forms.json
A single list that stores attributes of stanzaic forms for identification.
```json 
["Count Up", [], ["1 2 3 4 5 6 7 8 9 10"], [], 10],
["Short Couplet", ["aa"], ["8"], ["iambic", "trochaic"], 2],
["Sapphic Stanza", [], [], ["sapphic sapphic sapphic adonic"], 4],
["Sextilla", ["aabccb", "ababcc"], ["8"], [], 16]
```
**Form name (`str`)**  
The name of the stanzaic form.  

**Rhyme schemes (`list[str]`)**  
A list of the possible rhyme schemes of a stanza of the form. Can be empty.

**Syllables (`list[str]`)**  
A list of the possible arrangements of syllables per line for the form. A sequence of integers
separated by spaces (as in _Count Up_ above) is interpreted as a sequence of syllable counts per line.
A single integer (as in _Short Couplet_) is interpreted as indicating that all lines should be of the given
length(s). Can be empty.

**Meters (`list[str]`)**  
A list of the possible meters for the form. As with syllables, if a single meter is included, it is 
interpreted as applying to all lines of the stanza. If multiple meters are included, separated by spaces,
then this is interepreted as a sequence of meters for each line in the stanza. Valid values can be either
one of the _values_ from `classic_meters` in `poetics/config.py`, or one of the keys from `metrical_foot_adj`
in the same file. Can be empty.

**Line count (`int`)**  
The number of lines in the form.

