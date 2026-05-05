from django import forms
from datetime import datetime, timedelta
from .models import Booking, BookingService, Client
from core.models import Service


BOOKING_TIME_CHOICES = [
    ("11:00", "11:00 صباحًا"),
    ("12:00", "12:00 ظهرًا"),
    ("13:00", "01:00 مساءً"),
    ("14:00", "02:00 مساءً"),
    ("15:00", "03:00 مساءً"),
    ("16:00", "04:00 مساءً"),
    ("17:00", "05:00 مساءً"),
    ("18:00", "06:00 مساءً"),
    ("19:00", "07:00 مساءً"),
    ("20:00", "08:00 مساءً"),
    ("21:00", "09:00 مساءً"),
    ("22:00", "10:00 مساءً"),
    ("23:00", "11:00 مساءً"),
    ("00:00", "12:00 منتصف الليل"),
    ("01:00", "01:00 صباحًا"),
]

EXTRA_TIME_CHOICES = [
    (0, "بدون وقت إضافي"),
    (15, "ربع ساعة إضافية"),
    (30, "نصف ساعة إضافية"),
    (45, "45 دقيقة إضافية"),
    (60, "ساعة إضافية"),
    (75, "ساعة وربع إضافية"),
    (90, "ساعة ونصف إضافية"),
    (105, "ساعة و45 دقيقة إضافية"),
    (120, "ساعتان إضافيتان"),
    (150, "ساعتان ونصف إضافية"),
    (180, "3 ساعات إضافية"),
]


class BookingForm(forms.ModelForm):
    client_name = forms.CharField(max_length=100, label="اسم العميل")
    client_phone = forms.CharField(max_length=11, label="رقم هاتف العميل")

    class Meta:
        model = Booking
        fields = [
            "hall",
            "occasion_type",
            "duration_type",
            "booking_date",
            "occasion_date",
            "start_time",
            "extra_minutes",
            "groom_name",
            "groom_national_id",
            "groom_address",
            "bride_name",
            "bride_national_id",
            "bride_address",
            "amount_paid",
            "notes",
        ]
        widgets = {
            "booking_date": forms.DateInput(attrs={"type": "date"}),
            "occasion_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.Select(choices=BOOKING_TIME_CHOICES),
            "extra_minutes": forms.Select(choices=EXTRA_TIME_CHOICES),
            "groom_address": forms.TextInput(),
            "bride_address": forms.TextInput(),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_client_phone(self):
        phone = self.cleaned_data["client_phone"]
        Client._meta.get_field("phone").run_validators(phone)
        return phone

    def clean(self):
        cleaned_data = super().clean()
        hall = cleaned_data.get("hall")
        occasion_date = cleaned_data.get("occasion_date")
        start_time = cleaned_data.get("start_time")

        duration_type = cleaned_data.get("duration_type")

        if hall and occasion_date and start_time:
            base_minutes = {
                Booking.DurationType.ONE_HOUR: 60,
                Booking.DurationType.TWO_HOURS: 120,
                Booking.DurationType.PHOTO_VIDEO_ZAFFA_OFFER: 90,
            }.get(duration_type, 60)
            minutes = base_minutes + (cleaned_data.get("extra_minutes") or 0)
            start_datetime = datetime.combine(occasion_date, start_time)
            end_datetime = start_datetime + timedelta(minutes=minutes)

            possible_conflicts = Booking.objects.filter(
                hall=hall,
                occasion_date=occasion_date,
            ).exclude(status=Booking.BookingStatus.CANCELLED)
            if self.instance.pk:
                possible_conflicts = possible_conflicts.exclude(pk=self.instance.pk)

            for booking in possible_conflicts:
                conflict_start, conflict_end = booking.booking_interval()
                if start_datetime < conflict_end and end_datetime > conflict_start:
                    raise forms.ValidationError("هذه القاعة محجوزة بالفعل في وقت متداخل مع هذا الحجز.")

        return cleaned_data

    def save(self, commit=True):
        client_name = self.cleaned_data.pop("client_name")
        client_phone = self.cleaned_data.pop("client_phone")
        client, created = Client.objects.get_or_create(
            phone=client_phone,
            defaults={"name": client_name},
        )
        if not created and client.name != client_name:
            client.name = client_name
            client.save(update_fields=["name"])

        booking = super().save(commit=False)
        booking.client = client
        if commit:
            booking.save()
            self.save_m2m()
        return booking


class BookingServiceForm(forms.ModelForm):
    class Meta:
        model = BookingService
        fields = ["service", "quantity", "notes"]
        labels = {
            "service": "الأوبشن / الخدمة الإضافية",
            "quantity": "الكمية",
            "notes": "ملاحظة",
        }

    def __init__(self, *args, **kwargs):
        booking = kwargs.pop("booking", None)
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True).order_by("service_type", "name")
        self.booking = booking

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.booking:
            obj.booking = self.booking
        if commit:
            obj.save()
        return obj
