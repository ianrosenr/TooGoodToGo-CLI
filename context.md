# Project context

## Goal
Raspberry Pi 5 prioritized bag dashboard, precise schedules and guarded checkout.

## Merged
- PR #1 dashboard; #2 scheduler tests/state; #3 touch priority; #4 schedules/windows; #5 independent background scheduler.

## Current PR
- Local scheduler tick defaults to 250ms, configurable with TGTG_SCHEDULER_TICK_SECONDS (0.05–60 seconds).
- This is **local scheduling only**, not Too Good To Go inventory polling.
- Future inventory polling needs rate-limit/backoff and terms review; default proposal 1s only while active, adjustable based on observed limits.
- Immediate purchase event handling still unimplemented.

## Constraints
Medium thinking, non-headless browser tests, no unauthenticated remote access, no stored payment secrets. Every PR updates context.md and next.md.
