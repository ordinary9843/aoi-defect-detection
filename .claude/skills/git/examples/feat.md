# feat — examples

Use when adding new functionality that didn't exist before.

## Good

```
feat: add user login page
feat: support dark mode toggle
feat: integrate stripe payment flow
feat: add csv export to report page
feat: allow multiple file upload
```

## Bad

```
feat: added new stuff          ← too vague
feat: Login                    ← not imperative, not lowercase
feat: implement the new feature that allows users to upload multiple files at once and also supports drag and drop  ← too long
new feature                    ← missing type prefix
```

## Borderline Cases

If the change is more about wiring up an existing library than writing new logic, `chore` may be more accurate than `feat`.

```
chore: install and configure react-query   ← setup only, no feature exposed yet
feat: add infinite scroll using react-query ← feature now visible to user
```
