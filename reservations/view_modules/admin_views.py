from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from ..models import Reservation, Slot


@login_required
def manage_home(request):
    if not request.user.is_staff:
        return redirect("/")
    return render(request, "manage/home.html")


@login_required
def reservation_list(request):
    if not request.user.is_staff:
        return redirect("/")

    reservations = Reservation.objects.select_related("slot").all().order_by("-id")

    return render(
        request, "manage/reservation_list.html", {"reservations": reservations}
    )


@login_required
def delete_reservation(request, pk):
    if not request.user.is_staff:
        return redirect("/")

    reservation = get_object_or_404(Reservation, pk=pk)

    if request.method == "POST":
        reservation.delete()

    return redirect("reservations:reservation_list")


@login_required
def edit_reservation(request, pk):
    if not request.user.is_staff:
        return redirect("/")

    reservation = get_object_or_404(Reservation, pk=pk)
    slots = Slot.objects.all().order_by("date", "time")

    if request.method == "POST":
        reservation.name = request.POST.get("name")
        reservation.people = request.POST.get("people")
        reservation.phone = request.POST.get("phone")
        slot_id = request.POST.get("slot")
        if slot_id:
            reservation.slot = get_object_or_404(Slot, pk=slot_id)
        reservation.save()
        messages.success(request, "予約を更新しました")
        return redirect("reservations:reservation_list")

    return render(
        request,
        "manage/edit_reservation.html",
        {
            "reservation": reservation,
            "slots": slots,
        },
    )
