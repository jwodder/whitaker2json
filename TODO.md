- Add the ability to convert `DICTLINE.GEN` to JSON
- Add a JSON Schema for the output format?
- Add an option for specifying the maximum field width? (currently 24; used for
  determining when abbreviated endings may have been truncated)
- Make a gh-pages site (or GitHub wiki?) describing the formats of Words'
  datafiles, including declension/conjugation variant numbers
- Allow any letter as an area/geo/etc. flag with unknowns mapped to `null`?
- Use warnings for things currently written straight to stderr?

- Improve output format:
    - Rename "uninflectable" and "inflected" to something less likely to cause
      confusion
    - Rename pronouns' `genitive` field so as not to conflict with adjectives'
      `genitive` field?
    - Give each nontrivial word named fields for each element of `base_forms`?
      (Keep `base_forms`, though)
