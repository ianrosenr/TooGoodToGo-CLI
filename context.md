# Project context

## Goal
Raspberry Pi 5 prioritized bag watchlist with scheduled monitoring and guarded checkout.

## Merged
- PR #1: local SQLite dashboard.
- PR #2: session state fixes and regression tests.
- PR #3: mobile pointer priority reorder.
- PR #4: daily/weekday/weekend schedules and configurable windows; custom-window timeout fix.

## Current PR
- Independent background scheduler tick every five seconds, with transaction commit and error isolation.
- No Too Good To Go network monitoring or purchase integration.
- Restart-safe schedule occurrence persistence, DST handling, and complete tests still pending.
- No visible browser test executed in this chat.

## Constraints
Medium thinking; visible non-headless browser testing only. No unauthenticated remote exposure, no stored payment secrets. Every PR updates context.md and next.md.
