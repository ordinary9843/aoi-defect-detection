# refactor — examples

Use when restructuring existing code without changing its external behavior or adding new functionality.

## Good

```
refactor: extract payment logic into service class
refactor: simplify user validation flow
refactor: replace callback chain with async/await
refactor: move config values to constants file
refactor: rename userInfo to userProfile for clarity
```

## Bad

```
refactor: refactored code          ← circular, no info
refactor: cleanup                  ← too vague
refactor: misc changes             ← not a real refactor
```

## Distinguish from style

- `refactor` changes structure, names, or logic organization — tests might need updating
- `style` is pure formatting (spaces, line breaks, linting) — no logic touched at all

```
style: apply prettier formatting across src/
refactor: split UserController into Auth and Profile controllers
```
