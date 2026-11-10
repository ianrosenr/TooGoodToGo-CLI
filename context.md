# Project context

Raspberry Pi Too Good To Go prototype. Offline-only simulator; no live inventory, reservation, or payment.

PRs #14 and #15 merged after GitHub CI passed. Dashboard offers manual daily arming, scheduling, priority ordering, dollar/bag caps, simulated observations, purchase summaries and simulated history.

Current branch adds startup recovery of pending *simulated* reservations and a systemd unit with persistent SQLite state and loopback-only access. Requires CI and real Pi validation.

Safety: no unattended real checkout. Future live API work requires authorization, rate-limit review and explicit testing.

Current work: show last simulated check timestamp and availability per bag. This proves only that the offline simulation ran, not that TGTG was contacted.
