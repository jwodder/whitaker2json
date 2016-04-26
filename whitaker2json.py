#!/usr/bin/python
# Input: DICTPAGE.RAW from <http://archives.nd.edu/whitaker/dictpage.zip>
# cf. <http://archives.nd.edu/whitaker/wordsdoc.htm>
from   __future__ import print_function
import argparse
import codecs
import itertools
import json
import re
import sys
import zipfile

if sys.version_info[0] == 2:
    from io       import open
    from StringIO import StringIO
else:
    from io       import BytesIO as StringIO

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
        "A": None,
        "B": 'C.H.Beeson, A Primer of Medieval Latin, 1925 (Bee)',
        "C": 'Charles Beard, Cassell\'s Latin Dictionary 1892 (CAS)',
        "D": 'J.N.Adams, Latin Sexual Vocabulary, 1982 (Sex)',
        "E": 'L.F.Stelten, Dictionary of Eccles. Latin, 1995 (Ecc)',
        "F": 'Roy J. Deferrari, Dictionary of St. Thomas Aquinas, 1960 (DeF)',
        "G": 'Gildersleeve + Lodge, Latin Grammar 1895 (G+L)',
        "H": 'Collatinus Dictionary by Yves Ouvrard',
        "I": 'Leverett, F.P., Lexicon of the Latin Language, Boston 1845',
        "J": None,
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
    "PACK": "PACKON",
    "PREP": "preposition",
    "PRON": "pronoun",
    "V": "verb",
}

cases = {
    "NOM": "nominative",
    "GEN": "genitive",
    "DAT": "dative",
    "ACC": "accusative",
    "ABL": "ablative",
    "VOC": "vocative",
    "LOC": "locative",
}

verb_types = {
    "TRANS": "transitive",
    "INTRANS": "intransitive",
    "IMPERS": "impersonal",
    "DAT": "w/dative",
    "ABL": "w/ablative",
    "DEP": "deponent",
    "SEMIDEP": "semideponent",
    "PERFDEF": "perfect definite",
}

tenses = {
    "PRES": "present",
    "IMPF": "imperfect",
    "FUT": "future",
    "PERF": "perfect",
    "PLUP": "pluperfect",
    "FUTP": "future perfect",
    "X": None,
}

voices = {
    "ACTIVE": "active",
    "PASSIVE": "passive",
}

moods = {
    "IND": "indicative",
    "SUB": "subjunctive",
    "IMP": "imperative",
    "INF": "infinitive",
    "PPL": "participle",
    "X": None,
}

nth = {
    "(1st)": 1,
    "(2nd)": 2,
    "(3rd)": 3,
    "(4th)": 4,
    "(5th)": 5,
}

genders = {
    "M": "masculine",
    "F": "feminine",
    "N": "neuter",
    "C": "common",
    "X": None,
}

numbers = {
    "S": "singular",
    "P": "plural",
    "X": None,
}

pronoun_types = {
    "X": None,
    "PERS": "personal",
    "REL": "relative",
    "REFLEX": "reflexive",
    "DEMONS": "demonstrative",
    "INTERR": "interrogative",
    "INDEF":  "indefinite",
    "ADJECT": "adjectival",
}


class WhitakerError(ValueError):
    def __init__(self, header, msg):
        self.header = header
        self.msg = msg
        super(WhitakerError, self).__init__('Could not parse header {!r}: {}'\
                                            .format(header, msg))

class UnknownFieldError(WhitakerError):
    def __init__(self, header, unk_type, unk_value):
        self.header = header
        self.unk_type = unk_type
        self.unk_value = unk_value
        super(UnknownFieldError, self).__init__(header, 'unknown {}: {!r}'\
                                                        .format(unk_type,
                                                                unk_value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-E', '--error-file', type=argparse.FileType('w'),
                        help='Write unparseable lines to this file')
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Don't report unparsable lines")
    parser.add_argument('-U', '--utf8', action='store_true',
                        help='Assume the input is UTF-8 instead of Latin-1')
    parser.add_argument('-z', '--zip-url',
                        default='http://archives.nd.edu/whitaker/dictpage.zip',
                        help='URL from which to download the zipfile')
    parser.add_argument('-Z', '--zip-path', default='DICTPAGE.RAW',
                        help='Location of the input file in the zipfile')
    parser.add_argument('infile', nargs='?')
    args = parser.parse_args()
    if args.infile is None:
        try:
            import requests
        except ImportError:
            raise SystemExit('Downloading dictpage.zip requires the `requests`'
                             ' module:\n    sudo pip install requests')
        r = requests.get(args.zip_url)
        r.raise_for_status()
        fp = zipfile.ZipFile(StringIO(r.content), 'r').open(args.zip_path)
    elif args.infile.lower().endswith('.zip'):
        fp = zipfile.ZipFile(args.infile, 'r').open(args.zip_path)
    elif args.infile == '-':
        fp = sys.stdin
        if sys.version_info[0] >= 3:
            fp = fp.buffer
    else:
        fp = open(args.infile, 'rb')
    with codecs.getreader('utf-8' if args.utf8 else 'iso-8859-1')(fp) as verba:
        json.dump(list(whitaker(verba, args.error_file, args.quiet)),
                  args.outfile, sort_keys=True, indent=4, separators=(',',': '))

def decapitate(line):
    m = re.search(r'\s+\[(\w{5})\]\s+::\s+', line)
    return line[:m.end()] if m else None

def whitaker(fp, error_file=None, quiet=False):
    for header, lines in itertools.groupby(fp, decapitate):
        if header is None:
            for s in lines:
                if not quiet:
                    print('Could not locate end of header in line', repr(s),
                          file=sys.stderr)
                if error_file is not None:
                    print(s, end='', file=error_file)
            continue
        try:
            verbum = parse_header(header)
        except WhitakerError as e:
            if not quiet:
                print(e, file=sys.stderr)
            if error_file is not None:
                for s in lines:
                    print(s, end='', file=error_file)
        except Exception:
            print('Unexpected error while parsing header', repr(header),
                  file=sys.stderr)
            raise
        else:
            verbum["definition"] = '; '.join(s[len(header):].lstrip('|')
                                                            .rstrip()
                                                            .rstrip(';')
                                             for s in lines)
            yield verbum

def parse_header(header):
    m = re.search(r'^#(.+?)\s+([A-Z]+)\s+(.*?)\s+\[(\w{5})\] ::\s+$', header)
    if not m:
        raise WhitakerError(header, 'unknown format')
    parts, cls, classifiers, flags = m.groups()
    parts = [p if p != '-' else None for p in parts.split(', ')]
    classifiers = classifiers.split()
    verbum = dict()
    if classifiers == ["ADJ"]:
        # Special handling for "colossicon" and "curotrophoe":
        try:
            verbum["gender"] = genders[cls]
        except KeyError:
            raise UnknownFieldError(header, 'gender code', cls)
        cls = classifiers.pop()
    if cls not in classes:
        raise UnknownFieldError(header, 'part of speech', cls)
    verbum["class"] = {"code": cls, "value": classes[cls]}
    if len(parts) == 2 and parts[1] == 'undeclined':
        parts.pop()
        if cls in ('N', 'ADJ'):
            verbum["declinable"] = False
        elif cls == 'V':
            verbum["conjugatable"] = False
        else:
            verbum["inflectable"] = False
    if len(parts) == 2 and parts[1] == 'abb.':
        parts.pop()
        verbum["abbreviation"] = True
    for f, field in zip(flags, ["age", "area", "geo", "frequency", "source"]):
        if f in dict_flags[field]:
            verbum[field] = {"code": f, "value": dict_flags[field][f]}
        else:
            raise UnknownFieldError(header, field + ' code', f)

    def classify(*classifications):
        for field, lookup in classifications:
            if classifiers and classifiers[0] in lookup:
                code = classifiers.pop(0)
                if lookup is nth:
                    verbum[field] = lookup[code]
                else:
                    verbum[field] = {"code": code, "value": lookup[code]}
        if classifiers:
            raise UnknownFieldError(header, classes[cls] + ' classifier',
                                            classifiers[0])

    def explode(entry, *endings, **kwargs):
        abbrev = ' -'.join(endings)
        while abbrev:
            if entry.endswith(abbrev):
                stem = entry[:-len(abbrev)]
                return [stem + e for e in endings]
            elif abbrev == 'o -ae -o':
                # Match "duo -ae o"
                abbrev = 'o -ae oX'
            elif len(entry) != 24:
                break
            abbrev = abbrev[:-1]
        if 'or_bust' in kwargs:
            raise UnknownFieldError(header, kwargs['or_bust'], entry)
        else:
            return None

    if cls == 'N':
        if len(parts) == 1 and len(classifiers) == 5 and \
                re.search(r'^\d+$', classifiers[0]) and \
                re.search(r'^\d+$', classifiers[1]):
            verbum["inflected"] = True
            verbum["declension"] = int(classifiers.pop(0))
            verbum["variant"] = int(classifiers.pop(0))
            classify(("case", cases), ("number", numbers), ("gender", genders))
        else:
            classify(("declension", nth), ("gender", genders))

    elif cls == 'V':
        if len(parts) == 1 and len(classifiers) in (7,8) and \
                re.search(r'^\d+$', classifiers[0]) and \
                re.search(r'^\d+$', classifiers[1]) and \
                re.search(r'^\d+$', classifiers[5]):
            verbum["inflected"] = True
            verbum["conjugation"] = int(classifiers.pop(0))
            verbum["variant"] = int(classifiers.pop(0))
            verbum["person"] = int(classifiers.pop(3)) or None
            classify(("tense", tenses), ("voice", voices), ("mood", moods),
                     ("number", numbers), ("type", verb_types))
        else:
            classify(("conjugation", nth), ("type", verb_types))

    elif cls == 'ADJ':
        if len(parts) == 2:
            p0 = explode(parts[0], 'or', 'or', 'us')
            p1 = explode(parts[1], 'us', 'a', 'um')
            if p0 is not None and p1 is not None:
                parts = None
                verbum["comparative"] = p0
                verbum["superlative"] = p1
            elif p0 is not None or p1 is not None:
                raise WhitakerError(header, 'unknown adjective format')
        elif len(parts) == 3 and parts[1] == '(gen.)':
            del parts[1]
        elif len(parts) == 4:
            part1, part2, comparative, superlative = parts
            ps = explode(part2, 'a', 'um') or explode(part2, 'is', 'e')
            if ps is not None:
                parts = [part1] + ps
            elif part2.endswith(' (gen.)'):
                parts = [part1, part2[:-7]]
            else:
                parts = [part1, part2]
            if comparative is not None:
                comparative = explode(comparative, 'or', 'or', 'us',
                                      or_bust='comparative')
            if superlative is not None:
                superlative = explode(superlative, 'us', 'a', 'um',
                                      or_bust='superlative')
            verbum["comparative"] = comparative
            verbum["superlative"] = superlative
        if parts is not None and (parts[-1] or '').endswith(' (gen -ius)'):
            parts[-1] = parts[-1][:-11]
            verbum["gen_ius"] = True

    elif cls == 'PREP':
        classify(("case", cases))
        if "case" not in verbum:
            raise WhitakerError(header, 'no case specified for preposition')

    elif cls == 'ADV':
        if len(parts) == 3:
            verbum["superlative"] = [parts.pop()]
            verbum["comparative"] = [parts.pop()]
        elif len(parts) == 2 and (parts[0] or '').endswith('ius') and \
                (parts[1] or '').endswith('ime'):
            verbum["superlative"] = [parts.pop()]
            verbum["comparative"] = [parts.pop()]
            parts = None
        elif len(parts) != 1:
            raise WhitakerError(header, 'unknown adverb format')

    elif cls == 'NUM' and len(parts) == 4:
        cardinal, ordinal, distributive, adv = parts
        parts = explode(cardinal, 'i', 'ae', 'a') or \
                explode(cardinal, 'us', 'a', 'um') or \
                explode(cardinal, 'o', 'ae', 'o') or \
                explode(cardinal, 'es', 'es', 'ia') or \
                [cardinal]
        if ordinal is not None:
            ordinal = explode(ordinal, 'us', 'a', 'um', or_bust='ordinal')
        verbum["ordinal"] = ordinal
        if distributive is not None:
            distributive = explode(distributive, 'i', 'ae', 'a',
                                   or_bust='distributive')
        verbum["distributive"] = distributive
        verbum["numeral adverb"] = [adv]

    elif cls == 'PRON' or cls == 'PACK':
        if len(parts) == 1 and len(classifiers) == 5 and \
                re.search(r'^\d+$', classifiers[0]) and \
                re.search(r'^\d+$', classifiers[1]):
            verbum["inflected"] = True
            verbum["declension"] = int(classifiers.pop(0))
            verbum["variant"] = int(classifiers.pop(0))
            classify(("case", cases), ("number", numbers), ("gender", genders))
        else:
            classify(("type", pronoun_types))
            if len(parts) == 1 and parts[0].endswith(' (GEN)'):
                parts[0] = parts[0][:-6]
                verbum["genitive"] = True

    elif len(parts) != 1:
        raise WhitakerError(header, 'unexpected number of principal parts')

    elif classifiers:
        raise UnknownFieldError(header, classes[cls] + ' classifier',
                                classifiers[0])

    verbum["base_forms"] = parts
    return verbum

if __name__ == '__main__':
    main()
