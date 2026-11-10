# Project context

## Goal
Raspberry Pi 5 dashboard for scheduled Too Good To Go bag monitoring and prioritized checkout, subject to payment feasibility and safeguards.

## Merged
- PR #1: SQLite-backed local-only dashboard, desktop priority drag and arrow controls, time inputs, enable switches.
- PR #2: scheduler state transitions and regression tests (not independently executed in this chat).

## Current work
- Mobile touch pointer-based reorder prototype; existing up/down buttons remain as accessible fallback.
- Visible browser manual testing required; no headless browser.

## Constraints
- Medium thinking for implementation and review.
- Dashboard currently localhost-only; do not expose publicly.
- No TGTG network monitoring or purchase wired yet; never store CVV/payment secrets.
- Update context.md and next.md with each merge.
