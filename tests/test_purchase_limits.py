"""Purchase limit selection and reservation regression tests."""
import sqlite3

import pytest

from purchase_limits import dollars_to_cents, reserve_bag, select_bags


def test_priority_skips_unaffordable_bag():
    bags = [{"id": 1, "priority": 1, "price_cents": 1000},
            {"id": 2, "priority": 2, "price_cents": 700},
            {"id": 3, "priority": 3, "price_cents": 400}]
    assert select_bags(bags, max_cents=1500, max_bags=2) == [1, 3]


def test_optional_caps_and_existing_spend():
    bags = [{"id": 1, "priority": 1, "price_cents": 1000},
            {"id": 2, "priority": 2, "price_cents": 400}]
    assert select_bags(bags) == [1, 2]
    assert select_bags(bags, max_cents=1500, spent_cents=600) == [2]
    assert select_bags(bags, max_bags=1, purchased_bags=1) == []


@pytest.mark.parametrize("amount", ["-1", "2.001", "nan", "Infinity"])
def test_reject_invalid_money(amount):
    with pytest.raises(ValueError):
        dollars_to_cents(amount)


def test_reservations_count_pending_and_confirmed():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE bags (id INTEGER PRIMARY KEY, price_cents INTEGER);
        CREATE TABLE purchase_limits (id INTEGER PRIMARY KEY,max_cents INTEGER,max_bags INTEGER);
        CREATE TABLE purchase_reservations (
            id INTEGER PRIMARY KEY,bag_id INTEGER,purchase_day TEXT,
            price_cents INTEGER,state TEXT,UNIQUE(bag_id,purchase_day));
        INSERT INTO bags VALUES (1,1000),(2,700),(3,400);
        INSERT INTO purchase_limits VALUES (1,1500,2);
    """)
    assert reserve_bag(db, 1, "2026-11-09")
    assert not reserve_bag(db, 2, "2026-11-09")
    assert reserve_bag(db, 3, "2026-11-09")
    assert not reserve_bag(db, 3, "2026-11-09")


@pytest.mark.parametrize("amount", ["1e100", "1e999999999", "999999999999999999999999"])
def test_reject_oversized_money_without_crashing(amount):
    with pytest.raises(ValueError):
        dollars_to_cents(amount)


def test_money_accepts_exact_cents():
    assert dollars_to_cents("15.00") == 1500
    assert dollars_to_cents("0.01") == 1
