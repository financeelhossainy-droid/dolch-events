from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum

from .models import Booking
from .forms import BookingForm, BookingServiceForm

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from django.conf import settings

from bidi.algorithm import get_display
import arabic_reshaper
import os


def booking_list(request):
    bookings = Booking.objects.select_related("client", "hall", "occasion_type").all()
    totals = bookings.aggregate(
        revenue=Sum("total_price"),
        paid=Sum("amount_paid"),
    )
    revenue = totals["revenue"] or 0
    paid = totals["paid"] or 0
    stats = {
        "bookings_count": bookings.count(),
        "confirmed_count": bookings.filter(status=Booking.BookingStatus.CONFIRMED).count(),
        "revenue": revenue,
        "remaining": revenue - paid,
    }
    return render(
        request,
        "bookings/booking_list.html",
        {
            "bookings": bookings,
            "stats": stats,
            "page_title": "لوحة الحجوزات",
        },
    )


def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            booking.refresh_totals(save=True)
            return redirect("booking_detail", booking_id=booking.id)
    else:
        form = BookingForm()

    return render(
        request,
        "bookings/booking_form.html",
        {
            "form": form,
            "title": "حجز جديد",
            "page_title": "حجز جديد",
        },
    )


def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    service_form = BookingServiceForm(booking=booking)

    if request.method == "POST":
        service_form = BookingServiceForm(request.POST, booking=booking)
        if service_form.is_valid():
            service_form.save()
            return redirect("booking_detail", booking_id=booking.id)

    services = booking.services.select_related("service").all()

    return render(
        request,
        "bookings/booking_detail.html",
        {
            "booking": booking,
            "services": services,
            "service_form": service_form,
            "page_title": f"حجز رقم {booking.id}",
        },
    )


def ar(text):
    text = "" if text is None else str(text)
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)


def format_money(value):
    try:
        return f"{float(value):,.2f} جنيه"
    except Exception:
        return str(value)


def format_date_ar(value):
    if not value:
        return ""
    try:
        return value.strftime("%d / %m / %Y")
    except Exception:
        return str(value)


def booking_pdf(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="contract_{pk}.pdf"'

    font_candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    font_path = next((path for path in font_candidates if os.path.exists(path)), None)
    font_name = "Helvetica"

    if font_path:
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
        font_name = "ArabicFont"

    primary = colors.HexColor("#0F5B78")
    gold = colors.HexColor("#C9A227")
    light_bg = colors.HexColor("#F7F7F7")

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    title_style = ParagraphStyle(
        "ArabicTitle",
        fontName=font_name,
        fontSize=20,
        leading=26,
        alignment=TA_RIGHT,
        textColor=primary,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ArabicSubtitle",
        fontName=font_name,
        fontSize=12,
        leading=18,
        alignment=TA_RIGHT,
        textColor=gold,
        spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "ArabicSection",
        fontName=font_name,
        fontSize=14,
        leading=20,
        alignment=TA_RIGHT,
        textColor=primary,
        spaceBefore=10,
        spaceAfter=8,
    )
    normal_style = ParagraphStyle(
        "ArabicNormal",
        fontName=font_name,
        fontSize=10,
        leading=16,
        alignment=TA_RIGHT,
    )

    def para(text, style=normal_style):
        return Paragraph(ar(text), style)

    table_style = TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), primary),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), light_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
    ])

    story = []
    logo_path = settings.BASE_DIR / "static" / "logo_farouk.png"
    if logo_path.exists():
        logo = Image(str(logo_path), width=2.2 * cm, height=2.2 * cm)
        logo.hAlign = "LEFT"
        story.append(logo)

    story.append(para("عقد حجز قاعة", title_style))
    story.append(para("قاعات مسجد الفاروق", subtitle_style))

    story.append(para("بيانات الحجز", section_style))
    booking_info = [
        [para("رقم الحجز"), para(booking.id), para("اسم العميل"), para(booking.client.name)],
        [para("رقم الهاتف"), para(booking.client.phone), para("القاعة"), para(str(booking.hall))],
        [para("نوع المناسبة"), para(str(booking.occasion_type)), para("مدة الحجز"), para(booking.get_duration_type_display())],
        [para("تاريخ الحجز"), para(format_date_ar(booking.booking_date)), para("تاريخ المناسبة"), para(format_date_ar(booking.occasion_date))],
        [para("اسم العريس / صاحب المناسبة"), para(booking.groom_name or "-"), para("الرقم القومي"), para(booking.groom_national_id or "-")],
        [para("العنوان"), para(booking.groom_address or "-"), para("اسم العروسة"), para(booking.bride_name or "-")],
        [para("الرقم القومي للعروسة"), para(booking.bride_national_id or "-"), para("عنوان العروسة"), para(booking.bride_address or "-")],
    ]
    info_table = Table(booking_info, colWidths=[3.2 * cm, 4.3 * cm, 3.2 * cm, 5.3 * cm])
    info_table.setStyle(table_style)
    story.append(info_table)

    story.append(para("تفاصيل الخدمات", section_style))
    services_data = [[para("الإجمالي"), para("الكمية"), para("سعر الوحدة"), para("الخدمة")]]

    for s in booking.services.all():
        services_data.append([
            para(format_money(s.line_total)),
            para(s.quantity),
            para(format_money(s.unit_price)),
            para(str(s.service)),
        ])

    if len(services_data) == 1:
        services_data.append([para("0.00 جنيه"), para("-"), para("-"), para("لا توجد خدمات إضافية")])

    services_table = Table(services_data, colWidths=[3.5 * cm, 2.5 * cm, 3.5 * cm, 7 * cm])
    services_table.setStyle(table_style)
    story.append(services_table)

    story.append(para("الملخص المالي", section_style))
    financial_data = [
        [para("البند"), para("القيمة")],
        [para("سعر القاعة"), para(format_money(booking.hall_price))],
        [para("إجمالي الخدمات"), para(format_money(booking.services_total))],
        [para("إجمالي العقد"), para(format_money(booking.total_price))],
        [para("المدفوع"), para(format_money(booking.amount_paid))],
        [para("المتبقي"), para(format_money(booking.remaining_amount))],
        [para("مقدم الحجز المطلوب"), para(format_money(booking.deposit_amount))],
    ]

    financial_table = Table(financial_data, colWidths=[8 * cm, 8 * cm])
    financial_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), gold),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), light_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(financial_table)

    story.append(para("شروط وأحكام الحجز", section_style))
    conditions = [
        "مقدم الحجز 25% بحد أدنى 3000 جنيه.",
        "يتم سداد كامل المبلغ قبل المناسبة بـ 7 أيام.",
        "في حالة الإلغاء قبل أكثر من 30 يوم يتم خصم 500 جنيه.",
        "في حالة الإلغاء أقل من 30 يوم يتم خصم 25% من قيمة الحجز.",
        "في حالة الإلغاء من 15 يوم فأقل يتم خصم 50% من قيمة الحجز.",
        "في حالة الإلغاء من أسبوع فأقل يتم خصم 100% من قيمة الحجز.",
    ]

    for c in conditions:
        story.append(para(f"- {c}"))

    story.append(Spacer(1, 1.2 * cm))
    signature_data = [[para("توقيع العميل", normal_style), para("توقيع الإدارة", normal_style)]]
    signature_table = Table(signature_data, colWidths=[8 * cm, 8 * cm])
    signature_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(signature_table)

    doc.build(story)
    return response
