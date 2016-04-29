This is a script for converting the
[`DICTPAGE.RAW`](http://archives.nd.edu/whitaker/dictpage.htm) Latin-English
dictionary file from [William Whitaker's
WORDS](http://archives.nd.edu/whitaker/words.htm) into JSON so that it can be
processed by programs made in this decade.  It is intended to work with both
Python 2.7 and Python 3.2+, the only external dependency being [the `requests`
package](http://www.python-requests.org), which is only needed for one optional
feature (see below).


Usage
=====

    whitaker2json.py [-E|--error-file <file>]
                     [-o|--outfile <file>]
                     [-q|--quiet]
                     [-U|--utf8]
                     [-z|--zip-url <URL>]
                     [-Z|--zip-path <path>]
                     [<infile>]

Input to the script must be either `DICTPAGE.RAW` or another sequence of lines
in the same format.  `whitaker2json.py` can acquire its input in three ways:

1. If no input file is specified on the command line, the script will download
   the zipfile at <http://archives.nd.edu/whitaker/dictpage.zip> (or another
   URL specified with the `--zip-url` option), extract the `DICTPAGE.RAW` entry
   from it (or another path specified with the `--zip-path` option), and use
   that as its input.  This mode requires the Python
   [`requests`](http://www.python-requests.org) module.

2. If an input file is specified and its name ends with "`.zip`" (case
   insensitive), it will be treated as a zipfile, and the `DICTPAGE.RAW` entry
   (or another path specified with the `--zip-path` option) will be extracted
   from it and used as the script's input.

3. Otherwise, the input file will be read as-is.  The script can be told to
   read unzipped input from standard input by specifying "`-`" as the name of
   the input file.


Options
-------

- `-E <file>`, `--error-file <file>` — Write all unparsable input lines to
  `<file>`

- `-o <file>`, `--outfile <file>` — Write the JSON output to `<file>` instead
  of standard output

- `-q`, `--quiet` — By default, unparsable input lines are written to standard
  error along with a brief description of where parsing went wrong.  The
  `--quiet` option disables this behavior.

- `-U`, `--utf8` — By default, the input is assumed to be encoded in ISO-8859-1
  (Latin-1), the same encoding used by the official `DICTPAGE.RAW`.  This
  option tells the script to expect input in UTF-8 instead.  (`iconv` or a
  similar tool must be used for files in other encodings.)

- `-z <URL>`, `--zip-url <URL>` — Specify the URL from which to download the
  zipfile in mode 1 (see above); default value:
  `http://archives.nd.edu/whitaker/dictpage.zip`.  This option is ignored in
  modes 2 & 3.

- `-Z <path>`, `--zip-path <path>` — Specify the file within the zipfile to
  extract in modes 1 & 2 (see above); default value: `DICTPAGE.RAW`.  This
  option is ignored in mode 3.


Output
======

The output is a list of JSON objects, normally one per input line.  Consecutive
input lines that are equal in all but the definition field are merged together
into one entry and their definitions concatenated (after removing leading
vertical bars).

All input fields that consist of abbreviations or single-letter codes are
converted to `{"code": ... , "value": ... }` objects on output, with the
`"code"` field being the abbreviation or code and the `"value"` field being a
human-readable representation thereof.  Codes of `X` (representing an unknown
or generic value) are always mapped to a value of `null`.

The following code-value mappings are used by multiple classes:

Cases:

    `code` | `value`
    ------ | ----------
    NOM    | nominative
    GEN    | genitive
    DAT    | dative
    ACC    | accusative
    ABL    | ablative
    VOC    | vocative
    LOC    | locative


Numbers:

    `code` | `value`
    ------ | ----------
    S      | singular
    P      | plural
    X      | `null`

Genders:

    `code` | `value`
    ------ | ---------
    M      | masculine
    F      | feminine
    N      | neuter
    C      | common
    X      | `null`


All Entries
-----------

All entries have the following fields:

- `abbreviation` — true iff the entry is for an abbreviation (in which case
  `base_forms` will contain only a single element)
- `age` — a code-value object for the time period in which the word was used;
  see <http://archives.nd.edu/whitaker/wordsdoc.htm#AGE> for more information
- `area` — a code-value object for the area of study in which the word was
  used; see <http://archives.nd.edu/whitaker/wordsdoc.htm#AREA> for more
  information
- `base_forms` — a list of strings giving the base forms of the word (for
  verbs, the principal parts; for nouns, the nominative & genitive; etc.)
- `class` — a code-value object for the word's part of speech:

    `code` | `value`
    ------ | ----------------
    ADJ    | adjective
    ADV    | adverb
    CONJ   | conjunction
    INTERJ | interjection
    N      | noun
    NUM    | number
    PACK   | PACKON (see below)
    PREP   | preposition
    PRON   | pronoun
    V      | verb

- `definition` — a string of semicolon-separated definitions of the word
- `freq` — a code-value object for how frequently the word was used; see
  <http://archives.nd.edu/whitaker/wordsdoc.htm#FREQ> for more information
- `geo` — a code-value object for the region in which or about which the word
  was used; see <http://archives.nd.edu/whitaker/wordsdoc.htm#GEO> for more
  information
- `inflected` — true iff the entry is for a word inflected into a specific
  (usually irregular) case/tense/etc. (in which case `base_forms` will contain
  only a single element)
- `source` — a code-value object for the reference work from which the entry
  was taken; see <http://archives.nd.edu/whitaker/wordsdoc.htm#SOURCE> for more
  information
    - The "A" and "J" sources (which have no meaning assigned to them) are
      mapped to the value `null`.
- `uninflectable` — true iff the word has only one form in all
  cases/tenses/etc. that does not change when inflected (in which case
  `base_forms` will contain only a single element)


Nouns
-----

Noun entries may have zero or more of the following fields:

- `declension` — an integer from 1 to 5 giving the declension of the noun under
  the traditional numbering
- `gender` — a code-value object for the noun's gender; see the table above for
  possible values

When `inflected` is true, a noun entry will also have the following fields:

- `case` — a code-value object for the case of the entry; see the table above
  for possible values
- `number` — a code-value object indicating whether the entry is singular or
  plural; see the table above for possible values
- `variant` — an integer giving the declension subdivision that the noun
  belongs to under a custom system specific to Whitaker's Words


Verbs
-----
Verb entries may have zero or more of the following fields:

- `conjugation` — an integer from 1 to 4 giving the conjugation of the verb
  under the traditional numbering, or 5 for a special custom conjugation
  specific to Whitaker's Words
- `type` — a code-value object indicating the type of verb or how it is used:

    `code`  | `value`
    ------- | ----------------
    ABL     | w/ablative
    DAT     | w/dative
    DEP     | deponent
    IMPERS  | impersonal
    INTRANS | intransitive
    PERFDEF | perfect definite
    SEMIDEP | semideponent
    TRANS   | transitive

When `inflected` is true, a verb entry will also have the following fields:

- `mood` — a code-value object for the mood or general type of form of the
  entry:

    `code` | `value`
    ------ | ----------------
    IMP    | imperative
    IND    | indicative
    INF    | infinitive
    PPL    | participle
    SUB    | subjunctive
    X      | `null`

- `number` — a code-value object indicating whether the entry is singular or
  plural; see the table above for possible values

- `person` — an integer from 1 to 3 indicating the person of the entry, or 0 if
  the person property does not apply (e.g., for infinitives)

- `tense` — a code-value object indicating the tense of the entry:

    `code` | `value`
    ------ | --------------
    PRES   | present
    IMPF   | imperfect
    FUT    | future
    PERF   | perfect
    PLUP   | pluperfect
    FUTP   | future perfect
    X      | `null`

- `variant` — an integer giving the conjugation subdivision that the verb
  belongs to under a custom system specific to Whitaker's Words

- `voice` — a code-value object indicating the voice of the entry:

    `code`  | `value`
    ------- | -------
    ACTIVE  | active
    PASSIVE | passive


Adjectives
----------
Adjective entries may have zero or more of the following fields:

- `comparative` — a list of strings giving the base forms of the comparative
  degree of the adjective
- `gender` — for single-gender adjectives, the gender in which the adjective is
  used; see the table above for possible values
- `gen_ius` — true if the adjective takes the ending `-ius` in the genitive
  singular
- `superlative` — a list of strings giving the base forms of the superlative
  degree of the adjective

Prepositions
------------
Preposition entries have the following field:

- `case` — the case of the object of the preposition; see the table above for
  possible values

Adverbs
-------
Adverb entries may have zero or more of the following fields:

- `comparative` — a list of one string giving the comparative degree of the
  adverb
- `superlative` — a list of one string giving the superlative degree of the
  adverb

Numbers
-------
Number entries may have zero or more of the following fields:

- `distributive` — a list of strings giving the base forms of the [distributive
  form](https://en.wikipedia.org/wiki/Distributive_number) ("_n_ each", "_n_ at
  a time") of the number
- `adverb` — a string giving the numeral adverb form ("_n_ times") of the
  number.  Note that, for many numbers, the numeral adverb may end in either
  "`-iens`" or "`-ies`", and this is represented by ending the string with
  "`-ie(n)s`" (e.g., `"centie(n)s"`).
- `ordinal` — a list of strings giving the base forms of the [ordinal
  form](https://en.wikipedia.org/wiki/Ordinal_number_(linguistics)) of the
  number

Pronouns and "PACKONs"
----------------------
"PACKONs" are a custom part of speech specific to the implementation of
Whitaker's Words consisting of a pronoun compounded with another word.
This script treats them the same way it treats pronouns.

Pronoun/PACKON entries may have zero or more of the following fields:

- `genitive` — true if the pronoun is genitive

- `type` — a code-value object indicating the type of pronoun:

    `code` | `value`
    ------ | -------------
    ADJECT | adjectival
    DEMONS | demonstrative
    INDEF  | indefinite
    INTERR | interrogative
    PERS   | personal
    REFLEX | reflexive
    REL    | relative
    X      | `null`

When `inflected` is true, a pronoun/PACKON entry will also have the following
fields:

- `case` — a code-value object for the case of the entry; see the table above
  for possible values
- `declension` — an integer giving the declension of the pronoun under a custom
  system specific to Whitaker's Words
- `gender` — a code-value object for the noun's gender
- `number` — a code-value object indicating whether the entry is singular or
  plural; see the table above for possible values
- `variant` — an integer giving the declension subdivision that the pronoun
  belongs to under a custom system specific to Whitaker's Words
