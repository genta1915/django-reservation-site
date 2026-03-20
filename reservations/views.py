from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.db import transaction
from django.utils.dateparse import parse_date
from .models import Slot,Reservation
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render
from django.db import models
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from collections import defaultdict
import json
from django.db.models import Case, When, IntegerField

@login_required
def manage_home(request):
    if not request.user.is_staff:
        return redirect('/')
    return render(request, "manage/home.html")

@login_required
def reservation_list(request):
    if not request.user.is_staff:
        return redirect('/')

    reservations = Reservation.objects.select_related('slot').all().order_by('-id')

    return render(request, 'manage/reservation_list.html', {
        'reservations': reservations
    })

@login_required
def delete_reservation(request, pk):
    if not request.user.is_staff:
        return redirect('/')

    reservation = get_object_or_404(Reservation, pk=pk)

    if request.method == "POST":
        reservation.delete()

    return redirect('reservations:reservation_list')

def index(request):
    # ?date=YYYY-MM-DD を受け取る
    qdate_str = request.GET.get("date")
    qdate = parse_date(qdate_str) if qdate_str else None

    today = timezone.localdate()

    slots = (
        Slot.objects.filter(date__gte=today)
        .annotate(
            reserved=Coalesce(
                Sum(
                    "reservations__people",
                    filter=models.Q(reservations__status=Reservation.Status.ACTIVE),
                ),
                0,
            ),
            remaining_db=F("capacity") - F("reserved")
        )
        .order_by("date", "time")
    )

    now = timezone.localtime().time()
    slots = slots.exclude(date=today, time__lt=now)
    
    if qdate:
        if qdate < today:
            qdate = None # 過去日なら無効化(一覧出さない)
        else:
            slots = slots.filter(date=qdate)

    # flatpickr の enable 用（"YYYY-MM-DD" の配列）
    available_dates = (
        Slot.objects.filter(date__gte=today)
        .order_by("date")
        .values_list("date", flat=True)
        .distinct()
    )
    available_dates = [d.strftime("%Y-%m-%d") for d in available_dates]

    all_slots = (
        Slot.objects.filter(date__gte=today)
        .annotate(
            reserved=Coalesce(
                Sum(
                    "reservations__people",
                    filter=models.Q(reservations__status=Reservation.Status.ACTIVE),
                ),
                0,
            )
        )
    )

    date_counts = defaultdict(lambda: {"available": 0, "full": 0})

    for s in all_slots:
        remaining = s.capacity - s.reserved
        key = s.date.strftime("%Y-%m-%d")

        if remaining > 0:
            date_counts[key]["available"] += 1
        else:
            date_counts[key]["full"] += 1

    # mixed判定
    final_status = {}

    for d, counts in date_counts.items():
        if counts["available"] > 0 and counts["full"] > 0:
            final_status[d] = "mixed"
        elif counts["available"] > 0:
            final_status[d] = "available"
        else:
            final_status[d] = "full"

    date_status_json = json.dumps(final_status)

    return render(request, "reservations/index.html", {
        "slots": slots,
        "qdate": qdate,
        "available_dates": available_dates,
        "date_status_json": date_status_json,
    })


@transaction.atomic
def reserve(request, slot_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    slot = Slot.objects.select_for_update().get(id=slot_id)
    people = int(request.POST.get("people", 1))

    # 1未満はNG
    if people < 1:
        return redirect("reservations:index")
    
    # 残席より多い人数はNG
    if slot.remaining < people:
        return redirect("reservations:index")

    today = timezone.localdate()
    if slot.date < today:
        # messages を使うなら
        # messages.error(request, "過去の日付は予約できません")
        return redirect("reservations:index")

    # 予約レコードを作る (name/phoneは今フォームがなければ空でOK)
    name = request.POST.get("name","")
    phone = request.POST.get("phone","")

    reservation = Reservation.objects.create(
        slot=slot,
        name=name,
        phone=phone,
        people=people,
        status=Reservation.Status.ACTIVE,
    )

    # thanks画面でキャンセルできるようにID保存(最短実装)
    request.session["last_reservation_id"] = reservation.id
    return redirect("reservations:thanks")

def thanks(request):
    reservation_id = request.session.get("last_reservation_id")
    return render(request,"reservations/thanks.html", {
        "reservation_id":reservation_id
    })

@transaction.atomic
def cansel_reservation(request,reservation_id):
    if request.method !="POST":
        return HttpResponseNotAllowed(["POST"])
    
    reservation = get_object_or_404(
        Reservation.objects.select_for_update(),
        id=reservation_id
    )

    if reservation.status == Reservation.Status.CANCELED:
        return redirect("reservations:index")
    
    reservation.status = Reservation.Status.CANCELED
    reservation.save(update_fields=["status"])

    request.session.pop("last_reservation_id",None)

    return redirect("reservations:index")

def slots_partial(request):
    qdate = parse_date(request.GET.get("date") or "")

    qs = Slot.objects.all().order_by("date", "time")

    if qdate:
        qs = qs.filter(date=qdate)

    return render(request, "reservations/_slots_list.html", {
        "slots": qs,
        "qdate": qdate,
    })