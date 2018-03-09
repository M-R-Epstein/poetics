# Data specifications
## poem_forms.json
Made up of two lists and a dictionary: poem forms, repeating poem forms, and poem names by stanza.

### Poem forms
Provides the identification features for poetic forms. For example:
```python 
["French sonnet", ["ABBAABBACCDEDE", "ABBAABBACCDCCD", "ABBAABBACCDEED"], ["10", "12"], 14]
```
**Form name**  
string - Name of the poetic form.

**Rhyme schemes**  
list of strings - A list of the possible rhyme schemes (without spaces).

**Syllables**  
list of strings - Listing of possible syllable per line arrangements as strings, with values separated by spaces. If a 
single value is provided, this value is interpreted as applying to all lines. So `["10", "12"]` in the example indicates
that a French sonnet either has all lines of 10 syllables or all lines of 12 syllables.

**Line count**  
int - The number of lines in the form.  

### Repeating poem forms
Provides the identification features for poetic forms with repeating elements. For example:
```python 
["Terza Rima","","a2ba2","a2a2","","",""],
```
**Form name**  
string - name of the poetic form

**Rhyme head**  
string - This is the initial segment of the rhyme scheme for a given repetitious form which is not repeated. Because 
this segment is always the same, it should consist of capital letters (`AA` for example).  

**Rhyme core**  
string - This is the segment of the rhyme scheme for a given repetitious form that is repeated any number of times.
This segment uses a similar syntax to standard rhyme notation schemes. Capital letters are always the same in all 
repetitions. Lower case letters are replaced with the next available letter in the alphabet in each repetition. Lower 
case letters which are followed by a digit copy the letter from the preceeding stanza in the position specified by the 
digit.  

In the case of Terza Rima (as above), this segment is `a2ba2`. For the first instance of the repeating segment, all 
positions marked with `a` will be replaced with the next available letter in the alphabet, and then all positions marked
with `b`. This would result in `ABA`. In the next repetition, `b` would be replaced with the next available letter (`C`)
but both instances of `a2` would be replaced with the second letter from the previous repetition (`B`) which results in 
`BCB`. A third repetition would result in `ABA BCB CDC`.

**Rhyme tail**  
string - This is the final segment of the rhyme scheme for a given repetitious form which is not repeated. This segment 
uses the same syntax as the rhyme core, referencing the final repetition of the core.

**Syllables head**  
string - This is the initial segment of the syllable per line scheme for a given form which is not repeated.
This is recorded as a string of integers separated by spaces indicating the syllable lengths.  

**Syllables core**  
string - This is the segment of the syllable per line scheme for a given form that is repeated. Recorded in the same
fashion as the head.  

**Syllables tail**  
string - This is the final segment of the syllable per line scheme for a given form which is not repeated.
Recorded in the same fashion as the head.  

### Poem names by stanza
A dictionary that provides the name that should be assigned to a poem which is made up exclusively of a single type of 
stanza.
```python 
"Ballade Stanza": ["Huitain", "Ballade Stanzas"]
```
**Stanza type**  
string - the key for each entry is the name of the stanzaic form.  

**Single stanza poetic form**  
string - Indicates the name that should be assigned to a poem's form if it is entire made up of a single instance
of a kind of stanza.  

**Multiple stanza poetic form**   
string - Indicates the name that should be assigned to a poem's form if it is exclusively composed of multiple stanazas 
of the given type.