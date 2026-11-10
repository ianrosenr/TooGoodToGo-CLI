"""Tests for the offline-only monitoring contract."""
from monitoring import PollGate, SimulatedAvailability


def test_simulated_availability_is_deterministic():
    source = SimulatedAvailability([2])
    assert source.check(2).available
    assert not source.check(3).available


def test_gate_spaces_out_requests():
    gate = PollGate(5)
    assert gate.ready(0)
    gate.record_request(0)
    assert not gate.ready(4.9)
    assert gate.ready(5)


def test_backoff_overrides_poll_interval():
    gate = PollGate(5)
    gate.record_request(0)
    gate.backoff(1, 30)
    assert not gate.ready(30)
    assert gate.ready(31)
