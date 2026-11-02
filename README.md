# DriveEasy — SDLC & GitFlow Lab (RPIS №3)

Educational release simulation for the DriveEasy car rental system (variant 13).

This repository contains a **small in-memory booking model**, not a production car-rental platform.
It demonstrates the key invariants from LR1 and LR2:

- FR-04 / SM-02: do not allocate overlapping intervals to one car.
- FR-34 / SM-15: temporary holds expire after 15 minutes.
- FR-35: a hold can be confirmed only after successful payment.
- NFR-07 / SM-04: repeated requests have a single business effect.

**Scope and limitations:** An `RLock` protects this model in a single Python process; it is not a
substitute for PostgreSQL constraints/transactions across multiple application instances.
There is no real payment gateway, persistence, telemetry, or production deployment.
All sample release history is a documented **lab simulation**.

## Run tests

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q
ruff check .
ruff format --check .
```

## Branching strategy

See `docs/BRANCHING.md` and `docs/RELEASE_WORKFLOW.md` for the exact branch/merge order.
See Git history with:

```bash
git log --all --graph --oneline --decorate
```

Release tags `v0.1.0` and `v0.1.1` are **actual annotated Git tags**, not files.
