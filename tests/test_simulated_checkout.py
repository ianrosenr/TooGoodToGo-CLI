"""Simulated checkout tests; no payment or network calls."""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from simulated_checkout import (
    recover_simulated_reservations,
    simulate_checkout,
)


def test_priority_skips_unaffordable_and_is_idempotent():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE bags (id INTEGER PRIMARY KEY, priority INTEGER, arm_date TEXT,
            enabled INTEGER, status TEXT, price_cents INTEGER);
        CREATE TABLE observations (id INTEGER PRIMARY KEY,bag_id INTEGER, arm_date TEXT, available INTEGER);
        CREATE TABLE purchase_limits (id INTEGER PRIMARY KEY, max_cents INTEGER, max_bags INTEGER);
        CREATE TABLE purchase_reservations (id INTEGER PRIMARY KEY, bag_id INTEGER,
            purchase_day TEXT, price_cents INTEGER, state TEXT,
            UNIQUE(bag_id,purchase_day));
        INSERT INTO purchase_limits VALUES(1,1500,2);
        INSERT INTO bags VALUES(1,1,'2026-11-09',1,'watching',1000);
        INSERT INTO bags VALUES(2,2,'2026-11-09',1,'watching',700);
        INSERT INTO bags VALUES(3,3,'2026-11-09',1,'watching',400);
        INSERT INTO observations(bag_id,arm_date,available) VALUES(1,'2026-11-09',1);
        INSERT INTO observations(bag_id,arm_date,available) VALUES(2,'2026-11-09',1);
        INSERT INTO observations(bag_id,arm_date,available) VALUES(3,'2026-11-09',1);
    """)
    now = datetime(2026, 11, 9, 12, 1, tzinfo=ZoneInfo("America/New_York"))
    assert simulate_checkout(db, now) == [1, 3]
    assert simulate_checkout(db, now) == []
    assert db.execute("SELECT COUNT(*) FROM purchase_reservations").fetchone()[0] == 2
    assert db.execute("SELECT enabled FROM bags WHERE id=2").fetchone()[0] == 1


def test_restart_recovers_pending_without_double_spending():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE bags (
            id INTEGER PRIMARY KEY, enabled INTEGER, status TEXT
        );
        CREATE TABLE purchase_reservations (
            id INTEGER PRIMARY KEY, bag_id INTEGER, purchase_day TEXT,
            price_cents INTEGER, state TEXT
        );
        INSERT INTO bags VALUES(1,1,'watching');
        INSERT INTO bags VALUES(2,1,'watching');
        INSERT INTO purchase_reservations
            VALUES(1,1,'2026-11-09',1000,'pending');
        INSERT INTO purchase_reservations
            VALUES(2,2,'2026-11-09',400,'confirmed');
    """)
    assert recover_simulated_reservations(db) == 1
    assert recover_simulated_reservations(db) == 0
    assert db.execute(
        "SELECT enabled,status FROM bags WHERE id=1"
    ).fetchone()[:] == (0, "simulated_purchased")
    assert db.execute(
        "SELECT SUM(price_cents) FROM purchase_reservations "
        "WHERE state IN ('pending','confirmed')"
    ).fetchone()[0] == 1400
