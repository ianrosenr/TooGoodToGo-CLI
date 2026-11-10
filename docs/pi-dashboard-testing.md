# Raspberry Pi dashboard development testing

This is a **local-only prototype**. No purchase, monitoring API or payment operations are connected.

Run `python pi_dashboard.py` from the repository root, then open **http://127.0.0.1:8765** in a normal, visible browser. The browser is **not headless**.

Run `python -m pytest tests/test_pi_dashboard.py` to check the scheduler. Browser interaction should be tested manually in a visible Chrome/Safari window; no automated browser harness is configured yet.

Test adding bags, editing time, enabling/disabling, desktop dragging and up/down controls. Mobile touch dragging is pending. Do not expose port 8765 to the public internet.

The current scheduler runs only when the bag list is requested, and the 5-minute session is an initial prototype. A proper background scheduler and persisted next-run state are still required before unattended deployment.
