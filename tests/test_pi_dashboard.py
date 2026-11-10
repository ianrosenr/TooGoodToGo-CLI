"""Regression tests for the standalone Raspberry Pi dashboard."""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from pi_dashboard import expire_sessions, list_bags

TZ = ZoneInfo("America/New_York")


def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE bags (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, drop_time TEXT NOT NULL,
        priority INTEGER NOT NULL, enabled INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'armed', last_session TEXT)""")
    conn.execute("INSERT INTO bags(name,drop_time,priority) VALUES ('Test','12:00',1)")
    return conn


def test_new_bag_does_not_expire_after_window():
    conn = db()
    expire_sessions(conn, datetime(2026, 11, 9, 14, 0, tzinfo=TZ))
    assert list_bags(conn)[0]["enabled"]


def test_enters_watching_during_window():
    conn = db()
    expire_sessions(conn, datetime(2026, 11, 9, 12, 1, tzinfo=TZ))
    assert list_bags(conn)[0]["status"] == "watching"


def test_watching_expires_after_window():
    conn = db()
    expire_sessions(conn, datetime(2026, 11, 9, 12, 1, tzinfo=TZ))
    expire_sessions(conn, datetime(2026, 11, 9, 12, 6, tzinfo=TZ))
    bag = list_bags(conn)[0]
    assert not bag["enabled"]
    assert bag["status"] == "timed_out"


def test_no_expiry_before_window():
    conn = db()
    expire_sessions(conn, datetime(2026, 11, 9, 11, 59, tzinfo=TZ))
    assert list_bags(conn)[0]["status"] == "armed"
