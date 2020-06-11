#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Find the name for a Montréal-Python release"""

from argparse import ArgumentParser

from string import ascii_lowercase

from mtlpyrelease import release


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
    parser.add_argument("--min-length", dest="min_length", default=0, type=int,
                        help="minimum length for words")
    parser.add_argument("adjective", type=str,
                        help="adjective to generate")
    parser.add_argument("noun", type=str,
                        help="noun to generate")

    args = parser.parse_args()

    # Proper and common nouns are equally valid, so all choices are normalized
    # to be in the same lower-case bucket.
    adjective = args.adjective.lower()
    noun = args.noun.lower()

    if not adjective:
        adjective = release.random_choice(ascii_lowercase)

    if not noun:
        noun = release.random_choice(ascii_lowercase)

    adjs = release.find_words("adj", min_length=args.min_length)[adjective]
    nouns = release.find_words("noun", min_length=args.min_length)[noun]

    names = release.get_release_names(args.number, adjs, nouns)
    fr_names, en_names = release.generate_release_names(
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

    print("\n%s" % output)


if __name__ == '__main__':
    main()
