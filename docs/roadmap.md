# Next milestones

The dashboard currently supports **offline simulated monitoring and checkout only**. A simulated “Last checked” indicator does **not** mean a live Too Good To Go listing was contacted. Do not enable real checkout or payment without verifying feasibility and authorization.

## 1. Deploy on Raspberry Pi

- Install Python dependencies in a virtual environment on the Raspberry Pi 5.
- Configure the `deploy/tgtg-dashboard.service` systemd unit, writable persistent SQLite directory, and environment file.
- Enable startup on boot and confirm automatic recovery after restart.
- Access the dashboard via an SSH tunnel using a normal SSH login account; keep the HTTP server bound to `127.0.0.1`, never expose port 8765 publicly.
- Verify service logs, filesystem permissions, and configuration.

**Done when:** dashboard is accessible from the Mac and survives reboot with all saved settings.

## 2. Run end-to-end simulation

- Add bags with prices, drop times, monitoring windows, and schedules.
- Arm each bag manually; verify the dashboard shows “Last checked” only after a simulated check.
- Verify availability transitions, unavailable results, and dashboard refresh.
- Confirm priority-first budget behavior: with $15 and two-bag caps, $10/$7/$4 bags select $10 and $4.
- Verify expiry, restart recovery, and no duplicate simulated reservations.
- Test the dashboard in a visible browser and on the Pi.

**Done when:** tests and manual scenarios pass without any network or payment activity.

## 3. Implement read-only live listing monitoring

- On the Mac, inspect authorized app traffic with Proxyman and sanitize credentials, cookies, and personal data before sharing examples.
- Identify a supported or otherwise permitted read-only listing/availability interface and its authentication and rate-limit requirements.
- Implement a separately configured live adapter with conservative polling, backoff, credential protection, and no purchase calls.
- Clearly label simulated versus live checks; display last successful check, availability, errors, and stale status.

**Done when:** an actual listing can be observed safely and reliably, without checkout.

## 4. Verify live behavior

- Confirm listing identity and mapping, availability changes, authentication failures, rate limits, and transient network failures.
- Confirm that failed requests never appear as successful “listing seen” checks.
- Verify restart behavior, logs, and monitoring freshness on the Pi.

**Done when:** live status is accurate, observable, and failure-safe.

## 5. Investigate checkout separately

- Determine whether reservation and checkout automation is technically supported and allowed under applicable terms.
- Document payment and cancellation requirements and safeguards before proposing implementation.
- Keep real purchase/payment operations disabled until explicitly approved and tested.

**Done when:** there is a documented go/no-go decision and safe design, not an assumed ability to buy.

## Release rules

- Implement each milestone in a focused PR with regression tests and updated `context.md` / `next.md`.
- Review changes and merge only after all required CI checks pass.
- Never present simulated observations or reservations as real TGTG activity.
