# Project context

## Goal
Raspberry Pi TGTG dashboard with manual daily arming, priority, spend and quantity caps, safe monitoring, guarded checkout.

## Merged
PRs #1-#10: dashboard, local scheduler, touch reorder, configurable windows, manual arming, offline monitoring simulation, configurable purchase limits.

## Current PR
- Opt-in offline checkout simulation: set TGTG_SIMULATED_AVAILABLE_IDS=1,2 and TGTG_SIMULATE_CHECKOUT=1.
- Priority-first selection skips unaffordable bags, reserves daily budget, marks simulated purchases disabled, prevents duplicate checkout.
- Dashboard shows today's reserved/simulated totals and GET /api/purchase-summary.
- No payment or actual purchase. Tests authored but not executed.
- Reservation state must be committed atomically before any future real checkout.

## Constraints
Manual daily arming only; missed window disables; confirmed purchases disable until manually rearmed. Avoid real TGTG requests before verifying service constraints. Browser testing must be non-headless.
