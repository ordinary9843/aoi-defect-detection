# chore — examples

Use for maintenance tasks that don't change production logic: dependency updates, config changes, tooling setup, project structure changes.

## Good

```
chore: first commit
chore: upgrade typescript to v5
chore: add .gitignore
chore: update node to v20
chore: remove unused dependencies
chore: add eslint config
chore: reorganize folder structure
chore: update env example file
```

## Bad

```
chore: stuff                   ← no info
chore: misc                    ← not descriptive
wip                            ← not a valid type, and not a commit message
chore: did some cleanup and also fixed a bug and updated some packages  ← multiple concerns, too long
```

## Note

`chore` is the most common type for project setup and the very first commit. Keep it honest — if the change actually touches business logic, it is `feat` or `fix`, not `chore`.
