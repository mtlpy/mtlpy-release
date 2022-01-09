# -*- coding: utf-8 -*-
import os
import platform
import time
import unicodedata

from collections import defaultdict
from random import Random, choice, randrange, getstate, setstate, seed
from translate import Translator
from string import ascii_lowercase

WN_BASE = "/usr/share/wordnet/index."
WN_BASE_DARWIN = "/usr/local/Cellar/wordnet/3.1/dict/index."


# seed the PRNG with today's date to have a consistent random choice all
# day long -- note that this does not affect other executions
# random.choice as the PRNG seed is reset on every call
random_choice = Random(int(time.strftime('%Y%m%d'))).choice


def strip_accents(s):
    return ''.join(char for char in unicodedata.normalize('NFD', s)
                   if unicodedata.category(char) != 'Mn')


def get_release_names(num, adjectives, nouns):
    # get more names then requested to allow refetching translation
    # and regeneration of release name if it doesn't pass our tests,
    # see generate_release_names() for the selection logic
    names = []

    num_nouns = [n*10 for n in [num]] or 10
    for i in range(num_nouns.pop()):
        name = ' '.join([choice(adjectives), choice(nouns)])
        names.append(name)

    return names


def build_path(type):
    """Returns the path to the dictionary"""
    if platform.system() == 'Darwin':
        return WN_BASE_DARWIN + type
    return WN_BASE + type


def find_words(word_type, min_length=0):
    """Returns a dict of first letter to set of words."""
    assert word_type in ["adj", "noun"]

    words = defaultdict(lambda: [])

    for l in open(build_path(word_type)):
        if l and not l.startswith(" "):
            w = l.split()[0].strip()
            if "_" in w:
                continue
            elif len(w) < min_length:
                continue
            else:
                words[l[0].lower()].append(w)

    return words


def generate_release_names(num, names, translate=True, show_excluded=False):
    """Generate release names for Montréal Python edition

    num: amount of names to generate
    names: list of English names in format "Adjective Noun"
    translate: query google translate to provide French translation

    returns a tuple of two lists in format: (french names, english names)
    """
    en_names = []
    fr_names = []

    for en_name in sorted(names, key=len):
        if len(en_names) == num:
            break

        if not translate:
            en_names.append(en_name)
            continue

        translator = Translator(from_lang='en', to_lang='fr')
        fr_name = translator.translate(en_name).encode('utf8')

        # allow another run when the translated name
        # produces more than two words for our release name
        if len(fr_name.split(' ')) != 2:
            continue

        en_adj, en_noun = en_name.strip().split(' ')
        fr_adj, fr_noun = fr_name.strip().split(' ')

        # only keep release names for which one of the
        # translation's opposed word is a match.
        s_fr_adj = strip_accents(fr_adj.decode('utf8'))
        s_fr_noun = strip_accents(fr_noun.decode('utf8'))

        save = lambda l, adj, noun: l.append(' '.join([adj, noun]))
        if s_fr_adj == en_noun:
            # TODO: s_fr_adj is really french?
            save(en_names, en_adj, en_noun)
            save(fr_names, fr_adj, fr_noun)
            continue
        elif s_fr_noun == en_adj:
            # TODO: s_fr_noun is really french?
            save(en_names, en_adj, en_noun)
            save(fr_names, fr_adj, fr_noun)
            continue
        elif show_excluded:
            c = lambda c: ' '.join([w.capitalize() for w in c.split(' ')])
            print("excluded: %s (%s)" % (c(en_name), c(fr_name)))

    return fr_names, en_names


def event_num_offsets(num):
    ''' Return two offsets to define how the words of event names are selected. 
    
    Every 26 events, a new series is generated. Inside a series, the 
    progression of letters from one event to the next is obvious.
    
    This system was is not historically compatible with the events up to MP-95. 
    It was first used at MP-96 and could extend to infinity if needed. '''
    old_state = getstate()
    series = 6 + (num - 96) // 26
    event_offset = (num - 96) % 26
    
    # going deterministic for a moment
    seed(f"This is a beatiful day to hack. Series: {series}")  

    adj_offset = (randrange(26) + event_offset * choice([-1, 1])) % 26
    nout_offset = (randrange(26) + event_offset * choice([-1, 1])) % 26

    setstate(old_state)  # back to chaos!

    return (adj_offset, nout_offset)


def relnum_to_letters(num):
    ''' Convert an event number to a pair of letters for the English initials
    of the event name. 

    On rare exceptions, the initials derived from the following rules were
    used for the French name, but in most cases, the rule was applied to the
    English name.'''

    if num < 17:
        # The first 16 events never had a name.
        raise ValueError("Event #{} didn't have a name.".format(num))
    elif num < 43:
        # the next 26 events repeated the letter
        letter = chr(ord('a') + num - 17)
        return (letter, letter)
    elif (57 <= num <= 69) or (43 <= num <= 56):
        # from #43 to 56 and from #57 to 69, noun is one letter ahead of adj, 
        # advance by two per event
        if num < 57:
            offset = (num - 43) * 2
        else:
            offset = (num - 57) * 2
        adj = chr(ord('a') + offset)
        noun = chr(ord('b') + offset)
        return (adj, noun)
    elif 70 <= num <= 95:
        # starting with #70, adj is 'z', noun is 'a', they move in
        # opposite directions
        adj = chr(ord('z') - num + 70)
        noun = chr(ord('a') + num - 70)
        return (adj, noun)
    else:
        adj_o, noun_o = event_num_offsets(num)
        return ascii_lowercase[adj_o], ascii_lowercase[noun_o]
