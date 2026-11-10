# Project context

Raspberry Pi Too Good To Go prototype. Offline-only simulator, no live inventory, reservation, or payment.

Merged PRs #1–#12: manual arming, scheduler, offline observations, simulated checkout, spend/quantity caps, CI workflow and write transaction hardening.

Current PR:
- Repairs severe pi_dashboard.py duplication (eight concatenated implementations).
- Adds remaining daily dollars/bags to dashboard and simulated purchase history API.
- Requires CI and runtime tests before merge. GitHub workflow success has not been confirmed.

Safety: manual rearming each day, no unattended real checkout. Need API authorization and rate-limit review.
