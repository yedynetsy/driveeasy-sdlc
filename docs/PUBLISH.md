# Publish the full Git history to your GitHub account

The local repo already contains all branches, merge commits and version tags.
Do NOT run `git init` again, and do NOT upload only the files without `.git` history.

## Method 1 — GitHub CLI (Mac)

```bash
# Install GitHub CLI if needed: brew install gh
gh auth login
cd driveeasy-sdlc
gh repo create driveeasy-sdlc --public --source=. --remote=origin

git push -u origin main
git push -u origin develop
git push origin feature/booking-hold feature/idempotency release/0.1.0 hotfix/confirm-deadline
git push origin v0.1.0 v0.1.1
```

## Method 2 — GitHub website

1. Create a new **empty** public `driveeasy-sdlc` repository (disable README/license/gitignore initialization).
2. In the local `driveeasy-sdlc` folder run:

```bash
git remote add origin https://github.com/YOUR_USER/driveeasy-sdlc.git
git push -u origin main
git push -u origin develop
git push origin feature/booking-hold feature/idempotency release/0.1.0 hotfix/confirm-deadline
git push origin v0.1.0 v0.1.1
```

Once pushed, inspect the Actions tab; until it runs, the workflow is only a configuration,
not proof of a completed GitHub Actions run. The Git graph in the archive is real local Git history.
