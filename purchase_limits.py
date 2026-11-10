"""Daily purchase caps and priority-first selection. All monetary amounts are cents.

No network or payment operations. Caller must serialize reservation transactions.
"""
from decimal import Decimal, InvalidOperation


def dollars_to_cents(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid dollar amount") from None
    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal("0.01")):
        raise ValueError("Dollar amount must be nonnegative with at most two decimals")
    return int(amount * 100)


def select_bags(bags, max_cents=None, max_bags=None, spent_cents=0, purchased_bags=0):
    """Choose in priority order, skipping unaffordable items.

    bags: iterable of mappings containing id, priority, price_cents.
    Pending reservations must be included in spent_cents/purchased_bags.
    """
    if max_cents is not None and max_cents < 0:
        raise ValueError("Invalid spending cap")
    if max_bags is not None and max_bags < 0:
        raise ValueError("Invalid bag cap")
    selected, total = [], spent_cents
    for bag in sorted(bags, key=lambda item: (item["priority"], item["id"])):
        if max_bags is not None and purchased_bags + len(selected) >= max_bags:
            break
        price = bag["price_cents"]
        if price is None or price < 0:
            continue
        if max_cents is not None and total + price > max_cents:
            continue
        selected.append(bag["id"])
        total += price
    return selected


def reserve_bag(db, bag_id, day):
    """Atomically reserve capacity before checkout. Must be called inside a write transaction.

    Only confirmed purchase or explicit cancellation should release a reservation.
    """
    config = db.execute("SELECT max_cents,max_bags FROM purchase_limits WHERE id=1").fetchone()
    bag = db.execute("SELECT price_cents FROM bags WHERE id=?", (bag_id,)).fetchone()
    if not bag or bag["price_cents"] is None:
        return False
    totals = db.execute(
        "SELECT COALESCE(SUM(price_cents),0),COUNT(*) FROM purchase_reservations "
        "WHERE purchase_day=? AND state IN ('pending','confirmed')", (day,)
    ).fetchone()
    if config["max_cents"] is not None and totals[0] + bag["price_cents"] > config["max_cents"]:
        return False
    if config["max_bags"] is not None and totals[1] + 1 > config["max_bags"]:
        return False
    try:
        db.execute(
            "INSERT INTO purchase_reservations(bag_id,purchase_day,price_cents,state) VALUES(?,?,?,'pending')",
            (bag_id, day, bag["price_cents"]),
        )
    except __import__("sqlite3").IntegrityError:
        return False
    return True
