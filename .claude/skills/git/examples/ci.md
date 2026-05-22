# ci — examples

Use when changes are only to CI/CD pipelines, workflows, or deployment configuration. No production code touched.

## Good

```
ci: add GitHub Actions workflow for lint and test
ci: fix failing deploy step on main branch
ci: cache node_modules in CI pipeline
ci: update deploy target to production
ci: add Docker build step to release workflow
```

## Bad

```
ci: ci stuff                   ← no info
ci: pipeline                   ← not descriptive
ci: update workflow and fix bug ← mixing ci with fix, split into two commits
```

## Note

If a change touches both app code and CI config (e.g., adding a new script and wiring it into GitHub Actions), use the type that reflects the app-side change, not `ci`.

```
feat: add lint script and wire into CI
```
