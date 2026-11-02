# Reproducible release simulation

Actual branch/tag history is embedded in `.git` and available through `git log --all`.

1. `main`: initial repository scaffold.
2. `develop`: integration branch derived from `main`.
3. `feature/booking-hold`: hold behavior and conflict tests; merge to `develop`.
4. `feature/idempotency`: replay safety; merge to `develop`.
5. `release/0.1.0`: CI and changelog; merge to `main`; annotated tag `v0.1.0`.
6. Sync `main` back into `develop`.
7. `hotfix/confirm-deadline`: fix confirm at exact expiration instant, add regression test;
   merge into `main` and tag `v0.1.1`.
8. Sync `main` back into `develop` and verify ancestry.

We intentionally leave the feature, release and hotfix branches visible for university defense.
They are normally deleted after successful merge in a standard GitFlow routine.

## Safety and scope

The `v0.1.0` release contains an **intentional boundary defect** at `now == expires_at`
that was discovered in the simulated post-release phase. Version `v0.1.1` addresses it.
The lab simulates Git release flow and unit-level quality gates; no production infrastructure,
real payments, browser-based PR approvals or live GitHub Actions runs are represented as done.

## Verify the hotfix

```bash
git show v0.1.0:src/driveeasy/booking.py | grep 'now > booking.expires_at'
git show v0.1.1:src/driveeasy/booking.py | grep 'now >= booking.expires_at'
git merge-base --is-ancestor v0.1.1 develop && echo synced
```
