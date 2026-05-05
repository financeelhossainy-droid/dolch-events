# Generated manually for expanded booking durations.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0004_booking_start_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="duration_type",
            field=models.CharField(
                choices=[
                    ("1h", "ساعة"),
                    ("2h", "ساعتان"),
                    ("photo_video_zaffa_offer", "عرض فوتو + فيديو + زفة"),
                ],
                default="1h",
                max_length=30,
                verbose_name="مدة الحجز",
            ),
        ),
    ]
