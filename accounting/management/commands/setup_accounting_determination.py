from django.core.management.base import BaseCommand, CommandError

from accounting.models import Account, AccountingDetermination, Treasury


ACCOUNT_MAP = {
    "cash": "1-2-1-1-1",
    "receivable": "1-2-3-1-1",
    "clients": "1-2-11-1-2",
    "deferred_revenue": "2-2-2-3-1",
    "suppliers": "2-3-1-1-1",
    "inventory_food": "1-2-5-1-1",
    "inventory_packaging": "1-2-5-1-2",
    "service_expense": "3-1-1-8-1",
    "event_consumption": "3-1-1-1-4",
    "hall_revenue": "4-1-1-1-1",
    "service_revenue": "4-1-1-1-12",
}


DETERMINATIONS = [
    (
        AccountingDetermination.EventType.BOOKING_DEPOSIT,
        "cash",
        "deferred_revenue",
        "عند تحصيل مقدم حجز: مدين الخزينة، دائن إيرادات مؤجلة حتى إتمام المناسبة.",
    ),
    (
        AccountingDetermination.EventType.BOOKING_REVENUE,
        "receivable",
        "hall_revenue",
        "عند إثبات إيراد القاعة: مدين العملاء/الاستكمال، دائن إيرادات القاعة.",
    ),
    (
        AccountingDetermination.EventType.SERVICE_REVENUE,
        "receivable",
        "service_revenue",
        "عند إثبات إيراد الأوبشنز: مدين العملاء/الاستكمال، دائن إيرادات الخدمات.",
    ),
    (
        AccountingDetermination.EventType.RECEIVABLE,
        "receivable",
        "hall_revenue",
        "ذمم مدينة للحجوزات عند وجود مبلغ متبقي على العميل.",
    ),
    (
        AccountingDetermination.EventType.SUPPLIER_INVOICE,
        "service_expense",
        "suppliers",
        "فاتورة مورد تشغيلية: مدين مصروف خدمة، دائن الموردين.",
    ),
    (
        AccountingDetermination.EventType.CASH_IN,
        "cash",
        "receivable",
        "قبض نقدي: مدين الخزينة، دائن الحساب المقابل المختار في الحركة.",
    ),
    (
        AccountingDetermination.EventType.CASH_OUT,
        "service_expense",
        "cash",
        "صرف نقدي: مدين الحساب المقابل المختار في الحركة، دائن الخزينة.",
    ),
    (
        AccountingDetermination.EventType.INVENTORY_PURCHASE,
        "inventory_food",
        "suppliers",
        "شراء مخزون: مدين المخزون، دائن الموردين.",
    ),
    (
        AccountingDetermination.EventType.COST_OF_SERVICE,
        "event_consumption",
        "inventory_food",
        "استهلاك مخزون على مناسبة: مدين تكلفة المناسبات، دائن المخزون.",
    ),
]


class Command(BaseCommand):
    help = "Setup reviewed default accounting determination from the imported COA."

    def handle(self, *args, **options):
        accounts = {}
        missing = []

        for key, code in ACCOUNT_MAP.items():
            account = Account.objects.filter(code=code).first()
            if not account:
                missing.append(f"{key}: {code}")
            accounts[key] = account

        if missing:
            raise CommandError("Missing required COA accounts: " + ", ".join(missing))

        Treasury.objects.update_or_create(
            name="الخزينة الرئيسية",
            defaults={
                "account": accounts["cash"],
                "opening_balance": 0,
                "is_active": True,
            },
        )

        created = 0
        updated = 0
        for event_type, debit_key, credit_key, notes in DETERMINATIONS:
            _, was_created = AccountingDetermination.objects.update_or_create(
                event_type=event_type,
                defaults={
                    "debit_account": accounts[debit_key],
                    "credit_account": accounts[credit_key],
                    "is_active": True,
                    "notes": notes,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Accounting determination ready. Created: {created}, Updated: {updated}. Treasury ensured: الخزينة الرئيسية"
        ))
