# Project context

## Goal
Raspberry Pi Too Good To Go dashboard: manual daily arming, priority ordering, narrow monitoring windows, optional daily spend and bag caps, and guarded checkout.

## Merged
PR #1–#9: local dashboard, scheduler, touch reorder, configurable windows, manual daily arming, offline availability simulation and observation history.

## Current PR
- Editable bag prices and independent optional daily max dollars / max bags in dashboard.
- Integer cents; priority-first selection skips unaffordable bags (e.g. $10, $7, $4 with $15/2 caps selects #1 and #3).
- Pending and confirmed reservations count against limits; reservation helper available but not yet connected to any checkout.
- No real TGTG API or purchases. Tests authored but not executed.
- Changing limits below existing reservations must not authorize more spending; existing reservations remain and should be surfaced.

## Constraints
No automatic rearming. Missed windows disable. Confirmed purchase disables until manually rearmed. Respect rate limits and require secure dashboard access before network exposure.
