- Be able to handle all entries currently in `DICTPAGE.RAW`
- Entries that are currently not handled correctly:
    - `#colossicon  N ADJ`
    - `#curotrophoe F ADJ`
- Add the ability to convert `DICTLINE.GEN` to JSON
- Write a README
- Add a JSON Schema for the output format?
- Make sure the code is compatible with both Python 2 and Python 3
- Find a better term for "parts"
- Should the "(gen.)" in adjective headers be preserved somehow?
- Add an option for specifying the maximum field width? (currently 24; used for
  determining when abbreviated endings may have been truncated)
- Exit with a failure status if any lines were unparseable
- Rename "inflectable" and "inflected" to something less likely to cause
  confusion
- Add fancy error checking & error messages for malformed inflected word
  entries
- Make a gh-pages site describing the formats of Words' datafiles, including
  declension/conjugation variant numbers
- Make "numeral adverb" a string instead of a list?
- For adjectives & adverbs, merge "parts", "comparative", and "superlative"
  into a single `"parts": {"positive": ..., "comparative": ..., "superlative":
  ...}` field?
    - Do the same for numbers?
