# docs — examples

Use when the only changes are to documentation, markdown files, comments, or README.

## Good

```
docs: update README setup instructions
docs: add API usage examples to SKILL.md
docs: fix typo in contributing guide
docs: document environment variables
docs: add examples for git commit types
```

## Bad

```
docs: updated docs              ← past tense, too vague
docs: documentation             ← no description
update readme                   ← missing type prefix
```

## Note

If a commit touches both code and documentation, use the type that reflects the primary change. A `feat` commit that also updates the README is still `feat`.
