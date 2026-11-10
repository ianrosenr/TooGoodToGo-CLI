# Project context

## Goal
Raspberry Pi TGTG bag dashboard with manual daily arming, narrow monitoring windows, priority and guarded checkout.

## Merged
PR #1 dashboard; #2 scheduler tests; #3 touch reorder; #4 configurable windows; #5 background scheduler; #6 250ms local tick; #7 manual daily arming.

## Current PR
- Read-only availability adapter protocol, deterministic offline simulation and global poll gate with backoff.
- No remote TGTG requests, no checkout, no actual monitoring integration yet.
- Unit tests authored but not executed; visible browser testing pending.

## Constraints
No automatic rearming. Missed windows disable. Confirmed purchase must disable until manually rearmed. Respect provider rate limits; no remote access without authentication.
