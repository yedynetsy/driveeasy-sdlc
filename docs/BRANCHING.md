# Simplified GitFlow

| Branch | Source | Purpose | Merge destination |
| --- | --- | --- | --- |
| `main` | stable code | tagged release-ready state | — |
| `develop` | `main` | upcoming release integration | `release/*` is forked here |
| `feature/*` | `develop` | one self-contained change | `develop` (merge commit) |
| `release/*` | `develop` | release candidate, fixes, validation | `main`, then sync into `develop` |
| `hotfix/*` | `main` | urgent correction to published version | `main`, then sync into `develop` |

All merges in this lab use `--no-ff` so history visibly records the merge event.
Branches are intentionally retained as evidence instead of being deleted after merge.

> The lab builds a small in-memory model; the real DriveEasy would require PostgreSQL
> transactional constraints, payment orchestration, security checks and staging validation.

## Verification commands

```bash
git branch -avv
git tag -n
git log --all --graph --oneline --decorate
git merge-base --is-ancestor v0.1.1 develop && echo 'Hotfix propagated to develop'
```
