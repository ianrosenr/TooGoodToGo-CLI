# Next action

1. Run dashboard pytest suite and fix failures. Inspect GitHub Actions status.
2. Confirm repaired dashboard module imports and starts; test GET /api/limits, /api/purchase-summary, /api/purchase-history.
3. Add non-headless browser test of the mobile dashboard.
4. Harden simulated checkout: interrupted reservations, retry states and startup recovery.
5. Package Pi systemd service and documented secure access. Real API integration remains blocked.
