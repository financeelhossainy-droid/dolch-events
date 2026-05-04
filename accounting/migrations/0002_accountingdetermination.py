# Generated manually for accounting configuration.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounting", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountingDetermination",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("booking_deposit", "مقدم حجز"),
                            ("booking_revenue", "إيراد حجز"),
                            ("service_revenue", "إيراد خدمة إضافية"),
                            ("receivable", "عميل / ذمم مدينة"),
                            ("supplier_invoice", "فاتورة مورد"),
                            ("cash_in", "قبض نقدي"),
                            ("cash_out", "صرف نقدي"),
                            ("inventory_purchase", "شراء مخزون"),
                            ("cost_of_service", "تكلفة خدمة"),
                        ],
                        max_length=40,
                        unique=True,
                        verbose_name="الحدث المحاسبي",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="مفعل")),
                ("notes", models.TextField(blank=True, verbose_name="ملاحظات")),
                (
                    "credit_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="determination_credits",
                        to="accounting.account",
                        verbose_name="حساب الدائن الافتراضي",
                    ),
                ),
                (
                    "debit_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="determination_debits",
                        to="accounting.account",
                        verbose_name="حساب المدين الافتراضي",
                    ),
                ),
            ],
            options={
                "verbose_name": "تحديد محاسبي",
                "verbose_name_plural": "Accounting Determination",
                "ordering": ["event_type"],
            },
        ),
    ]
