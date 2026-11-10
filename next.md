# Next action

1. Execute tests and inspect the live dashboard with a visible, non-headless browser.
2. Add secure read-only real inventory adapter only after investigating supported APIs and provider rate limits.
3. Separate remote polling from 250ms local scheduler; use a shared rate gate and Retry-After.
4. Add notifications and purchase-confirmed permanent disable with idempotency safeguards.
5. Secure Pi deployment, mobile access and checkout feasibility.
