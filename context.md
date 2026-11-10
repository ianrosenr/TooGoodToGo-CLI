# Project context

## Goal
Raspberry Pi 5 dashboard for prioritized scheduled Too Good To Go bag monitoring and guarded checkout.

## Merged
- PR #1: local-only SQLite dashboard.
- PR #2: scheduler state transition regression tests (not independently executed).
- PR #3: touch pointer reorder, desktop drag and up/down fallback.

## Current PR
- Configurable window duration (1-120 minutes), weekdays/weekends/every day, SQLite migration for existing databases.
- Prototype still depends on GET /api/bags to evaluate sessions; not a background monitor.
- Tests and visible browser validation pending.

## Constraints
Medium thinking; visible non-headless browser tests. No purchase/credentials currently connected. Keep local-only until authenticated and secured. Every PR updates context.md and next.md.
