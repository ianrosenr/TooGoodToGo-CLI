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
            window_minutes INTEGER, days TEXT, arm_date TEXT
        );
        CREATE TABLE observations (
            id INTEGER PRIMARY KEY, bag_id INTEGER NOT NULL,
            arm_date TEXT NOT NULL, observed_at TEXT NOT NULL,
            available INTEGER NOT NULL,
            UNIQUE(bag_id, arm_date, available)
        );
        INSERT INTO bags VALUES (1,'Test','12:00',1,1,'armed',NULL,5,'all','2026-11-09');
    """)
    now = datetime(2026, 11, 9, 12, 1, tzinfo=TZ)
    expire_sessions(db, now)
    source = SimulatedAvailability([1])
    assert len(observe_simulated(db, source, now)) == 1
    assert observe_simulated(db, source, now) == []
    assert db.execute("SELECT count(*) FROM observations").fetchone()[0] == 1
    expire_sessions(db, datetime(2026, 11, 9, 12, 6, tzinfo=TZ))
    assert observe_simulated(db, source, now) == []
