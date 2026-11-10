# Next action

1. Run pytest and review current scheduler fix; repair any failing cases.
2. Implement reliable persistent scheduler state (including missed sessions/restarts, timezone/DST and daily rearming).
3. Implement touch-friendly priority dragging with keyboard accessibility.
4. Add schedule weekdays/windows and SQLite migration.
5. Add secure Pi service deployment and authentication.
6. Integrate read-only monitoring with simulation, then evaluate checkout and payment safeguards.
7. Add notifications, store import, browser-visible integration testing.

All browser-based testing must run in a visible (non-headless) browser. Never merge changes without passing checks and review.
