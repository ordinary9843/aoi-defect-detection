# fix — examples

Use when correcting broken or incorrect behavior.

## Good

```
fix: prevent crash when user list is empty
fix: correct off-by-one in pagination logic
fix: handle null response from auth API
fix: remove duplicate entry in nav menu
fix: resolve race condition in file upload
```

## Bad

```
fix: bug fix                   ← no information
fix: fixed it                  ← past tense
fix: some issues               ← vague
hotfix                         ← missing type prefix
```

## When to Use a Body

Only when the root cause is non-obvious and someone reading the commit later would be confused without it.

```
fix: prevent infinite loop in retry handler

Retry count was not being decremented when the request timed out
(as opposed to returning an error), causing infinite retries.
```
