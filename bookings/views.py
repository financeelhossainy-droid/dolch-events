from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import Booking
from .forms import BookingForm, BookingServiceForm

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm

from bidi.algorithm import get_display
import arabic_reshaper
import os


def booking_list(request):
    bookings = Booking.objects.select_related("client", "hall", "occasion_type").all()
    return render(request, "bookings/booking_list.html", {"bookings": bookings})


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
    response["Content-Disposition"] = f'attachment; filename="contract_{pk}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # فونت عربي
    font_path = r"C:\Windows\Fonts\arial.ttf"
    if not os.path.exists(font_path):
        font_path = r"C:\Windows\Fonts\tahoma.ttf"

    pdfmetrics.registerFont(TTFont("ArabicFont", font_path))

    # ألوان
    primary = colors.HexColor("#0F5B78")
    gold = colors.HexColor("#C9A227")
    light_bg = colors.HexColor("#F7F7F7")

    # هوامش
    right_margin = width - 40
    left_margin = 40
    y = height - 40

    # اللوجو
    logo_path = r"D:\Hall\system\static\logo_farouk.png"
    if os.path.exists(logo_path):
        p.drawImage(
            logo_path,
            left_margin,
            height - 95,
            width=70,
            height=70,
            preserveAspectRatio=True,
            mask="auto",
        )

    # عنوان العقد
    p.setFont("ArabicFont", 20)
    p.setFillColor(primary)
    p.drawRightString(right_margin, y, ar("عقد حجز قاعة"))
    y -= 28

    p.setFont("ArabicFont", 14)
    p.setFillColor(gold)
    p.drawRightString(right_margin, y, ar("قاعات مسجد الفاروق"))
    y -= 35

    # خط فاصل
    p.setStrokeColor(primary)
    p.setLineWidth(1)
    p.line(left_margin, y, right_margin, y)
    y -= 35

    # جدول بيانات الحجز
    booking_info = [
        [ar("رقم الحجز"), ar(booking.id), ar("اسم العميل"), ar(booking.client.name)],
        [ar("رقم الهاتف"), ar(booking.client.phone), ar("القاعة"), ar(str(booking.hall))],
        [ar("نوع المناسبة"), ar(str(booking.occasion_type)), ar("مدة الحجز"), ar(booking.get_duration_type_display())],
        [ar("تاريخ الحجز"), ar(format_date_ar(booking.booking_date)), ar("تاريخ المناسبة"), ar(format_date_ar(booking.occasion_date))],
        [ar("اسم العريس"), ar(booking.groom_name), ar("الرقم القومي"), ar(booking.groom_national_id)],
        [ar("عنوان العريس"), ar(booking.groom_address), ar("اسم العروسة"), ar(booking.bride_name)],
        [ar("الرقم القومي للعروسة"), ar(booking.bride_national_id), ar("عنوان العروسة"), ar(booking.bride_address)],
    ]

    info_table = Table(booking_info, colWidths=[3.2 * cm, 4.3 * cm, 3.2 * cm, 5.3 * cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "ArabicFont"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), light_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    info_table_width, info_table_height = info_table.wrap(0, 0)
    info_table.drawOn(p, left_margin, y - info_table_height)
    y = y - info_table_height - 25

    # عنوان الخدمات
    p.setFillColor(primary)
    p.setFont("ArabicFont", 15)
    p.drawRightString(right_margin, y, ar("تفاصيل الخدمات"))
    y -= 20

    services_data = [[ar("الإجمالي"), ar("الكمية"), ar("سعر الوحدة"), ar("الخدمة")]]

    for s in booking.services.all():
        services_data.append([
            ar(format_money(s.line_total)),
            ar(s.quantity),
            ar(format_money(s.unit_price)),
            ar(str(s.service)),
        ])

    if len(services_data) == 1:
        services_data.append([ar("0.00"), ar("-"), ar("-"), ar("لا توجد خدمات إضافية")])

    services_table = Table(services_data, colWidths=[3.5 * cm, 2.5 * cm, 3.5 * cm, 7 * cm])
    services_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "ArabicFont"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
    ]))

    services_table_width, services_table_height = services_table.wrap(0, 0)

    # لو المساحة لا تكفي للخدمات، افتح صفحة جديدة
    if y - services_table_height < 120:
        p.showPage()
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
        y = height - 50

    p.setFillColor(primary)
    p.setFont("ArabicFont", 15)
    p.drawRightString(right_margin, y, ar("تفاصيل الخدمات"))
    y -= 20

    services_table.drawOn(p, left_margin, y - services_table_height)
    y = y - services_table_height - 30

    # لو المساحة لا تكفي للملخص المالي، افتح صفحة جديدة
    if y < 260:
        p.showPage()
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
        y = height - 50

    # الملخص المالي
    p.setFillColor(primary)
    p.setFont("ArabicFont", 15)
    p.drawRightString(right_margin, y, ar("الملخص المالي"))
    y -= 20

    financial_data = [
        [ar("البند"), ar("القيمة")],
        [ar("سعر القاعة"), ar(format_money(booking.hall_price))],
        [ar("إجمالي الخدمات"), ar(format_money(booking.services_total))],
        [ar("إجمالي العقد"), ar(format_money(booking.total_price))],
        [ar("المدفوع"), ar(format_money(booking.amount_paid))],
        [ar("المتبقي"), ar(format_money(booking.remaining_amount))],
        [ar("مقدم الحجز المطلوب"), ar(format_money(booking.deposit_amount))],
    ]

    financial_table = Table(financial_data, colWidths=[8 * cm, 8 * cm])
    financial_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), gold),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "ArabicFont"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), light_bg),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    financial_table_width, financial_table_height = financial_table.wrap(0, 0)
    financial_table.drawOn(p, left_margin, y - financial_table_height)
    y = y - financial_table_height - 25

    # لو المساحة لا تكفي للشروط، افتح صفحة جديدة
    if y < 180:
        p.showPage()
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
        y = height - 50

    # الشروط
    p.setFillColor(primary)
    p.setFont("ArabicFont", 15)
    p.drawRightString(right_margin, y, ar("شروط وأحكام الحجز"))
    y -= 22

    p.setFillColor(colors.black)
    p.setFont("ArabicFont", 11)

    conditions = [
        "مقدم الحجز 25% بحد أدنى 3000 جنيه.",
        "يتم سداد كامل المبلغ قبل المناسبة بـ 7 أيام.",
        "في حالة الإلغاء قبل أكثر من 30 يوم يتم خصم 500 جنيه.",
        "في حالة الإلغاء أقل من 30 يوم يتم خصم 25% من قيمة الحجز.",
        "في حالة الإلغاء من 15 يوم فأقل يتم خصم 50% من قيمة الحجز.",
        "في حالة الإلغاء من أسبوع فأقل يتم خصم 100% من قيمة الحجز.",
    ]

    for c in conditions:
        p.drawRightString(right_margin, y, ar(f"- {c}"))
        y -= 18

    y -= 25

    # لو المساحة لا تكفي للتوقيعات، افتح صفحة جديدة
    if y < 80:
        p.showPage()
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
        y = height - 80

    # التوقيعات
    p.setStrokeColor(colors.black)
    p.line(left_margin + 20, y, left_margin + 180, y)
    p.line(right_margin - 180, y, right_margin - 20, y)

    y -= 18
    p.setFont("ArabicFont", 12)
    p.drawString(left_margin + 55, y, ar("توقيع العميل"))
    p.drawRightString(right_margin - 55, y, ar("توقيع الإدارة"))

    p.save()
    return response