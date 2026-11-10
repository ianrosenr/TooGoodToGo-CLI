# Project context

## Goal
Raspberry Pi 5 dashboard for scheduled Too Good To Go bag monitoring and prioritized checkout, subject to payment feasibility and safeguards.

## Merged
- PR #1: SQLite-backed local-only dashboard, desktop priority drag and arrow controls, time inputs, enable switches. No checkout.

## Current PR
- Scheduler regression tests and session-state fix; visible browser manual testing instructions.
- No automated visible-browser tests yet; not executed on Raspberry Pi.

## Constraints
- Use medium thinking for implementation and review.
- Do not expose unauthenticated localhost dashboard publicly.
- Never store CVV or payment secrets; no unattended purchase without validation and explicit guardrails.
- Every PR updates context.md and next.md; review and run checks before merge.
- This chat does not have autonomous subagent execution or continuous unattended iteration.
