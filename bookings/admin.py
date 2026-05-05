from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Client, Booking, BookingService


class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 0
    fields = ("service", "unit_price", "quantity", "notes")
    readonly_fields = ("unit_price",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "created_at")
    search_fields = ("name", "phone")
    readonly_fields = ("created_at",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "hall",
        "occasion_type",
        "duration_type",
        "occasion_date",
        "status_badge",
        "hall_price",
        "services_total",
        "total_price",
        "amount_paid",
        "remaining_colored",
        "print_pdf",
    )

    list_filter = ("hall", "occasion_type", "duration_type", "status")
    search_fields = (
        "client__name",
        "client__phone",
        "groom_name",
        "groom_national_id",
        "bride_name",
        "bride_national_id",
        "bride_address",
    )
    readonly_fields = (
        "hall_price",
        "services_total",
        "total_price",
        "remaining_amount",
        "deposit_amount",
        "created_at",
        "updated_at",
        "is_posted",
        "posted_at",
        "posted_by",
        "journal_entry",
        "print_pdf_link",
    )
    date_hierarchy = "occasion_date"
    inlines = [BookingServiceInline]

    fieldsets = (
        ("بيانات الحجز", {
            "fields": (
                "client",
                "hall",
                "occasion_type",
                "duration_type",
                "booking_date",
                "occasion_date",
                "status",
            )
        }),
        ("بيانات العريس والعروسة", {
            "fields": (
                "groom_name",
                "groom_national_id",
                "groom_address",
                "bride_name",
                "bride_national_id",
                "bride_address",
            )
        }),
        ("المالية", {
            "fields": (
                "hall_price",
                "services_total",
                "total_price",
                "amount_paid",
                "remaining_amount",
                "deposit_amount",
                "print_pdf_link",
            )
        }),
        ("الترحيل المحاسبي", {
            "fields": (
                "is_posted",
                "posted_at",
                "posted_by",
                "journal_entry",
            )
        }),
        ("ملاحظات", {
            "fields": ("notes",),
            "classes": ("collapse",),
        }),
        ("معلومات النظام", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="الحالة")
    def status_badge(self, obj):
        colors = {
            "pending": "#f0ad4e",
            "confirmed": "#5bc0de",
            "cancelled": "#d9534f",
            "completed": "#5cb85c",
        }
        color = colors.get(obj.status, "#999")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="المتبقي")
    def remaining_colored(self, obj):
        remaining = obj.remaining_amount
        color = "red" if remaining > 0 else "green"
        return format_html(
            '<span style="color:{};font-weight:bold;">{}</span>',
            color,
            remaining
        )

    @admin.display(description="طباعة")
    def print_pdf(self, obj):
        url = reverse("booking_print", args=[obj.pk])
        return format_html(
            '<a class="button" target="_blank" href="{}">طباعة</a>',
            url,
        )

    @admin.display(description="طباعة العقد")
    def print_pdf_link(self, obj):
        if obj.pk:
            url = reverse("booking_print", args=[obj.pk])
            return format_html(
                '<a class="button" target="_blank" '
                'style="padding:8px 12px;background:#0f5b78;color:white;border-radius:6px;text-decoration:none;" '
                'href="{}">فتح ملف PDF</a>',
                url,
            )
        return "احفظ الحجز أولًا لتفعيل الطباعة"


@admin.register(BookingService)
class BookingServiceAdmin(admin.ModelAdmin):
    list_display = ("booking", "service", "unit_price", "quantity", "line_total")
    search_fields = ("booking__client__name", "service__name")
