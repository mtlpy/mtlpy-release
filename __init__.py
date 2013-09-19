#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Find the name for a Montréal-Python release"""

from collections import defaultdict
from random import choice
from argparse import ArgumentParser

WN_BASE = "/usr/share/wordnet/index."

BASE_MP = 17

def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mp_number", type=int,
                        help=u"Montréal-Python event number")
    parser.add_argument("-n", "--number", type=int, default=1,
                        help=u"number or names to generate")
    return parser.parse_args()


def find_words(type):
    """ Return a dict of first letter to set of words. """
    assert type in ["adj", "noun"]

    words = defaultdict(lambda : [])

    for l in open(WN_BASE + type):
        if l and not l.startswith(" "):
            w = l.split()[0].strip()
            if "_" not in w:
                words[l[0].lower()].append(w)
    return words


def main():
    args = parse_args()

    letter = chr(ord("a") + args.mp_number - BASE_MP)
    adjs = find_words("adj")[letter]
    nouns = find_words("noun")[letter]

    names = []
    for i in range(args.number):
        names.append("%s %s" % (choice(adjs), choice(nouns)))
    for name in sorted(names, key=len):
        print name

if __name__ == '__main__':
    main()
