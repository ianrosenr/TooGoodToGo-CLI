# Project context

## Goal
Raspberry Pi TGTG bag dashboard with manually armed per-day monitoring windows and guarded purchase.

## Merged
PR #1 dashboard; #2 scheduler tests; #3 touch reorder; #4 configurable schedules; #5 background scheduler; #6 250ms local scheduler tick.

## Current PR
- Explicit arm_date per bag; new and migrated bags default off.
- Arming during today's remaining window monitors today; arming after window schedules next eligible day.
- Window expiry disables; no automatic rearming.
- Purchase-confirmed permanent disable still requires checkout integration.
- No TGTG event API verified. Polling policy must honor limits.
- Existing regression tests require updates to reflect new manual-arming semantics; not yet validated.

## Constraints
Visible non-headless browser testing, no unauthorized remote access, no stored payment credentials.
