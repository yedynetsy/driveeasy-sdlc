# Changelog

## [0.1.1] - 2026-11-02

- Fix exact deadline: `now >= expires_at` rejects confirmation.
- Add regression test for the critical expiration boundary.

## [0.1.0] - 2026-11-02

- Process-local reservation holds and half-open interval collision protection.
- Payment-gated confirmation, expiration cleanup, idempotency keys.
- CI lint, unit tests with coverage, and Python package build.

> Educational release candidate. Not a production deployment.
