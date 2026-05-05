from decimal import Decimal

from django.db import models
from django.utils import timezone


class Account(models.Model):
    class AccountType(models.TextChoices):
        ASSET = "asset", "أصول"
        LIABILITY = "liability", "التزامات"
        EQUITY = "equity", "حقوق ملكية"
        REVENUE = "revenue", "إيرادات"
        EXPENSE = "expense", "مصروفات وتكاليف"
        OTHER = "other", "أخرى"

    code = models.CharField(max_length=30, unique=True, verbose_name="كود الحساب")
    name_ar = models.CharField(max_length=180, verbose_name="اسم الحساب عربي")
    name_en = models.CharField(max_length=180, blank=True, verbose_name="اسم الحساب إنجليزي")
    main_account_ar = models.CharField(max_length=180, blank=True, verbose_name="الحساب الرئيسي عربي")
    main_account_en = models.CharField(max_length=180, blank=True, verbose_name="الحساب الرئيسي إنجليزي")
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.OTHER,
        verbose_name="نوع الحساب",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="الحساب الأب",
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "حساب"
        verbose_name_plural = "شجرة الحسابات"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name_ar}"

    @property
    def level(self):
        return len([part for part in self.code.split("-") if part])

    @classmethod
    def infer_type(cls, code):
        first = str(code or "").strip()[:1]
        return {
            "1": cls.AccountType.ASSET,
            "2": cls.AccountType.LIABILITY,
            "3": cls.AccountType.EXPENSE,
            "4": cls.AccountType.REVENUE,
            "5": cls.AccountType.EQUITY,
        }.get(first, cls.AccountType.OTHER)


class Treasury(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="اسم الخزينة")
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="treasuries",
        verbose_name="حساب الخزينة",
    )
    opening_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="الرصيد الافتتاحي",
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعلة")

    class Meta:
        verbose_name = "خزينة"
        verbose_name_plural = "الخزائن"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def current_balance(self):
        incoming = self.transactions.filter(transaction_type=CashTransaction.TransactionType.IN).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")
        outgoing = self.transactions.filter(transaction_type=CashTransaction.TransactionType.OUT).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")
        return self.opening_balance + incoming - outgoing


class Supplier(models.Model):
    name = models.CharField(max_length=160, unique=True, verbose_name="اسم المورد")
    phone = models.CharField(max_length=30, blank=True, verbose_name="رقم الهاتف")
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="suppliers",
        verbose_name="حساب المورد",
    )
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="مفعل")

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردون"
        ordering = ["name"]

    def __str__(self):
        return self.name


class JournalEntry(models.Model):
    class EntryStatus(models.TextChoices):
        DRAFT = "draft", "مسودة"
        POSTED = "posted", "مرحل"
        CANCELLED = "cancelled", "ملغي"

    entry_date = models.DateField(default=timezone.localdate, verbose_name="تاريخ القيد")
    reference = models.CharField(max_length=80, blank=True, verbose_name="مرجع")
    description = models.CharField(max_length=255, verbose_name="البيان")
    status = models.CharField(
        max_length=15,
        choices=EntryStatus.choices,
        default=EntryStatus.DRAFT,
        verbose_name="الحالة",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإنشاء")

    class Meta:
        verbose_name = "قيد يومية"
        verbose_name_plural = "قيود اليومية"
        ordering = ["-entry_date", "-id"]

    def __str__(self):
        return f"قيد #{self.pk} - {self.entry_date}"

    @property
    def total_debit(self):
        return self.lines.aggregate(total=models.Sum("debit"))["total"] or Decimal("0")

    @property
    def total_credit(self):
        return self.lines.aggregate(total=models.Sum("credit"))["total"] or Decimal("0")

    @property
    def is_balanced(self):
        return self.total_debit == self.total_credit


class JournalLine(models.Model):
    entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="القيد",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="journal_lines",
        verbose_name="الحساب",
    )
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="مدين")
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="دائن")
    description = models.CharField(max_length=255, blank=True, verbose_name="بيان السطر")

    class Meta:
        verbose_name = "سطر قيد"
        verbose_name_plural = "سطور القيود"

    def __str__(self):
        return f"{self.account} | مدين {self.debit} | دائن {self.credit}"


class CashTransaction(models.Model):
    class TransactionType(models.TextChoices):
        IN = "in", "قبض"
        OUT = "out", "صرف"

    treasury = models.ForeignKey(
        Treasury,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="الخزينة",
    )
    transaction_date = models.DateField(default=timezone.localdate, verbose_name="التاريخ")
    transaction_type = models.CharField(
        max_length=5,
        choices=TransactionType.choices,
        verbose_name="نوع الحركة",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="المبلغ")
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="cash_transactions",
        verbose_name="الحساب المقابل",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cash_transactions",
        verbose_name="المورد",
    )
    description = models.CharField(max_length=255, verbose_name="البيان")
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cash_transactions",
        verbose_name="قيد اليومية",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإنشاء")

    class Meta:
        verbose_name = "حركة خزينة"
        verbose_name_plural = "حركات الخزينة"
        ordering = ["-transaction_date", "-id"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.treasury}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.journal_entry_id:
            from .services import post_cash_transaction

            post_cash_transaction(self)


class AccountingDetermination(models.Model):
    class EventType(models.TextChoices):
        BOOKING_DEPOSIT = "booking_deposit", "مقدم حجز"
        BOOKING_REVENUE = "booking_revenue", "إيراد حجز"
        SERVICE_REVENUE = "service_revenue", "إيراد خدمة إضافية"
        RECEIVABLE = "receivable", "عميل / ذمم مدينة"
        SUPPLIER_INVOICE = "supplier_invoice", "فاتورة مورد"
        CASH_IN = "cash_in", "قبض نقدي"
        CASH_OUT = "cash_out", "صرف نقدي"
        INVENTORY_PURCHASE = "inventory_purchase", "شراء مخزون"
        COST_OF_SERVICE = "cost_of_service", "تكلفة خدمة"

    event_type = models.CharField(
        max_length=40,
        choices=EventType.choices,
        unique=True,
        verbose_name="الحدث المحاسبي",
    )
    debit_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="determination_debits",
        verbose_name="حساب المدين الافتراضي",
    )
    credit_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="determination_credits",
        verbose_name="حساب الدائن الافتراضي",
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تحديد محاسبي"
        verbose_name_plural = "Accounting Determination"
        ordering = ["event_type"]

    def __str__(self):
        return self.get_event_type_display()
