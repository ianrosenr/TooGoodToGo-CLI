# Next action

1. Run pytest and validate browser UI with visible non-headless browser; fix regressions.
2. Implement SQLite BEGIN IMMEDIATE transaction boundary for future concurrent checkout workers.
3. Improve event history: record every availability transition and prevent stale availability.
4. Add mock checkout failure/retry and pending reservation reconciliation.
5. Research supported TGTG inventory/payment flows and rate limits; secure Pi deployment.
