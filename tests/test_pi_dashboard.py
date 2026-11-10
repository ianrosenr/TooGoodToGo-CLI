"""Manual arming and scheduled-window regression tests."""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from pi_dashboard import expire_sessions, list_bags, next_arm_date

TZ = ZoneInfo("America/New_York")


def at(day, hour, minute=0):
    return datetime(2026, 11, day, hour, minute, tzinfo=TZ)


def db(armed=True, days="all", duration=5):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE bags (
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, drop_time TEXT NOT NULL,
        priority INTEGER NOT NULL, enabled INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'disabled', last_session TEXT,
        window_minutes INTEGER NOT NULL DEFAULT 5,
        days TEXT NOT NULL DEFAULT 'all', arm_date TEXT)""")
    conn.execute(
        "INSERT INTO bags(name,drop_time,priority,enabled,status,window_minutes,days,arm_date) VALUES(?,?,?,?,?,?,?,?)",
        ("Test", "12:00", 1, int(armed), "armed" if armed else "disabled", duration, days,
         "2026-11-09" if armed else None),
    )
    return conn


def test_new_bag_is_not_automatically_armed():
    conn = db(armed=False)
    expire_sessions(conn, at(9, 12, 1))
    assert not list_bags(conn)[0]["enabled"]


def test_enters_watching_during_window():
    conn = db()
    expire_sessions(conn, at(9, 12, 1))
    assert list_bags(conn)[0]["status"] == "watching"


def test_watching_expires_after_window():
    conn = db()
    expire_sessions(conn, at(9, 12, 1))
    expire_sessions(conn, at(9, 12, 6))
    bag = list_bags(conn)[0]
    assert not bag["enabled"]
    assert bag["status"] == "timed_out"


def test_missed_window_disables_without_ever_watching():
    conn = db()
    expire_sessions(conn, at(9, 14))
    assert list_bags(conn)[0]["status"] == "timed_out"


def test_no_expiry_before_window():
    conn = db()
    expire_sessions(conn, at(9, 11, 59))
    assert list_bags(conn)[0]["status"] == "armed"


def test_custom_window_does_not_expire_early():
    conn = db(duration=30)
    expire_sessions(conn, at(9, 12, 10))
    assert list_bags(conn)[0]["enabled"]
    expire_sessions(conn, at(9, 12, 31))
    assert list_bags(conn)[0]["status"] == "timed_out"


def test_after_window_arms_tomorrow():
    bag = dict(list_bags(db())[0])
    assert next_arm_date(bag, at(9, 13)) == "2026-11-10"


def test_during_window_arms_today():
    bag = dict(list_bags(db())[0])
    assert next_arm_date(bag, at(9, 12, 2)) == "2026-11-09"


def test_weekend_schedule_skips_monday():
    bag = dict(list_bags(db(days="weekends"))[0])
    assert next_arm_date(bag, at(9, 10)) == "2026-11-14"


def test_restart_does_not_rearm_expired_occurrence():
    conn = db()
    expire_sessions(conn, at(9, 14))
    expire_sessions(conn, at(10, 12, 1))
    assert not list_bags(conn)[0]["enabled"]
