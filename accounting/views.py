from django.db.models import Count, Sum
from django.shortcuts import render

from .models import Account, AccountingDetermination, CashTransaction, JournalEntry, Supplier, Treasury


def account_list(request):
    accounts = Account.objects.all()
    stats = accounts.aggregate(total=Count("id"))
    return render(
        request,
        "accounting/account_list.html",
        {
            "page_title": "شجرة الحسابات",
            "accounts": accounts,
            "stats": stats,
        },
    )


def treasury_list(request):
    treasuries = Treasury.objects.select_related("account").all()
    transactions = CashTransaction.objects.select_related("treasury", "account", "supplier")[:50]
    totals = CashTransaction.objects.aggregate(total=Sum("amount"))
    return render(
        request,
        "accounting/treasury_list.html",
        {
            "page_title": "الخزينة",
            "treasuries": treasuries,
            "transactions": transactions,
            "totals": totals,
        },
    )


def supplier_list(request):
    suppliers = Supplier.objects.select_related("account").all()
    return render(
        request,
        "accounting/supplier_list.html",
        {
            "page_title": "الموردون",
            "suppliers": suppliers,
        },
    )


def journal_entry_list(request):
    entries = JournalEntry.objects.prefetch_related("lines__account").all()
    return render(
        request,
        "accounting/journal_entry_list.html",
        {
            "page_title": "قيود اليومية",
            "entries": entries,
        },
    )


def accounting_determination_list(request):
    determinations = AccountingDetermination.objects.select_related("debit_account", "credit_account").all()
    process_notes = [
        ("مقدم حجز", "مدين الخزينة / دائن إيرادات مؤجلة"),
        ("إثبات إيراد القاعة", "مدين العملاء / دائن إيرادات القاعة"),
        ("إثبات إيراد الخدمات", "مدين العملاء / دائن إيرادات الخدمات"),
        ("قبض نقدي", "مدين الخزينة / دائن الحساب المقابل في حركة القبض"),
        ("صرف نقدي", "مدين الحساب المقابل في حركة الصرف / دائن الخزينة"),
        ("فاتورة مورد", "مدين مصروف أو تكلفة / دائن الموردين"),
        ("شراء مخزون", "مدين المخزون / دائن الموردين"),
        ("استهلاك مخزون", "مدين تكلفة المناسبة / دائن المخزون"),
    ]
    return render(
        request,
        "accounting/accounting_determination_list.html",
        {
            "page_title": "Accounting Determination",
            "determinations": determinations,
            "process_notes": process_notes,
        },
    )


def master_data(request):
    cards = [
        ("القاعات", "القاعات المتاحة للحجز", "/admin/core/hall/"),
        ("أنواع المناسبات", "فرح، كتب كتاب، عزاء، عقيقة، اجتماع", "/admin/core/occasiontype/"),
        ("الخدمات", "الخدمات الرئيسية والإضافية", "/admin/core/service/"),
        ("أسعار الإيجار", "أسعار القاعة حسب المناسبة والمدة", "/admin/core/mainserviceprice/"),
        ("أسعار الخدمات الإضافية", "أسعار تختلف حسب القاعة", "/admin/core/extraserviceprice/"),
        ("أسعار ثابتة", "خدمات ثابتة السعر", "/admin/core/fixedserviceprice/"),
        ("العملاء", "بيانات العملاء وأرقام التواصل", "/admin/bookings/client/"),
        ("الموردون", "بيانات الموردين وربطهم بالحسابات", "/admin/accounting/supplier/"),
        ("الخزائن", "الخزائن وربطها بحسابات النقدية", "/admin/accounting/treasury/"),
    ]
    return render(
        request,
        "accounting/master_data.html",
        {
            "page_title": "Master Data",
            "cards": cards,
        },
    )
