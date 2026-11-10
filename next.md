# Next action

1. Build read-only monitoring adapter and mock inventory events; separate scheduling ticks from network polling.
2. Define configurable active-window polling with exponential backoff on 429/5xx, jitter and rate caps; no aggressive retry outside authorized limits.
3. Persist session and purchase idempotency state; add tests.
4. Secure Pi deployment and visible-browser end-to-end testing.
5. Investigate checkout feasibility and implement explicit safeguards before purchase is enabled.

No headless browser testing. No real network purchases enabled.
