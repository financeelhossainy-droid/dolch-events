from django.shortcuts import redirect, render


MODULES = {
    "ar": {
        "modules": {
            "title": "مركز العمل",
            "subtitle": "تطبيقات Dolch ERP الرئيسية في مكان واحد",
            "items": [
                ("الحجوزات", "لوحة الحجوزات، حجز جديد، والكاليندر", "bookings_workspace"),
                ("الحسابات", "شجرة الحسابات، الخزينة، الموردين، والقيود", "accounting_module"),
                ("المشتريات", "طلبات الشراء وفواتير الموردين", "purchases_module"),
                ("المخازن", "الأصناف، الكميات، وحركات الصرف والإضافة", "inventory_module"),
                ("التكاليف", "تكلفة الخدمات والمنتجات وربحية كل حجز", "costing_module"),
                ("التقارير", "التقارير المالية والتشغيلية وفترات العقود", "reports_module"),
                ("الإعدادات", "Master Data و Accounting Determination وإدارة النظام", "configuration_module"),
            ],
        },
        "bookings": {
            "title": "الحجوزات",
            "subtitle": "إدارة دورة الحجز من الطلب إلى العقد والكاليندر",
            "items": [
                ("لوحة الحجوزات", "جدول الحجوزات والإيرادات والمتبقي للتحصيل", "booking_list"),
                ("حجز جديد", "إنشاء حجز وعميل جديد وتحديد الموعد", "booking_create"),
                ("كاليندر الحجوزات", "معرفة المواعيد المتاحة ومنع التعارض", "booking_calendar"),
            ],
        },
        "configuration": {
            "title": "الإعدادات",
            "subtitle": "إعداد البيانات الأساسية وربط الحسابات الافتراضية",
            "items": [
                ("البيانات الأساسية", "القاعات والخدمات والأسعار والعملاء والموردين", "master_data"),
                ("التحديد المحاسبي", "تحديد الحسابات الافتراضية للقيود التلقائية", "accounting_determination_list"),
                ("إدارة النظام", "إدارة الجداول الخام والصلاحيات", "admin:index"),
            ],
        },
        "accounting": {
            "title": "الحسابات",
            "subtitle": "شجرة الحسابات والخزينة والموردين والقيود",
            "items": [
                ("شجرة الحسابات", "استيراد وتصنيف حسابات COA من ملف Excel", "account_list"),
                ("الخزينة", "يومية الخزينة، قبض وصرف، أرصدة يومية", "treasury_list"),
                ("الموردين", "أرصدة الموردين وفواتير مستحقة", "supplier_list"),
                ("قيود اليومية", "قيود تلقائية للحجوزات وقيود يدوية", "journal_entry_list"),
                ("مراكز التكلفة", "ربط التكلفة بالحجز أو القاعة أو نوع المناسبة", None),
                ("التقارير المالية", "ميزان مراجعة، قائمة دخل، مركز مالي", None),
            ],
        },
        "purchases": {
            "title": "المشتريات",
            "subtitle": "إدارة طلبات الشراء وفواتير الموردين",
            "items": [
                ("طلبات شراء", "تجميع احتياجات القاعات والخدمات", None),
                ("فواتير موردين", "ربط الفاتورة بالمورد والمخزن والتكلفة", None),
                ("مصروفات تشغيل", "تحميل المصروف على مركز تكلفة مناسب", None),
            ],
        },
        "inventory": {
            "title": "المخازن",
            "subtitle": "متابعة الأصناف والكميات وحركات المخزن",
            "items": [
                ("الأصناف", "منتجات وخامات قابلة للصرف على المناسبات", None),
                ("إضافة مخزنية", "استلام مشتريات أو تسوية إضافة", None),
                ("صرف مخزني", "صرف خامات وخدمات على حجز أو تكلفة", None),
            ],
        },
        "costing": {
            "title": "التكاليف",
            "subtitle": "حساب تكلفة الخدمات والمنتجات وربحية الحجز",
            "items": [
                ("تكلفة الخدمة", "تكلفة الوحدة لكل خدمة إضافية", None),
                ("تكلفة المنتج", "تكلفة الخامات أو الأصناف المستخدمة", None),
                ("ربحية الحجز", "إيراد الحجز ناقص الخدمات والمشتريات والتكاليف", None),
            ],
        },
        "reports": {
            "title": "التقارير",
            "subtitle": "تقارير مالية وتشغيلية قابلة للتصفية بالفترة والبند",
            "items": [
                ("يومية الخزينة", "حركات قبض وصرف خلال فترة", None),
                ("عقود فترة معينة", "إجمالي العقود وبنود الخدمات", None),
                ("تقرير الاستكمالات", "المبالغ المتبقية والمواعيد المطلوب تحصيلها", None),
                ("تقارير مالية", "ميزان مراجعة وقائمة دخل ومركز مالي", None),
            ],
        },
    },
    "en": {
        "modules": {
            "title": "Work Center",
            "subtitle": "Dolch ERP applications in one place",
            "items": [
                ("Bookings", "Booking board, new booking, and calendar", "bookings_workspace"),
                ("Accounting", "Chart of accounts, treasury, suppliers, and journals", "accounting_module"),
                ("Purchasing", "Purchase requests and supplier invoices", "purchases_module"),
                ("Inventory", "Items, quantities, and stock movements", "inventory_module"),
                ("Costing", "Service and product costs with booking profitability", "costing_module"),
                ("Reports", "Financial and operational reports", "reports_module"),
                ("Configuration", "Master Data, Accounting Determination, and system admin", "configuration_module"),
            ],
        },
        "bookings": {
            "title": "Bookings",
            "subtitle": "Manage booking lifecycle from request to contract and calendar",
            "items": [
                ("Booking Board", "Bookings table, revenue, and remaining balances", "booking_list"),
                ("New Booking", "Create a booking, client, and time slot", "booking_create"),
                ("Booking Calendar", "Check availability and prevent time conflicts", "booking_calendar"),
            ],
        },
        "configuration": {
            "title": "Configuration",
            "subtitle": "Master data and default accounting setup",
            "items": [
                ("Master Data", "Halls, services, prices, clients, and suppliers", "master_data"),
                ("Accounting Determination", "Default accounts for automated journal entries", "accounting_determination_list"),
                ("Django Admin", "Raw data and permissions management", "admin:index"),
            ],
        },
        "accounting": {
            "title": "Accounting",
            "subtitle": "Chart of accounts, treasury, suppliers, and journals",
            "items": [
                ("Chart of Accounts", "Imported and classified COA accounts", "account_list"),
                ("Treasury", "Cash in/out and daily balances", "treasury_list"),
                ("Suppliers", "Supplier balances and payables", "supplier_list"),
                ("Journal Entries", "Manual and future automated journals", "journal_entry_list"),
                ("Cost Centers", "Connect costs to bookings, halls, and occasions", None),
                ("Financial Reports", "Trial balance, income statement, and balance sheet", None),
            ],
        },
        "purchases": {
            "title": "Purchasing",
            "subtitle": "Purchase requests and supplier invoices",
            "items": [
                ("Purchase Requests", "Collect operational purchasing needs", None),
                ("Supplier Invoices", "Connect invoices to suppliers, inventory, and costs", None),
                ("Operating Expenses", "Assign expenses to cost centers", None),
            ],
        },
        "inventory": {
            "title": "Inventory",
            "subtitle": "Track items, quantities, and stock movements",
            "items": [
                ("Items", "Products and consumables used in events", None),
                ("Stock Receipt", "Purchase receipts or stock adjustments", None),
                ("Stock Issue", "Issue materials to bookings or cost centers", None),
            ],
        },
        "costing": {
            "title": "Costing",
            "subtitle": "Calculate service and product costs with profitability",
            "items": [
                ("Service Cost", "Unit cost for every service option", None),
                ("Product Cost", "Material and item cost tracking", None),
                ("Booking Profitability", "Booking revenue minus service and material costs", None),
            ],
        },
        "reports": {
            "title": "Reports",
            "subtitle": "Financial and operational period reports",
            "items": [
                ("Cash Journal", "Cash in/out movements by period", None),
                ("Contracts by Period", "Contracts totals and service breakdowns", None),
                ("Completion Report", "Remaining amounts and due follow-ups", None),
                ("Financial Reports", "Trial balance, income statement, and balance sheet", None),
            ],
        },
    },
}


def get_lang(request):
    return request.session.get("ui_lang", "ar")


def get_module(request, key):
    return MODULES[get_lang(request)][key]


def render_module(request, key):
    module = get_module(request, key)
    return render(request, "core/module_page.html", {"page_title": module["title"], "module": module})


def switch_language(request, lang):
    request.session["ui_lang"] = "en" if lang == "en" else "ar"
    return redirect(request.META.get("HTTP_REFERER") or "module_hub")


def module_hub(request):
    return render_module(request, "modules")


def bookings_workspace(request):
    return render_module(request, "bookings")


def configuration_module(request):
    return render_module(request, "configuration")


def accounting_module(request):
    return render_module(request, "accounting")


def calendar_module(request):
    return redirect("booking_calendar")


def purchases_module(request):
    return render_module(request, "purchases")


def inventory_module(request):
    return render_module(request, "inventory")


def costing_module(request):
    return render_module(request, "costing")


def reports_module(request):
    return render_module(request, "reports")
