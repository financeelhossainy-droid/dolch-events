from django.urls import path
from .views import booking_list, booking_create, booking_detail, booking_pdf

urlpatterns = [
    path("", booking_list, name="booking_list"),
    path("new/", booking_create, name="booking_create"),
    path("<int:booking_id>/", booking_detail, name="booking_detail"),
    path("<int:booking_id>/pdf/", booking_pdf, name="booking_pdf"),
]
from django.urls import path
from .views import booking_pdf

urlpatterns = [
    path("booking/<int:pk>/pdf/", booking_pdf, name="booking_pdf"),
]
