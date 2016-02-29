#!/usr/bin/python
# Input: DICTPAGE.RAW from <http://archives.nd.edu/whitaker/dictpage.zip>
# cf. <http://archives.nd.edu/whitaker/wordsdoc.htm>
from   __future__ import print_function
import codecs
import itertools
import json
import re
import sys

dict_flags = {
    "age": {
        "A": 'archaic',
        "B": 'early',
        "C": 'classical',
        "D": 'late',
        "E": 'later',
        "F": 'medieval',
        "G": 'scholarly',
        "H": 'modern',
        "X": None,
    },
    "area": {
        "A": 'agriculture',
        "B": 'biology',
        "D": 'art',
        "E": 'ecclesiastic',
        "G": 'rhetoric & literature',
        "L": 'law',
        "P": 'poetic',
        "S": 'philosophy',
        "T": 'technical',
        "W": 'military',
        "Y": 'mythology',
        "X": None,
    },
    "geo": {
        "A": 'Africa',
        "B": 'Britian',
        "C": 'China',
        "D": 'Scandinavia',
        "E": 'Egypt',
        "F": 'France/Gaul',
        "G": 'Germany',
        "H": 'Greece',
        "I": 'Italy',
        "J": 'India',
        "K": 'Balkans',
        "N": 'Netherlands',
        "P": 'Persia',
        "Q": 'Near East',
        "R": 'Russia',
        "S": 'Iberia',
        "U": 'Eastern Europe',
        "X": None,
    },
    "frequency": {
        "A": 'very freq',
        "B": 'frequent',
        "C": 'common',
        "D": 'lesser',
        "E": 'uncommon',
        "F": 'very rare',
        "I": 'inscription',
        "M": 'graffiti',
        "N": 'Pliny',
        "X": None,
    },
    "source": {
        "A": 'SOURCE A',
        "B": 'C.H.Beeson, A Primer of Medieval Latin, 1925 (Bee)',
        "C": 'Charles Beard, Cassell\'s Latin Dictionary 1892 (CAS)',
        "D": 'J.N.Adams, Latin Sexual Vocabulary, 1982 (Sex)',
        "E": 'L.F.Stelten, Dictionary of Eccles. Latin, 1995 (Ecc)',
        "F": 'Roy J. Deferrari, Dictionary of St. Thomas Aquinas, 1960 (DeF)',
        "G": 'Gildersleeve + Lodge, Latin Grammar 1895 (G+L)',
        "H": 'Collatinus Dictionary by Yves Ouvrard',
        "I": 'Leverett, F.P., Lexicon of the Latin Language, Boston 1845',
        "J": 'SOURCE J',
        "K": 'Calepinus Novus, modern Latin, by Guy Licoppe (Cal)',
        "L": 'Lewis, C.S., Elementary Latin Dictionary 1891',
        "M": 'Latham, Revised Medieval Word List, 1980',
        "N": 'Lynn Nelson, Wordlist',
        "O": 'Oxford Latin Dictionary, 1982 (OLD)',
        "P": 'Souter, A Glossary of Later Latin to 600 A.D., Oxford 1949',
        "Q": 'Other, cited or unspecified dictionaries',
        "R": 'Plater & White, A Grammar of the Vulgate, Oxford 1926',
        "S": 'Lewis and Short, A Latin Dictionary, 1879 (L+S)',
        "T": 'Found in a translation -- no dictionary reference',
        "U": 'Du Cange',
        "V": 'Vademecum in opus Saxonis - Franz Blatt (Saxo)',
        "W": "Whitaker's personal guess",
        "Y": "Temp special code",
        "X": None,
        "Z": "Sent by user; no dictionary reference (mostly John White of Blitz Latin)",
    },
}

classes = {
    "ADJ": "adjective",
    "ADV": "adverb",
    "CONJ": "conjunction",
    "INTERJ": "interjection",
    "N": "noun",
    "NUM": "number",
    "PREP": "preposition",
    "PRON": "pronoun",
    "V": "verb",
}

cls_rgx = r'(?:' + '|'.join(classes.keys()) + ')'

cases = {
    "ABL": "ablative",
    "ACC": "accusative",
    "GEN": "genitive",
}

verb_types = {
    "TRANS": "transitive",
    "INTRANS": "intransitive",
    "IMPERS": "impersonal",
    "DAT": "w/dative",
    "DEP": "deponent",
    "SEMIDEP": "semideponent",
    "PERFDEF": "perfect definite",
}

nth = {
    "(1st)": 1,
    "(2nd)": 2,
    "(3rd)": 3,
    "(4th)": 4,
    "(5th)": 5,
}

genders = {"M": "M", "F": "F", "N": "N", "C": "C"}
#genders = {
#    "M": "masculine",
#    "F": "feminine",
#    "N": "neuter",
#    "C": "common",
#}


class WhitakerError(ValueError):
    pass

class UnknownFieldError(WhitakerError):
    def __init__(self, header, unk_type, unk_value):
        self.header = header
        self.unk_type = unk_type
        self.unk_value = unk_value
        super(UnknownFieldError, self).__init__(header, unk_type, unk_value)

    def __str__(self):
        return 'Could not parse header {0.header!r}: unknown {0.unk_type}:' \
               ' {0.unk_value!r}'.format(self)


def main():
    if len(sys.argv) > 1:
        fp = open(sys.argv[1])
    else:
        import requests
        import zipfile
        r = requests.get('http://archives.nd.edu/whitaker/dictpage.zip',
                         stream=True)
        r.raise_for_status()
        zfp = zipfile.ZipFile(r.raw, 'r')
        fp = zfp.open('DICTPAGE.RAW')
    ### Add an option for assuming the input is UTF-8
    with codecs.getreader('iso-8859-1')(fp) as verba:
        json.dump(list(whitaker(verba)), sys.stdout, sort_keys=True, indent=4,
                  separators=(',', ': '))

def whitaker(fp):
    for header, lines in itertools.groupby(fp, lambda s: s[:112]):
        try:
            verbum = parse_header(header)
        except WhitakerError as e:
            print(e, file=sys.stderr)
        except Exception as e:
            print(repr(header), file=sys.stderr)
            raise
        #    print('{0.__class__.__name__}: {0}: {1!r}'.format(e, header),
        #          file=sys.stderr)
        else:
            verbum["definition"] = '; '.join(s[112:].lstrip('|').rstrip()
                                                    .rstrip(';') for s in lines)
            yield verbum

def parse_header(header):
    m = re.search(r'^#(.+?)\s+(' + cls_rgx + r')\s+(.*?)\s+\[(\w{5})\] ::\s+$',
                  header)
    if not m:
        raise WhitakerError(header)
    parts, cls, classifiers, flags = m.groups()
    parts = [p if p != '-' else None for p in parts.split(', ')]
    classifiers = classifiers.split()
    if cls not in classes:
        raise UnknownFieldError(header, 'part of speech', cls)
    verbum = {
        "class": classes[cls],
    }
    if len(parts) == 2 and parts[1] == 'undeclined':
        parts.pop()
        verbum["undeclined"] = True
    if len(parts) == 2 and parts[1] == 'abb.':
        parts.pop()
        verbum["abbreviation"] = True
    for f, field in zip(flags, ["age", "area", "geo", "frequency", "source"]):
        if f in dict_flags[field]:
            verbum[field] = dict_flags[field][f]
        else:
            raise UnknownFieldError(header, field + ' flag', f)

    def classify(*classifications):
        for field, lookup in classifications:
            if classifiers and classifiers[0] in lookup:
                verbum[field] = lookup[classifiers.pop(0)]
        if classifiers:
            raise UnknownFieldError(header, classes[cls] + ' classifier',
                                            classifiers[0])

    if cls == 'N':
        classify(("declension", nth), ("gender", genders))
        verbum.setdefault("declension", None)

    elif cls == 'V':
        classify(("conjugation", nth), ("type", verb_types))
        verbum.setdefault("conjugation", None)
        verbum.setdefault("type", None)
        if verbum["type"] == verb_types["IMPERS"] and len(parts) == 3 and \
                parts[0].endswith('it') and \
                parts[1] is not None and parts[1].endswith('isse') and \
                (parts[2] is None or parts[2].endswith(' est')):
            verbum["type"] = "impersonal perfect definite"

    elif cls == 'ADJ':
        if len(parts) == 3 and parts[1] == '(gen.)':
            del parts[1]
        elif len(parts) == 4:
            part1, part2, comparative, superlative = parts
            if part2.endswith('a -um'):
                parts = [part1, part2[:-4], part2[:-5] + 'um']
            elif part2.endswith('is -e'):
                parts = [part1, part2[:-3], part2[:-5] + 'e']
            elif part2.endswith(' (gen.)'):
                parts = [part1, part2[:-7]]
            else:
                parts = [part1, part2]
            if comparative is not None:
                if comparative.endswith('or -or -us'):
                    stem = comparative[:-10]
                    comparative = [stem + 'or', stem + 'or', stem + 'us']
                else:
                    raise UnknownFieldError(header, 'comparative', comparative)
            if superlative is not None:
                if superlative.endswith('us -a -um'):
                    stem = superlative[:-9]
                    superlative = [stem + 'us', stem + 'a', stem + 'um']
                else:
                    raise UnknownFieldError(header, 'superlative', superlative)
            verbum["comparative"] = comparative
            verbum["superlative"] = superlative

    elif cls == 'PREP':
        #classify(("case", cases))
        if not classifiers:
            raise WhitakerError(header)
        elif classifiers[0] not in cases:
            raise UnknownFieldError(header, 'preposition case', classifiers[0])
        else:
            verbum["case"] = cases[classifiers[0]]

    elif cls == 'ADV' and len(parts) == 3:
        verbum["superlative"] = [parts.pop()]
        verbum["comparative"] = [parts.pop()]

    elif cls == 'NUM' and len(parts) == 4:
        cardinal, ordinal, distributive, adv = parts
        if cardinal.endswith('i -ae -a'):
            stem = cardinal[:-8]
            parts = [stem + 'i', stem + 'ae', stem + 'a']
        else:
            parts = [cardinal]

        if ordinal is None:
            verbum["ordinal"] = None
        elif ordinal.endswith('us -a -um'):
            stem = ordinal[:-9]
            verbum["ordinal"] = [stem + 'us', stem + 'a', stem + 'um']
        else:
            raise UnknownFieldError(header, 'ordinal', ordinal)

        if distributive is None:
            verbum["distributive"] = None
        elif distributive.endswith('i -ae -a'):
            stem = distributive[:-8]
            verbum["distributive"] = [stem + 'i', stem + 'ae', stem + 'a']
        else:
            raise UnknownFieldError(header, 'distributive', distributive)

        verbum["numeral adverb"] = [adv]

    elif cls != 'PRON' and len(parts) != 1:
        raise WhitakerError(header)

    verbum["parts"] = parts
    return verbum

if __name__ == '__main__':
    main()
