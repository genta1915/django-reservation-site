from django.db import models
from django.utils import timezone
from django.apps import apps
from django.db.models import Sum


class Slot(models.Model):
    date = models.DateField()
    time = models.TimeField()
    capacity = models.PositiveIntegerField(default=1) # 定員(固定)


    class Meta:
        unique_together = ("date", "time")
        ordering = ["date", "time"]

    def __str__(self):
        date = self.date if self.date else "no-date"
        time = self.time.strftime("%H:%M") if self.time else "no-time"
        return f"{date} {time} (cap:{self.capacity})"

    @property
    def reserved_count(self):
        Reservation = apps.get_model("reservations","Reservation")
        total = self.reservations.filter(
            status=Reservation.Status.ACTIVE
        ).aggregate(s=Sum("people"))["s"]
        return total or 0
    
    @property
    def remaining(self):
        # 空き枠
        return max(0,self.capacity - self.reserved_count)

    @property
    def is_full(self):
        return self.remaining <= 0


class Reservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "予約中"
        CANCELED = "canceled", "キャンセル"

    slot = models.ForeignKey(Slot, related_name="reservations", on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    people = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} / {self.slot} ({self.status})"


