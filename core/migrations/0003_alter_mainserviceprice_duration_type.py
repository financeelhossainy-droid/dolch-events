# Generated manually for expanded booking durations.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_alter_mainserviceprice_unique_together_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mainserviceprice",
            name="duration_type",
            field=models.CharField(
                choices=[
                    ("1h", "ساعة"),
                    ("2h", "ساعتان"),
                    ("photo_video_zaffa_offer", "عرض فوتو + فيديو + زفة"),
                    ("na", "غير مرتبط بمدة"),
                ],
                default="na",
                max_length=30,
                verbose_name="المدة",
            ),
        ),
    ]
