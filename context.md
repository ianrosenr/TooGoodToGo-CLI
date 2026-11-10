# Project context

## Goal
Raspberry Pi TGTG bag dashboard with manually armed per-day monitoring windows, priority ordering and guarded checkout.

## Merged
PR #1 dashboard; #2 scheduler tests; #3 touch reorder; #4 configurable windows; #5 background scheduler; #6 250ms local tick; #7 manual daily arming; #8 offline availability adapter and poll gate.

## Current PR
- Optional offline simulated availability events integrated with scheduler.
- Set TGTG_SIMULATED_AVAILABLE_IDS to comma-separated local bag IDs to activate.
- Observations persisted once per bag/armed date/availability state, exposed at GET /api/observations.
- No real TGTG requests, payments, or purchase claims. Tests authored, not executed.
- Simulation currently checks locally on every scheduler tick; this is not the remote polling interval.

## Constraints
No automatic rearming. Missed windows disable. Confirmed purchase must disable until manually rearmed. Respect service rate limits. No exposed unauthenticated dashboard.
