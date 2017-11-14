#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Find the name for a Montréal-Python release"""

import os
import platform
import time
import unicodedata

from argparse import ArgumentParser
from collections import defaultdict
from random import Random, choice
from string import ascii_lowercase
from translate import Translator

WN_BASE = "/usr/share/wordnet/index."
WN_BASE_DARWIN = "/usr/local/Cellar/wordnet/3.1/dict/index."


# seed the PRNG with today's date to have a consistent random choice all
# day long -- note that this does not affect other executions
# random.choice as the PRNG seed is reset on every call
random_choice = Random(int(time.strftime('%Y%m%d'))).choice


def strip_accents(s):
    return ''.join(char for char in unicodedata.normalize('NFD', s)
                   if unicodedata.category(char) != 'Mn')


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
            print "excluded: %s (%s)" % (c(en_name), c(fr_name))

    return fr_names, en_names


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


def find_words(word_type):
    """Returns a dict of first letter to set of words."""
    assert word_type in ["adj", "noun"]

    words = defaultdict(lambda: [])

    for l in open(build_path(word_type)):
        if l and not l.startswith(" "):
            w = l.split()[0].strip()
            if "_" not in w:
                words[l[0].lower()].append(w)

    return words


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--number", default=10, dest='number',
                        type=int, help="number or names to generate")
    parser.add_argument("-T", "--translation", default=False,
                        dest="translate", action="store_true",
                        help="force the script not to query google translate")
    parser.add_argument("-S", "--show-excluded", default=False,
                        dest="show_excluded", action="store_true",
                        help="print names excluded by selection")
    parser.add_argument("adjective", type=str,
                        help="adjective to generate")
    parser.add_argument("noun", type=str,
                        help="noun to generate")

    args = parser.parse_args()

    adjective = args.adjective
    noun = args.noun

    if not adjective:
        adjective = random_choice(ascii_lowercase)

    if not noun:
        noun = random_choice(ascii_lowercase)

    adjs = find_words("adj")[adjective]
    nouns = find_words("noun")[noun]

    names = get_release_names(args.number, adjs, nouns)
    fr_names, en_names = generate_release_names(
        args.number,
        names,
        translate=args.translate,
        show_excluded=args.show_excluded)

    output = ""
    for n, en_name in enumerate(en_names):
        en_name = ' '.join([word.capitalize() for word in en_name.split(' ')])
        if fr_names:
            fr_name = ' '.join([word.decode('utf8').capitalize()
                                for word in fr_names[n].split(' ')])
        elif not args.translate:
            fr_name = ''

        output += '{0:>32}'.format(en_name)

        if fr_name:
            output += ' - {1:<32}\n'.format(fr_name)
        else:
            output += '\n'

    print "\n%s" % output


if __name__ == '__main__':
    main()
