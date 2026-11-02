"""In-memory reservation invariants for the lab, NOT distributed production booking."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from threading import RLock
from typing import Literal


class BookingError(ValueError):
    """Raised when a booking operation violates a domain rule."""


Status = Literal["HELD", "CONFIRMED", "EXPIRED"]


@dataclass(frozen=True, slots=True)
class Booking:
    booking_id: str
    car_id: str
    starts_at: datetime
    ends_at: datetime
    expires_at: datetime
    status: Status


def _require_aware(*values: datetime) -> None:
    for value in values:
        if value.tzinfo is None or value.utcoffset() is None:
            raise BookingError("All timestamps must be timezone-aware")


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """Half-open intervals [start, end): touching endpoints do not overlap."""
    return a_start < b_end and b_start < a_end


class BookingService:
    """Process-local reference model (not suitable for multiple server instances)."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._bookings: dict[str, Booking] = {}
        self._hold_requests: dict[str, tuple[tuple[str, datetime, datetime], str]] = {}

    def place_hold(
        self,
        car_id: str,
        starts_at: datetime,
        ends_at: datetime,
        now: datetime,
        idempotency_key: str | None = None,
    ) -> Booking:
        _require_aware(starts_at, ends_at, now)
        if not car_id.strip() or starts_at >= ends_at:
            raise BookingError("Car ID and a valid rental interval are required")
        if idempotency_key is not None and not idempotency_key.strip():
            raise BookingError("Idempotency key cannot be empty")
        with self._lock:
            if idempotency_key is not None and idempotency_key in self._hold_requests:
                original_payload, original_id = self._hold_requests[idempotency_key]
                if original_payload != (car_id, starts_at, ends_at):
                    raise BookingError("Idempotency key reused with different request")
                return self._bookings[original_id]
            for previous in self._bookings.values():
                active = previous.status == "CONFIRMED" or (
                    previous.status == "HELD" and now < previous.expires_at
                )
                if (
                    previous.car_id == car_id
                    and active
                    and _overlaps(starts_at, ends_at, previous.starts_at, previous.ends_at)
                ):
                    raise BookingError("Car already held or booked for overlapping dates")
            booking_id = f"B-{len(self._bookings) + 1:04d}"
            booking = Booking(
                booking_id, car_id, starts_at, ends_at, now + timedelta(minutes=15), "HELD"
            )
            self._bookings[booking_id] = booking
            if idempotency_key is not None:
                self._hold_requests[idempotency_key] = ((car_id, starts_at, ends_at), booking_id)
            return booking

    def confirm(self, booking_id: str, now: datetime, payment_succeeded: bool) -> Booking:
        _require_aware(now)
        with self._lock:
            booking = self._bookings[booking_id]
            if booking.status == "CONFIRMED":
                return booking
            if booking.status != "HELD":
                raise BookingError("Booking is no longer held")
            if not payment_succeeded:
                raise BookingError("Successful payment is required")
            if now > booking.expires_at:
                self._bookings[booking_id] = replace(booking, status="EXPIRED")
                raise BookingError("Hold already expired")
            confirmed = replace(booking, status="CONFIRMED")
            self._bookings[booking_id] = confirmed
            return confirmed

    def expire_holds(self, now: datetime) -> int:
        _require_aware(now)
        count = 0
        with self._lock:
            for booking_id, booking in list(self._bookings.items()):
                if booking.status == "HELD" and now >= booking.expires_at:
                    self._bookings[booking_id] = replace(booking, status="EXPIRED")
                    count += 1
        return count

    def get(self, booking_id: str) -> Booking:
        with self._lock:
            return self._bookings[booking_id]
