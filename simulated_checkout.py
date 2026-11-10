"""Offline-only purchase simulation and idempotent state transitions."""
from datetime import datetime

from purchase_limits import reserve_bag


def simulate_checkout(db, now: datetime):
    """Select currently available, watching bags by priority and confirm locally.

    Caller must hold the dashboard lock and an SQLite write transaction.
    Never contacts payment services. A confirmation is SIMULATED only.
    """
    day = now.date().isoformat()
    candidates = db.execute("""
        SELECT b.id,b.arm_date FROM bags b
        JOIN observations o ON o.bag_id=b.id AND o.arm_date=b.arm_date
        WHERE b.enabled=1 AND b.status='watching' AND o.available=1
          AND o.id=(SELECT MAX(o2.id) FROM observations o2
                    WHERE o2.bag_id=b.id AND o2.arm_date=b.arm_date)
        ORDER BY b.priority,b.id
    """).fetchall()
    confirmed = []
    for bag in candidates:
        if not reserve_bag(db, bag["id"], day):
            continue
        db.execute(
            "UPDATE purchase_reservations SET state='confirmed' "
            "WHERE bag_id=? AND purchase_day=? AND state='pending'",
            (bag["id"], day),
        )
        db.execute(
            "UPDATE bags SET enabled=0,status='simulated_purchased' WHERE id=?",
            (bag["id"],),
        )
        confirmed.append(bag["id"])
    return confirmed
