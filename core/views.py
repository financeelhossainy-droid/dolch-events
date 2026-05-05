from django.shortcuts import redirect, render

MODULES = {
    "modules": {
        "title": "مركز الموديولز",
        "subtitle": "نظرة عامة على أقسام نظام Dolch Events",
        "items": [
            ("الحجوزات", "إدارة الحجوزات والعقود والخدمات", "booking_list"),
            ("الحسابات", "الخزينة، الموردين، القيود وشجرة الحسابات", "accounting_module"),
            ("الكاليندر", "مراجعة الأيام المتاحة وتخطيط الحجوزات", "calendar_module"),
            ("المشتريات", "طلبات الشراء وفواتير الموردين", "purchases_module"),
            ("المخازن", "الأصناف، الكميات، وحركات الصرف والإضافة", "inventory_module"),
            ("التكاليف", "تكلفة الخدمات والمنتجات وربحية كل حجز", "costing_module"),
            ("التقارير", "التقارير المالية والتشغيلية وفترات العقود", "reports_module"),
        ],
    },
    "accounting": {
        "title": "الحسابات",
        "subtitle": "تجهيز شجرة الحسابات والخزينة والموردين والقيود",
        "items": [
            ("شجرة الحسابات", "استيراد وتصنيف حسابات COA من ملف Excel", "account_list"),
            ("Master Data", "القاعات والخدمات والأسعار والعملاء والموردين", "master_data"),
            ("Accounting Determination", "تحديد الحسابات الافتراضية للقيود التلقائية", "accounting_determination_list"),
            ("الخزينة", "يومية الخزينة، قبض وصرف، أرصدة يومية", "treasury_list"),
            ("الموردين", "أرصدة الموردين وفواتير مستحقة", "supplier_list"),
            ("قيود اليومية", "قيود تلقائية للحجوزات وقيود يدوية", "journal_entry_list"),
            ("مراكز التكلفة", "ربط التكلفة بالحجز أو القاعة أو نوع المناسبة", None),
            ("التقارير المالية", "ميزان مراجعة، قائمة دخل، مركز مالي", None),
        ],
    },
    "calendar": {
        "title": "الكاليندر والحجز أونلاين",
        "subtitle": "معرفة المواعيد الفارغة وتجهيز طلبات الحجز من العميل",
        "items": [
            ("تقويم الحجوزات", "عرض اليوم والأسبوع والشهر حسب القاعة", None),
            ("بحث عن موعد فاضي", "اختيار تاريخ وقاعة ونوع مناسبة", None),
            ("طلبات أونلاين", "استقبال طلب حجز مبدئي للمراجعة", None),
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
}


def module_hub(request):
    return render(request, "core/module_page.html", {"page_title": MODULES["modules"]["title"], "module": MODULES["modules"]})


def accounting_module(request):
    return render(request, "core/module_page.html", {"page_title": MODULES["accounting"]["title"], "module": MODULES["accounting"]})


def calendar_module(request):
    return redirect("booking_calendar")


def purchases_module(request):
    return render(request, "core/module_page.html", {"page_title": MODULES["purchases"]["title"], "module": MODULES["purchases"]})


def inventory_module(request):
    return render(request, "core/module_page.html", {"page_title": MODULES["inventory"]["title"], "module": MODULES["inventory"]})


def costing_module(request):
    return render(request, "core/module_page.html", {"page_title": MODULES["costing"]["title"], "module": MODULES["costing"]})


def reports_module(request):
    return render(request, "core/module_page.html", {"page_title": MODULES["reports"]["title"], "module": MODULES["reports"]})
