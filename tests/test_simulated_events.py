"""Offline monitoring integration regression tests."""
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from monitoring import SimulatedAvailability
from pi_dashboard import expire_sessions, observe_simulated

TZ = ZoneInfo("America/New_York")


def test_simulated_event_is_deduplicated_per_arm_date():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE bags (
            id INTEGER PRIMARY KEY, name TEXT, drop_time TEXT, priority INTEGER,
            enabled INTEGER, status TEXT, last_session TEXT,
            window_minutes INTEGER, days TEXT, arm_date TEXT,
            last_checked_at TEXT, last_check_available INTEGER
        );
        CREATE TABLE observations (
            id INTEGER PRIMARY KEY, bag_id INTEGER NOT NULL,
            arm_date TEXT NOT NULL, observed_at TEXT NOT NULL,
            available INTEGER NOT NULL,
            UNIQUE(bag_id, arm_date, available)
        );
        INSERT INTO bags (id,name,drop_time,priority,enabled,status,last_session,window_minutes,days,arm_date) VALUES (1,'Test','12:00',1,1,'armed',NULL,5,'all','2026-11-09');
    """)
    now = datetime(2026, 11, 9, 12, 1, tzinfo=TZ)
    expire_sessions(db, now)
    source = SimulatedAvailability([1])
    assert len(observe_simulated(db, source, now)) == 1
    assert observe_simulated(db, source, now) == []
    assert db.execute("SELECT count(*) FROM observations").fetchone()[0] == 1
    expire_sessions(db, datetime(2026, 11, 9, 12, 6, tzinfo=TZ))
    assert observe_simulated(db, source, now) == []


def test_availability_can_cycle_without_stale_true_state():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE bags (
            id INTEGER PRIMARY KEY, name TEXT, drop_time TEXT, priority INTEGER,
            enabled INTEGER, status TEXT, last_session TEXT,
            window_minutes INTEGER, days TEXT, arm_date TEXT
        );
        CREATE TABLE observations (
            id INTEGER PRIMARY KEY, bag_id INTEGER NOT NULL,
            arm_date TEXT NOT NULL, observed_at TEXT NOT NULL,
            available INTEGER NOT NULL,
            UNIQUE(bag_id, arm_date, available)
        );
        INSERT INTO bags VALUES
            (1,'Test','12:00',1,1,'watching',NULL,5,'all','2026-11-09');
    """)
    now = datetime(2026, 11, 9, 12, 1, tzinfo=TZ)
    assert len(observe_simulated(db, SimulatedAvailability([1]), now)) == 1
    assert observe_simulated(db, SimulatedAvailability([]), now) == []
    assert db.execute(
        "SELECT available FROM observations ORDER BY id DESC LIMIT 1"
    ).fetchone()[0] == 0
    assert len(observe_simulated(db, SimulatedAvailability([1]), now)) == 1
    assert db.execute(
        "SELECT available FROM observations ORDER BY id DESC LIMIT 1"
    ).fetchone()[0] == 1


def test_repeated_checks_update_timestamp_even_without_transition():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE bags (
            id INTEGER PRIMARY KEY, priority INTEGER, enabled INTEGER, status TEXT,
            arm_date TEXT, last_checked_at TEXT, last_check_available INTEGER
        );
        CREATE TABLE observations (
            id INTEGER PRIMARY KEY, bag_id INTEGER, arm_date TEXT,
            observed_at TEXT, available INTEGER,
            UNIQUE(bag_id, arm_date, available)
        );
        INSERT INTO bags(id,priority,enabled,status,arm_date)
            VALUES(1,1,1,'watching','2026-11-09');
    """)
    first = datetime(2026, 11, 9, 12, 1, tzinfo=TZ)
    second = datetime(2026, 11, 9, 12, 2, tzinfo=TZ)
    assert observe_simulated(db, SimulatedAvailability([]), first) == []
    assert observe_simulated(db, SimulatedAvailability([]), second) == []
    bag = db.execute(
        "SELECT last_checked_at,last_check_available FROM bags WHERE id=1"
    ).fetchone()
    assert bag["last_checked_at"] == second.isoformat()
    assert bag["last_check_available"] == 0
    assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
