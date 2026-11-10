# Raspberry Pi local deployment (simulation only)

Install Python 3.12+ and uv on the Pi. Copy this repository to
`/opt/tgtg-dashboard` and install dependencies with `uv sync`.
Create a dedicated `tgtg` system user and ensure that user owns
`/opt/tgtg-dashboard`. The unit expects the virtual environment at
`/opt/tgtg-dashboard/.venv`.

Create `/etc/tgtg-dashboard.env` (root-owned, mode 0600):

```sh
TGTG_DASHBOARD_DB=/var/lib/tgtg-dashboard/bag-dashboard.sqlite3
TGTG_TIMEZONE=America/New_York
# Optional offline-only testing:
# TGTG_SIMULATED_AVAILABLE_IDS=1,3
# TGTG_SIMULATE_CHECKOUT=1
```

Install `deploy/tgtg-dashboard.service` to
`/etc/systemd/system/tgtg-dashboard.service`, then run:

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now tgtg-dashboard
sudo systemctl status tgtg-dashboard
journalctl -u tgtg-dashboard -f
```

The dashboard binds to **127.0.0.1:8765 only**. From your Mac, use an
SSH tunnel: `ssh -L 8765:127.0.0.1:8765 tgtg@PI_HOST`,
then open `http://127.0.0.1:8765` locally. Do not expose port 8765
to the internet: the dashboard has no authentication or TLS.

SQLite state survives restarts under `/var/lib/tgtg-dashboard`.
Pending *simulated* reservations are finalized locally on startup;
no real purchase or payment occurs.
