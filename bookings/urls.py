from django.urls import path
from . import views

urlpatterns = [
    path("", views.booking_list, name="booking_list"),
    path("calendar/", views.booking_calendar, name="booking_calendar"),
    path("create/", views.booking_create, name="booking_create"),
    path("<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path("booking/<int:pk>/pdf/", views.booking_pdf, name="booking_pdf"),
]
