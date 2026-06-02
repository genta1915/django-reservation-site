from django.urls import path

from .view_modules import admin_views, reservation_views

app_name = "reservations"

urlpatterns = [
    path("", reservation_views.index, name="index"),
    path("slots/<int:slot_id>/reserve/", reservation_views.reserve, name="reserve"),
    path("thanks/", reservation_views.thanks, name="thanks"),
    path(
        "cancel/<int:reservation_id>/",
        reservation_views.cancel_reservation,
        name="cancel_reservation",
    ),
    path("manage/", admin_views.manage_home, name="manage_home"),
    path(
        "manage/reservations/",
        admin_views.reservation_list,
        name="reservation_list",
    ),
    path("slots/partial/", reservation_views.slots_partial, name="slots_partial"),
    path(
        "manage/reservations/edit/<int:pk>/",
        admin_views.edit_reservation,
        name="edit_reservation",
    ),
    path(
        "manage/reservations/delete/<int:pk>/",
        admin_views.delete_reservation,
        name="delete_reservation",
    ),
]
