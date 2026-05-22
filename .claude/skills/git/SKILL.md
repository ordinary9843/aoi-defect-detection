---
name: git
description: "Enforce conventional git commit messages. Every change gets a single-line commit in the format <type>: <short description>. Types: feat, fix, docs, refactor, chore, test, style, ci. No multi-line messages unless body is strictly necessary."
---

# Git Commit Convention

> **Goal**: Every commit must have a short, single-line message in the format `<type>: <description>`. The description should be lowercase, imperative, and under 72 characters. No multi-line bodies unless the change genuinely cannot be understood without one.

## Format

```
<type>: <short description>
```

- **type**: one of the allowed prefixes (see below)
- **description**: imperative mood, lowercase, no period at end
- **length**: aim for under 50 chars, hard limit 72 chars

## Allowed Types

| Type | When to use |
|---|---|
| `feat` | adding new functionality |
| `fix` | fixing a bug or broken behavior |
| `docs` | changes to documentation or markdown files only |
| `refactor` | restructuring code without changing behavior |
| `chore` | maintenance tasks, config changes, dependencies |
| `test` | adding or updating tests |
| `style` | formatting, whitespace, naming — no logic change |
| `ci` | CI/CD pipeline or workflow changes |

## Rules

1. One commit per logical change — do not bundle unrelated changes
2. Single line only — no body, no footer unless strictly necessary
3. Lowercase description — `feat: add login page` not `feat: Add Login Page`
4. Imperative mood — `fix: remove null check` not `fixed` or `fixes`
5. No vague messages — `chore: update` is bad, `chore: update node to v20` is good

## When a Body IS Acceptable

Only when the "why" cannot be inferred from the type + description alone. Keep it to 1–2 sentences. Leave one blank line between subject and body.

```
fix: handle empty response from payment API

Stripe returns 204 with no body on some edge cases; previous
code crashed on JSON.parse of an empty string.
```

## Examples

See `examples/` for good and bad examples per type:
- examples/feat.md
- examples/fix.md
- examples/docs.md
- examples/refactor.md
- examples/chore.md
