# Generated manually for the first accounting module batch.

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=30, unique=True, verbose_name="كود الحساب")),
                ("name_ar", models.CharField(max_length=180, verbose_name="اسم الحساب عربي")),
                ("name_en", models.CharField(blank=True, max_length=180, verbose_name="اسم الحساب إنجليزي")),
                ("main_account_ar", models.CharField(blank=True, max_length=180, verbose_name="الحساب الرئيسي عربي")),
                ("main_account_en", models.CharField(blank=True, max_length=180, verbose_name="الحساب الرئيسي إنجليزي")),
                (
                    "account_type",
                    models.CharField(
                        choices=[
                            ("asset", "أصول"),
                            ("liability", "التزامات"),
                            ("equity", "حقوق ملكية"),
                            ("revenue", "إيرادات"),
                            ("expense", "مصروفات وتكاليف"),
                            ("other", "أخرى"),
                        ],
                        default="other",
                        max_length=20,
                        verbose_name="نوع الحساب",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="مفعل")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="accounting.account",
                        verbose_name="الحساب الأب",
                    ),
                ),
            ],
            options={
                "verbose_name": "حساب",
                "verbose_name_plural": "شجرة الحسابات",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="JournalEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("entry_date", models.DateField(default=django.utils.timezone.localdate, verbose_name="تاريخ القيد")),
                ("reference", models.CharField(blank=True, max_length=80, verbose_name="مرجع")),
                ("description", models.CharField(max_length=255, verbose_name="البيان")),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "مسودة"), ("posted", "مرحل"), ("cancelled", "ملغي")],
                        default="draft",
                        max_length=15,
                        verbose_name="الحالة",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="وقت الإنشاء")),
            ],
            options={
                "verbose_name": "قيد يومية",
                "verbose_name_plural": "قيود اليومية",
                "ordering": ["-entry_date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, unique=True, verbose_name="اسم المورد")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="رقم الهاتف")),
                ("notes", models.TextField(blank=True, verbose_name="ملاحظات")),
                ("is_active", models.BooleanField(default=True, verbose_name="مفعل")),
                (
                    "account",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="suppliers",
                        to="accounting.account",
                        verbose_name="حساب المورد",
                    ),
                ),
            ],
            options={
                "verbose_name": "مورد",
                "verbose_name_plural": "الموردون",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Treasury",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="اسم الخزينة")),
                ("opening_balance", models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name="الرصيد الافتتاحي")),
                ("is_active", models.BooleanField(default=True, verbose_name="مفعلة")),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="treasuries",
                        to="accounting.account",
                        verbose_name="حساب الخزينة",
                    ),
                ),
            ],
            options={
                "verbose_name": "خزينة",
                "verbose_name_plural": "الخزائن",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="JournalLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("debit", models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name="مدين")),
                ("credit", models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name="دائن")),
                ("description", models.CharField(blank=True, max_length=255, verbose_name="بيان السطر")),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="journal_lines",
                        to="accounting.account",
                        verbose_name="الحساب",
                    ),
                ),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="accounting.journalentry",
                        verbose_name="القيد",
                    ),
                ),
            ],
            options={
                "verbose_name": "سطر قيد",
                "verbose_name_plural": "سطور القيود",
            },
        ),
        migrations.CreateModel(
            name="CashTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_date", models.DateField(default=django.utils.timezone.localdate, verbose_name="التاريخ")),
                ("transaction_type", models.CharField(choices=[("in", "قبض"), ("out", "صرف")], max_length=5, verbose_name="نوع الحركة")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14, verbose_name="المبلغ")),
                ("description", models.CharField(max_length=255, verbose_name="البيان")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="وقت الإنشاء")),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cash_transactions",
                        to="accounting.account",
                        verbose_name="الحساب المقابل",
                    ),
                ),
                (
                    "journal_entry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cash_transactions",
                        to="accounting.journalentry",
                        verbose_name="قيد اليومية",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cash_transactions",
                        to="accounting.supplier",
                        verbose_name="المورد",
                    ),
                ),
                (
                    "treasury",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        to="accounting.treasury",
                        verbose_name="الخزينة",
                    ),
                ),
            ],
            options={
                "verbose_name": "حركة خزينة",
                "verbose_name_plural": "حركات الخزينة",
                "ordering": ["-transaction_date", "-id"],
            },
        ),
    ]
