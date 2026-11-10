"""Read-only availability monitoring contract; no TGTG requests or checkout.

Adapters must be explicitly supplied. Simulation never contacts a remote service.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class Availability:
    bag_id: int
    available: bool
    observed_at: datetime


class AvailabilitySource(Protocol):
    def check(self, bag_id: int) -> Availability:
        """Perform one read-only availability observation."""


class SimulatedAvailability:
    """Deterministic local test source, no network traffic."""

    def __init__(self, available_bag_ids=()):
        self.available_bag_ids = frozenset(available_bag_ids)

    def check(self, bag_id: int) -> Availability:
        return Availability(bag_id, bag_id in self.available_bag_ids,
                            datetime.now().astimezone())


class PollGate:
    """Global minimum request interval and temporary backoff.

    Caller must check eligibility before calling any remote adapter.
    No rate-limit guarantees: providers may enforce stricter limits.
    """

    def __init__(self, interval_seconds=5.0):
        if interval_seconds < 1:
            raise ValueError("Remote polling interval must be >= 1 second")
        self.interval_seconds = float(interval_seconds)
        self.next_allowed = 0.0

    def ready(self, monotonic_now: float) -> bool:
        return monotonic_now >= self.next_allowed

    def record_request(self, monotonic_now: float) -> None:
        self.next_allowed = max(self.next_allowed, monotonic_now) + self.interval_seconds

    def backoff(self, monotonic_now: float, retry_after_seconds: float) -> None:
        self.next_allowed = max(self.next_allowed, monotonic_now + max(0, retry_after_seconds))
