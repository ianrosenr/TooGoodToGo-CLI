# Next action

1. Execute unit tests, resolve failures and verify dashboard in visible browser.
2. Integrate selection/reservations with a deterministic checkout simulator; ensure atomic SQLite BEGIN IMMEDIATE and idempotent purchase state.
3. Add daily spend/quantity progress and remaining budget to dashboard.
4. Research supported TGTG inventory APIs and rate limits before any real requests.
5. Build guarded checkout only after confirming supported payment/authorization mechanisms.
