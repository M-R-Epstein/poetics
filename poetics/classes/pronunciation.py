from collections import namedtuple

from poetics.lookups import get_word_endings

Syllable = namedtuple('Syllable', 'stress, onset, nucleus, coda')


class Pronunciation:
    def __init__(self, syllables, parent=None):
        self.parent = parent
        self.plaintext = None
        self.syllables = []
        self.stress = ''
        self.stress_index = None

        self.str_vowel = None  # Vowel sound in the stressed syllable.
        self.str_ini_con = None  # First single consonant sound in the stressed syllable.
        self.str_fin_con = None  # Last single consonant sound in the stressed syllable.
        self.str_bkt_cons = None  # All consonant sounds in the stressed syllable.
        self.word_ini_con = None  # First single consonant sound in the word.

        self.p_rhyme = None  # Perfect rhyme.
        self.p_rhyme_type = None  # Perfect rhyme type. Feminine (F) or masculine (M).
        self.r_rhyme = None  # Rich rhyme.
        self.n_rhyme = None  # Near rhyme.

        # Future: light rhyme (stressed syllables with unstressed syllables).
        # Future: unstressed rhyme (unstressed syllables with unstressed syllables).

        f_syllables = []
        for syllable in syllables:
            f_syllables.append(Syllable(syllable[0], syllable[1], syllable[2], syllable[3]))
        self.syllables = tuple(f_syllables)

        self.stress = ''.join([str(syllable.stress) for syllable in self.syllables])

        for index, syllable in enumerate(self.syllables):
            if syllable.onset and index == 0:
                self.word_ini_con = syllable.onset.split(' ')[0] or None
            if syllable.stress == 1 or len(syllables) == 1:
                self.stress_index = index
                self.str_vowel = syllable.nucleus or None
                self.str_ini_con = syllable.onset.split(' ')[0] or None
                self.str_fin_con = syllable.coda.split(' ')[-1] or None
                if syllable.coda and syllable.onset:
                    self.str_bkt_cons = ' '.join([syllable.onset, syllable.coda])

        # Create plaintext pronunciation.
        plain = []
        for syllable in self.syllables:
            plain.append(syllable.onset or None)
            plain.append(syllable.nucleus or None)
            plain.append(syllable.coda or None)
        self.plaintext = ' '.join(phonemes for phonemes in plain if phonemes)

        # Get word endings (used for near rhyme).
        endings = get_word_endings(self.plaintext)
        if endings:
            self.n_rhyme = tuple(endings)

        perfect_rhyme = []
        rich_rhyme = []
        for syllable in self.syllables[self.stress_index:]:
            if syllable.stress == 1:
                perfect_rhyme.extend([syllable.nucleus, syllable.coda])
            else:
                perfect_rhyme.extend([syllable.onset, syllable.nucleus, syllable.coda])
            rich_rhyme.extend([syllable.onset, syllable.nucleus, syllable.coda])
        self.r_rhyme = ' '.join([segment for segment in rich_rhyme if segment])
        self.p_rhyme = ' '.join([segment for segment in perfect_rhyme if segment])

    def __str__(self) -> str:
        return self.plaintext

    def __repr__(self) -> str:
        return '%s (%s)' % (super().__repr__(), self.plaintext)
