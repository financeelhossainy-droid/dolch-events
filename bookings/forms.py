from django import forms
from .models import Booking, BookingService
from core.models import Service


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "client",
            "hall",
            "occasion_type",
            "duration_type",
            "booking_date",
            "occasion_date",
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
            "groom_address": forms.TextInput(),
            "bride_address": forms.TextInput(),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

class BookingServiceForm(forms.ModelForm):
    class Meta:
        model = BookingService
        fields = ["service", "quantity", "notes"]

    def __init__(self, *args, **kwargs):
        booking = kwargs.pop("booking", None)
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        self.booking = booking

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.booking:
            obj.booking = self.booking
        if commit:
            obj.save()
        return obj
