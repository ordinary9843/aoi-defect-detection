# style — examples

Use when changes are purely cosmetic: formatting, whitespace, linting fixes, import ordering. Zero logic change.

## Good

```
style: apply prettier formatting across src/
style: fix eslint warnings in user module
style: reorder imports to match lint rules
style: remove trailing whitespace
style: normalize quote style to single quotes
```

## Bad

```
style: cleanup                 ← vague
style: small fixes             ← could be anything
style: format and fix null bug ← mixing style with fix, split into two commits
```

## Distinguish from refactor

- `style` = only whitespace, formatting, or linting — no structural change, tests unaffected
- `refactor` = renamed variables, extracted functions, reorganized logic — tests may need updating
