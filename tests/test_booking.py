from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from driveeasy import BookingError, BookingService

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
START = NOW + timedelta(days=2)
END = START + timedelta(days=3)


def test_hold_is_15_minutes() -> None:
    hold = BookingService().place_hold("CAR-1", START, END, NOW)
    assert hold.expires_at == NOW + timedelta(minutes=15)
    assert hold.status == "HELD"


def test_overlapping_car_cannot_be_held_twice() -> None:
    service = BookingService()
    service.place_hold("CAR-1", START, END, NOW)
    with pytest.raises(BookingError, match="already held"):
        service.place_hold("CAR-1", START + timedelta(hours=1), END, NOW)


def test_adjacent_intervals_are_allowed() -> None:
    service = BookingService()
    service.place_hold("CAR-1", START, END, NOW)
    next_hold = service.place_hold("CAR-1", END, END + timedelta(hours=2), NOW)
    assert next_hold.status == "HELD"


def test_another_car_can_have_the_same_interval() -> None:
    service = BookingService()
    service.place_hold("CAR-1", START, END, NOW)
    assert service.place_hold("CAR-2", START, END, NOW).car_id == "CAR-2"


def test_payment_is_required_to_confirm() -> None:
    service = BookingService()
    hold = service.place_hold("CAR-1", START, END, NOW)
    with pytest.raises(BookingError, match="payment"):
        service.confirm(hold.booking_id, NOW, payment_succeeded=False)
    assert service.get(hold.booking_id).status == "HELD"


def test_paid_hold_can_be_confirmed() -> None:
    service = BookingService()
    hold = service.place_hold("CAR-1", START, END, NOW)
    confirmed = service.confirm(hold.booking_id, NOW, payment_succeeded=True)
    assert confirmed.status == "CONFIRMED"


def test_confirmed_car_remains_unavailable_after_hold_expiration() -> None:
    service = BookingService()
    hold = service.place_hold("CAR-1", START, END, NOW)
    service.confirm(hold.booking_id, NOW, payment_succeeded=True)
    assert service.expire_holds(NOW + timedelta(hours=1)) == 0
    with pytest.raises(BookingError, match="already held"):
        service.place_hold("CAR-1", START, END, NOW + timedelta(hours=1))


def test_hold_cleanup_releases_unpaid_car() -> None:
    service = BookingService()
    hold = service.place_hold("CAR-1", START, END, NOW)
    assert service.expire_holds(hold.expires_at) == 1
    assert service.get(hold.booking_id).status == "EXPIRED"
    assert service.place_hold("CAR-1", START, END, hold.expires_at).status == "HELD"


def test_late_payment_cannot_confirm() -> None:
    service = BookingService()
    hold = service.place_hold("CAR-1", START, END, NOW)
    with pytest.raises(BookingError, match="expired"):
        service.confirm(hold.booking_id, hold.expires_at + timedelta(microseconds=1), True)
    assert service.get(hold.booking_id).status == "EXPIRED"


def test_naive_timestamps_are_rejected() -> None:
    service = BookingService()
    with pytest.raises(BookingError, match="timezone-aware"):
        service.place_hold("CAR-1", START.replace(tzinfo=None), END, NOW)


def test_concurrent_holds_cannot_double_book() -> None:
    service = BookingService()

    def attempt(_: int) -> bool:
        try:
            service.place_hold("CAR-1", START, END, NOW)
            return True
        except BookingError:
            return False

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(attempt, range(30)))
    assert sum(results) == 1


def test_idempotent_hold_returns_one_booking() -> None:
    service = BookingService()
    first = service.place_hold("CAR-1", START, END, NOW, "request-123")
    repeat = service.place_hold("CAR-1", START, END, NOW, "request-123")
    assert first.booking_id == repeat.booking_id


def test_idempotency_key_cannot_be_reused_with_different_payload() -> None:
    service = BookingService()
    service.place_hold("CAR-1", START, END, NOW, "request-123")
    with pytest.raises(BookingError, match="different request"):
        service.place_hold("CAR-2", START, END, NOW, "request-123")


def test_repeated_confirmation_has_no_new_business_effect() -> None:
    service = BookingService()
    hold = service.place_hold("CAR-1", START, END, NOW, "request-123")
    first = service.confirm(hold.booking_id, NOW, True)
    second = service.confirm(hold.booking_id, NOW + timedelta(hours=2), True)
    assert first == second
