from collections import defaultdict

from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce

from ..models import Reservation, Slot


def get_slots_with_remaining():
    return (
        Slot.objects.all()
        .annotate(
            reserved=Coalesce(
                Sum(
                    "reservations__people",
                    filter=models.Q(reservations__status=Reservation.Status.ACTIVE),
                ),
                0,
            ),
            remaining_db=F("capacity") - F("reserved"),
        )
        .order_by("date", "time")
    )


def build_date_status(all_slots):
    date_counts = defaultdict(lambda: {"available": 0, "full": 0})

    for s in all_slots:
        remaining = s.capacity - s.reserved
        key = s.date.strftime("%Y-%m-%d")

        if remaining > 0:
            date_counts[key]["available"] += 1
        else:
            date_counts[key]["full"] += 1

    final_status = {}

    for d, counts in date_counts.items():
        if counts["available"] > 0 and counts["full"] > 0:
            final_status[d] = "mixed"
        elif counts["available"] > 0:
            final_status[d] = "available"
        else:
            final_status[d] = "full"

    return final_status


def create_reservation(slot, people, request):
    name = request.POST.get("name", "")
    phone = request.POST.get("phone", "")

    return Reservation.objects.create(
        slot=slot,
        name=name,
        phone=phone,
        people=people,
        status=Reservation.Status.ACTIVE,
    )
