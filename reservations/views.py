import json

from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date


from .models import Slot, Reservation

from .view_modules.utils import (
    build_date_status,
    create_reservation,
    get_slots_with_remaining,
)

from .view_modules.admin_views import (
    delete_reservation,
    edit_reservation,
    manage_home,
    reservation_list,
)

from .view_modules.reservation_views import (
    cancel_reservation,
    index,
    reserve,
    slots_partial,
    thanks,
)
