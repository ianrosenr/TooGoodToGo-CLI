# Next action

## Priority 1
Fix dashboard session lifecycle and add automated tests (see GitHub issue queue).

### Acceptance
- Do not time out a bag before its next scheduled drop window.
- Re-arm semantics are explicit; restarts preserve state.
- Tests cover before/within/after windows, timezone and DST, persistence.
- No network checkout calls or payment data.
- Update context.md and next.md in PR; review and run checks before merge.

## After
Mobile touch reorder, per-bag weekdays/windows, secure Raspberry Pi deployment, monitoring simulation, guest-checkout feasibility, then guarded payment integration.

## Agent policy
Use low-thinking implementation workers for bounded coding tasks; stronger independent reviewer for safety, concurrency and payment paths. Do not claim agents were spawned unless a runtime actually executed them.
