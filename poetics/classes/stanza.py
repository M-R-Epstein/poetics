from poetics.conversions import get_sound_set_groups, feats_to_scheme
from poetics.logging import print_sound_set
from poetics.lookups import name_stanza


class Stanza:
    def __init__(self, tokens, lines, parent=None):
        self.parent = parent
        self.tokens = tokens
        self.word_tokens = [token for token in tokens if not token.is_punct and not token.is_wspace]
        self.lines = lines
        self.line_lengths = []
        self.meters = None
        self.form = None

        # Line final rhyme schemes.
        self.scm_p_rhymes = None
        self.scm_r_rhymes = None
        self.scm_asso = None
        self.scm_cons = None
        self.scm_bkt_cons = None
        self.scm_str_allit = None
        self.scm_ini_allit = None

        # Line initial rhyme schemes.
        self.scm_i_p_rhymes = None
        self.scm_i_r_rhymes = None
        self.scm_i_asso = None
        self.scm_i_cons = None
        self.scm_i_bkt_cons = None
        self.scm_i_str_allit = None
        self.scm_i_ini_allit = None

        # Stanza internal sonic features.
        self.p_rhyme = None
        self.r_rhyme = None
        self.n_rhyme = None
        self.asso = None
        self.cons = None
        self.bkt_cons = None
        self.str_allit = None
        self.ini_allit = None

    def __str__(self) -> str:
        return ''.join([token.token for token in self.tokens])

    def __repr__(self) -> str:
        return '%s (%s)' % (super().__repr__(), ' '.join([token.token for token in self.word_tokens[0:2]]))

    def get_rhymes(self):
        rhyme_features = [('p_rhyme', 'p_rhymes'), ('r_rhyme', 'r_rhymes'), ('str_vowel', 'asso'),
                          ('str_fin_con', 'cons'), ('str_bkt_cons', 'bkt_cons'), ('str_ini_con', 'str_allit'),
                          ('word_ini_con', 'ini_allit')]
        for feature, attr_name in rhyme_features:
            scm = feats_to_scheme([getattr(line.final_word.pronunciations[0], feature) for line in self.lines], True)
            iscm = feats_to_scheme([getattr(line.initial_word.pronunciations[0], feature) for line in self.lines], True)
            setattr(self, 'scm_' + attr_name, scm)
            setattr(self, 'scm_i_' + attr_name, iscm)

    def get_form(self):
        # Create a list of syllables per line.
        for line in self.lines:
            self.line_lengths.append(str(line.syllables))
        # If they are all the same length, we only need the one meter.
        if len(set(self.line_lengths)) == 1:
            self.meters = [meter for length, (meter, repetitions, name) in self.parent.meters.items()
                           if length == int(self.line_lengths[0])][0]
        # Else, a list of meters
        else:
            meter_list = []
            for length in self.line_lengths:
                meter_list.append(self.parent.meters[int(length)][0])
            self.meters = ' '.join(meter_list)
        self.form = name_stanza(self.scm_p_rhymes, self.line_lengths, self.meters, len(self.lines))

    def get_sonic_features(self):
        asso_list, cons_list, bkt_cons_list, str_allit_list, ini_allit_list = [], [], [], [], []
        # Retrieve lists of sounds from word objects.
        for token in self.word_tokens:
            asso_list.append(list(set([pro.str_vowel for pro in token.pronunciations if pro.str_vowel])))
            cons_list.append(list(set([pro.str_fin_con for pro in token.pronunciations if pro.str_fin_con])))
            bkt_cons_list.append(list(set([pro.str_bkt_cons for pro in token.pronunciations if pro.str_bkt_cons])))
            str_allit_list.append(list(set([pro.str_ini_con for pro in token.pronunciations if pro.str_ini_con])))
            ini_allit_list.append(list(set([pro.word_ini_con for pro in token.pronunciations if pro.word_ini_con])))

        # Get feature groups for rhyme-like features
        tokens = [token.token for token in self.word_tokens]
        max_distance = max(self.parent.avg_words_per_line, 5)
        self.asso = get_sound_set_groups(asso_list, tokens, max_distance)
        self.cons = get_sound_set_groups(cons_list, tokens, max_distance)
        self.bkt_cons = get_sound_set_groups(bkt_cons_list, tokens, max_distance)
        self.str_allit = get_sound_set_groups(str_allit_list, tokens, max_distance)
        self.ini_allit = get_sound_set_groups(ini_allit_list, tokens, max_distance)

    def print_sonic_features(self):
        tokens = [token.token for token in self.word_tokens]
        if self.asso:
            print_sound_set('Assonance', self.asso, tokens)
        if self.cons:
            print_sound_set('Consonance', self.cons, tokens)
        if self.bkt_cons:
            print_sound_set('Bracket Consonance', self.bkt_cons, tokens)
        if self.str_allit:
            print_sound_set('Stressed Alliteration', self.str_allit, tokens)
        if self.ini_allit:
            print_sound_set('Alliteration', self.ini_allit, tokens)
