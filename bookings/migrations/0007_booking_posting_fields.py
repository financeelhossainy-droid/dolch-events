# Generated manually for booking posting controls.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounting", "0002_accountingdetermination"),
        ("bookings", "0006_booking_extra_minutes"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="is_posted",
            field=models.BooleanField(default=False, verbose_name="مرحل محاسبيًا"),
        ),
        migrations.AddField(
            model_name="booking",
            name="posted_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="وقت الترحيل"),
        ),
        migrations.AddField(
            model_name="booking",
            name="journal_entry",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bookings",
                to="accounting.journalentry",
                verbose_name="قيد اليومية",
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="posted_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="posted_bookings",
                to=settings.AUTH_USER_MODEL,
                verbose_name="تم الترحيل بواسطة",
            ),
        ),
        migrations.AlterModelOptions(
            name="booking",
            options={
                "ordering": ["-occasion_date"],
                "permissions": [
                    ("can_confirm_booking", "Can confirm and post booking"),
                    ("can_unpost_booking", "Can reverse posted booking"),
                ],
                "verbose_name": "حجز",
                "verbose_name_plural": "الحجوزات",
            },
        ),
    ]
