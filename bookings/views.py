from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from .models import Booking
from .forms import BOOKING_TIME_CHOICES, EXTRA_TIME_CHOICES, BookingForm, BookingServiceForm
from .services import confirm_and_post_booking
from core.models import Hall

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


@login_required(login_url="/admin/login/")
@permission_required("bookings.can_confirm_booking", login_url="/admin/login/", raise_exception=True)
def booking_confirm(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method != "POST":
        return redirect("booking_detail", booking_id=booking.id)

    try:
        entry = confirm_and_post_booking(booking, request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"تم تأكيد العقد وترحيله إلى قيد يومية رقم {entry.id}.")
    return redirect("booking_detail", booking_id=booking.id)


def booking_calendar(request):
    selected_date = request.GET.get("date")
    hall_id = request.GET.get("hall")
    selected_time = request.GET.get("start_time") or "11:00"
    selected_duration = request.GET.get("duration_type") or Booking.DurationType.ONE_HOUR
    selected_extra_minutes = int(request.GET.get("extra_minutes") or 0)

    if selected_date:
        try:
            from datetime import date
            selected_date = date.fromisoformat(selected_date)
        except ValueError:
            selected_date = None

    if selected_date is None:
        from django.utils import timezone
        selected_date = timezone.localdate()

    start_date = selected_date - timedelta(days=3)
    days = [start_date + timedelta(days=i) for i in range(7)]
    halls = Hall.objects.filter(is_active=True).order_by("name")
    bookings = Booking.objects.select_related("client", "hall", "occasion_type").filter(
        occasion_date__in=days
    ).exclude(status=Booking.BookingStatus.CANCELLED)

    if hall_id:
        bookings = bookings.filter(hall_id=hall_id)

    calendar_days = []
    for day in days:
        day_bookings = [booking for booking in bookings if booking.occasion_date == day]
        calendar_days.append({
            "date": day,
            "bookings": day_bookings,
            "is_selected": day == selected_date,
        })

    selected_day_bookings = []
    for day_data in calendar_days:
        if day_data["is_selected"]:
            selected_day_bookings = day_data["bookings"]
            break
    selected_start_time = datetime.strptime(selected_time, "%H:%M").time()
    selected_minutes = {
        Booking.DurationType.ONE_HOUR: 60,
        Booking.DurationType.TWO_HOURS: 120,
        Booking.DurationType.PHOTO_VIDEO_ZAFFA_OFFER: 90,
    }.get(selected_duration, 60) + selected_extra_minutes
    selected_start = datetime.combine(selected_date, selected_start_time)
    selected_end = selected_start + timedelta(minutes=selected_minutes)

    busy_hall_ids = set()
    for booking in selected_day_bookings:
        booking_start, booking_end = booking.booking_interval()
        if selected_start < booking_end and selected_end > booking_start:
            busy_hall_ids.add(booking.hall_id)
    available_halls = [hall for hall in halls if hall.id not in busy_hall_ids]

    return render(
        request,
        "bookings/booking_calendar.html",
        {
            "page_title": "كاليندر الحجوزات",
            "calendar_days": calendar_days,
            "selected_date": selected_date,
            "halls": halls,
            "selected_hall_id": int(hall_id) if hall_id else None,
            "selected_time": selected_time,
            "selected_duration": selected_duration,
            "duration_choices": Booking.DurationType.choices,
            "time_choices": BOOKING_TIME_CHOICES,
            "extra_time_choices": EXTRA_TIME_CHOICES,
            "selected_extra_minutes": selected_extra_minutes,
            "selected_end_time": selected_end.time(),
            "available_halls": available_halls,
            "selected_day_bookings": selected_day_bookings,
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


def format_time_ar(value):
    if not value:
        return ""
    hour = value.hour
    minute = value.minute
    suffix = "صباحًا" if hour < 12 else "مساءً"
    display_hour = hour % 12 or 12
    if hour == 0:
        suffix = "منتصف الليل"
    return f"{display_hour:02d}:{minute:02d} {suffix}"


def format_duration_minutes(minutes):
    if not minutes:
        return "بدون وقت إضافي"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    parts = []
    if hours:
        parts.append(f"{hours} ساعة")
    if remaining_minutes:
        parts.append(f"{remaining_minutes} دقيقة")
    return " و ".join(parts)


def booking_print(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related("client", "hall", "occasion_type"),
        pk=pk,
    )
    services = booking.services.select_related("service").all()
    return render(
        request,
        "bookings/booking_print.html",
        {
            "booking": booking,
            "services": services,
            "page_title": f"عقد حجز رقم {booking.id}",
            "duration_label": format_duration_minutes(booking.duration_minutes),
            "extra_duration_label": format_duration_minutes(booking.extra_minutes),
        },
    )


def booking_pdf(request, pk):
    return redirect("booking_print", pk=pk)

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
        wordWrap="RTL",
    )

    def para(text, style=normal_style):
        return Paragraph(ar(text), style)

    def txt(text):
        return ar(text)

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
        [txt("رقم الحجز"), txt(booking.id), txt("اسم العميل"), txt(booking.client.name)],
        [txt("رقم الهاتف"), txt(booking.client.phone), txt("القاعة"), txt(str(booking.hall))],
        [txt("نوع المناسبة"), txt(str(booking.occasion_type)), txt("مدة الحجز"), txt(booking.get_duration_type_display())],
        [txt("تاريخ الحجز"), txt(format_date_ar(booking.booking_date)), txt("تاريخ المناسبة"), txt(format_date_ar(booking.occasion_date))],
        [txt("من الساعة"), txt(format_time_ar(booking.start_time)), txt("إلى الساعة"), txt(format_time_ar(booking.end_time))],
        [txt("الحالة"), txt(booking.get_status_display()), txt("الوقت الأساسي"), txt(booking.get_duration_type_display())],
        [txt("وقت إضافي"), txt(format_duration_minutes(booking.extra_minutes)), txt("إجمالي الوقت"), txt(format_duration_minutes(booking.duration_minutes))],
        [txt("اسم العريس / صاحب المناسبة"), txt(booking.groom_name or "-"), txt("الرقم القومي"), txt(booking.groom_national_id or "-")],
        [txt("العنوان"), txt(booking.groom_address or "-"), txt("اسم العروسة"), txt(booking.bride_name or "-")],
        [txt("الرقم القومي للعروسة"), txt(booking.bride_national_id or "-"), txt("عنوان العروسة"), txt(booking.bride_address or "-")],
    ]
    info_table = Table(booking_info, colWidths=[3.2 * cm, 4.3 * cm, 3.2 * cm, 5.3 * cm])
    info_table.setStyle(table_style)
    story.append(info_table)

    story.append(para("تفاصيل الخدمات", section_style))
    services_data = [[txt("الإجمالي"), txt("الكمية"), txt("سعر الوحدة"), txt("الخدمة")]]

    for s in booking.services.all():
        services_data.append([
            txt(format_money(s.line_total)),
            txt(s.quantity),
            txt(format_money(s.unit_price)),
            txt(str(s.service)),
        ])

    if len(services_data) == 1:
        services_data.append([txt("0.00 جنيه"), txt("-"), txt("-"), txt("لا توجد خدمات إضافية")])

    services_table = Table(services_data, colWidths=[3.5 * cm, 2.5 * cm, 3.5 * cm, 7 * cm])
    services_table.setStyle(table_style)
    story.append(services_table)

    story.append(para("الملخص المالي", section_style))
    financial_data = [
        [txt("البند"), txt("القيمة")],
        [txt("سعر القاعة"), txt(format_money(booking.hall_price))],
        [txt("إجمالي الخدمات"), txt(format_money(booking.services_total))],
        [txt("إجمالي العقد"), txt(format_money(booking.total_price))],
        [txt("المدفوع"), txt(format_money(booking.amount_paid))],
        [txt("المتبقي"), txt(format_money(booking.remaining_amount))],
        [txt("مقدم الحجز المطلوب"), txt(format_money(booking.deposit_amount))],
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
