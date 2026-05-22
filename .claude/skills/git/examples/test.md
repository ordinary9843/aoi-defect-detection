# test — examples

Use when adding new tests or updating existing ones without changing production code.

## Good

```
test: add unit tests for payment service
test: cover edge case in empty cart scenario
test: update mock for updated user API response
test: add integration test for login flow
test: fix flaky timeout in upload test
```

## Bad

```
test: tests                    ← no info
test: added some tests         ← past tense, vague
test: wip                      ← not a commit message
```

## Note

If you fix a bug AND add a test for it in the same commit, use `fix` — the test is just part of the fix.

```
fix: prevent null crash in cart and add test coverage
```
