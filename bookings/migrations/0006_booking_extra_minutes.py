# Generated manually for extra booking time.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0005_alter_booking_duration_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="extra_minutes",
            field=models.PositiveSmallIntegerField(default=0, verbose_name="وقت إضافي بالدقائق"),
        ),
    ]
