# Project context

## Goal
Raspberry Pi 5 hosted Too Good To Go bag watchlist, prioritized mobile dashboard and scheduled monitoring. Existing Python CLI remains the integration baseline; avoid premature Rust rewrite.

## Current state
- PR #1 merged: local-only Python/SQLite prototype dashboard, desktop drag ordering, up/down controls, daily time, enable switches, five-minute timeout.
- No TGTG network monitoring, guest checkout, Apple Pay, or purchase capability wired into dashboard.
- Security: dashboard currently binds localhost; no authentication. Do not expose publicly.
- Payment: no stored card data/CVV. Checkout must remain disabled until feasibility, consent, and safeguards are validated.
- Compliance: unofficial integration may conflict with Too Good To Go terms.

## Engineering workflow
- One scoped issue per PR; implementation assigned to lower-thinking/cost-efficient agents where available.
- Higher-thinking review for correctness, security, payments, concurrency and architecture.
- Run tests/lint before merge; fix review findings; update context.md and next.md in every PR.
- Merge only after review and passing checks; never assume tests passed.
- No actual subagent execution is currently available in this chat; GitHub issues are the delegation queue.

## Risks / known gaps
- Existing timeout logic may expire a newly enabled bag outside the intended session; fix first.
- iPhone drag sorting not yet supported.
- No persistent task runner in ChatGPT session.
