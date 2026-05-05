# Generated manually for booking time slots.

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0003_booking_bride_address_booking_bride_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="start_time",
            field=models.TimeField(default=datetime.time(11, 0), verbose_name="ساعة بداية الحجز"),
        ),
    ]
