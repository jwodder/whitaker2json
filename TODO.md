- Add the ability to convert `DICTLINE.GEN` to JSON
- Add a JSON Schema for the output format?
- Add an option for specifying the maximum field width? (currently 24; used for
  determining when abbreviated endings may have been truncated)
- Make a gh-pages site (or GitHub wiki?) describing the formats of Words'
  datafiles, including declension/conjugation variant numbers
- Use warnings for things currently written straight to stderr?

- Improve output format:
    - Rename "uninflectable" (to "invariable"?) and "inflected" to something
      less likely to cause confusion
    - Give each nontrivial word named fields for each element of `base_forms`?
      (Keep `base_forms`, though)
    - Always include all of the fields defined for a class in its entries?
