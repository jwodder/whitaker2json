- Add the ability to convert `DICTLINE.GEN` to JSON
- Write a README
- Add a JSON Schema for the output format?
- Find a better term for "parts"
- Should the "(gen.)" in adjective headers be preserved somehow?
- Add an option for specifying the maximum field width? (currently 24; used for
  determining when abbreviated endings may have been truncated)
- Exit with a failure status if any lines were unparseable
- Rename "inflectable" and "inflected" to something less likely to cause
  confusion
- Make a gh-pages site describing the formats of Words' datafiles, including
  declension/conjugation variant numbers
- Make "numeral adverb" a string instead of a list?
- For adjectives & adverbs, merge "parts", "comparative", and "superlative"
  into a single `"parts": {"positive": ..., "comparative": ..., "superlative":
  ...}` field?
    - Do the same for numbers?
- Allow any letter as an area/geo/etc. flag with unknowns mapped to `null`?
- Use warnings for things currently written straight to stderr?
