from datetime import datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator
from accounting.models import JournalEntry
from core.models import (
    Hall,
    OccasionType,
    Service,
    MainServicePrice,
    ExtraServicePrice,
    FixedServicePrice,
)

phone_validator = RegexValidator(
    regex=r"^01[0125]\d{8}$",
    message="أدخل رقم هاتف مصري صحيح"
)


class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم العميل")
    phone = models.CharField(
        max_length=11,
        validators=[phone_validator],
        unique=True,
        verbose_name="رقم الهاتف"
    )
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING = "pending", "قيد المراجعة"
        CONFIRMED = "confirmed", "مؤكد"
        CANCELLED = "cancelled", "ملغي"
        COMPLETED = "completed", "منتهي"

    class DurationType(models.TextChoices):
        ONE_HOUR = "1h", "ساعة"
        TWO_HOURS = "2h", "ساعتان"
        PHOTO_VIDEO_ZAFFA_OFFER = "photo_video_zaffa_offer", "عرض فوتو + فيديو + زفة"

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        verbose_name="العميل",
        related_name="bookings"
    )
    hall = models.ForeignKey(
        Hall,
        on_delete=models.PROTECT,
        verbose_name="القاعة",
        related_name="bookings"
    )
    occasion_type = models.ForeignKey(
        OccasionType,
        on_delete=models.PROTECT,
        verbose_name="نوع المناسبة",
        related_name="bookings"
    )

    booking_date = models.DateField(verbose_name="تاريخ الحجز")
    occasion_date = models.DateField(verbose_name="تاريخ المناسبة")
    start_time = models.TimeField(default="11:00", verbose_name="ساعة بداية الحجز")
    duration_type = models.CharField(
        max_length=30,
        choices=DurationType.choices,
        default=DurationType.ONE_HOUR,
        verbose_name="الوقت الأساسي"
    )
    extra_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="وقت إضافي بالدقائق"
    )

    status = models.CharField(
        max_length=15,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name="حالة الحجز"
    )

    hall_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="سعر القاعة"
    )
    services_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="إجمالي الخدمات"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="إجمالي السعر"
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="المبلغ المدفوع"
    )
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    is_posted = models.BooleanField(default=False, verbose_name="مرحل محاسبيًا")
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الترحيل")
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_bookings",
        verbose_name="تم الترحيل بواسطة",
    )
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
        verbose_name="قيد اليومية",
    )

    groom_name = models.CharField(max_length=100, blank=True, verbose_name="اسم العريس")
    groom_national_id = models.CharField(max_length=20, blank=True, verbose_name="الرقم القومي للعريس")
    groom_address = models.CharField(max_length=255, blank=True, verbose_name="عنوان العريس")

    bride_name = models.CharField(max_length=100, blank=True, verbose_name="اسم العروسة")
    bride_national_id = models.CharField(max_length=20, blank=True, verbose_name="الرقم القومي للعروسة")
    bride_address = models.CharField(max_length=255, blank=True, verbose_name="عنوان العروسة")
    

    class Meta:
        verbose_name = "حجز"
        verbose_name_plural = "الحجوزات"
        ordering = ["-occasion_date"]
        permissions = [
            ("can_confirm_booking", "Can confirm and post booking"),
            ("can_unpost_booking", "Can reverse posted booking"),
        ]

    def __str__(self):
        return f"حجز #{self.pk} | {self.client.name} | {self.hall} | {self.occasion_date}"

    @property
    def has_photo_video_zaffa_bundle(self):
        service_names = " ".join(str(item.service).lower() for item in self.services.all())
        required_words = ("فوتو", "فيديو", "زفة")
        return all(word in service_names for word in required_words)

    @property
    def duration_minutes(self):
        base_minutes = {
            self.DurationType.ONE_HOUR: 60,
            self.DurationType.TWO_HOURS: 120,
            self.DurationType.PHOTO_VIDEO_ZAFFA_OFFER: 90,
        }.get(self.duration_type, 60)
        return base_minutes + (self.extra_minutes or 0)

    @property
    def end_time(self):
        if not self.start_time:
            return None
        start_datetime = datetime.combine(self.occasion_date, self.start_time)
        return (start_datetime + timedelta(minutes=self.duration_minutes)).time()

    def booking_interval(self):
        start_datetime = datetime.combine(self.occasion_date, self.start_time)
        end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
        return start_datetime, end_datetime

    def clean(self):
        super().clean()
        if self.hall_id and self.occasion_date and self.start_time and self.status != self.BookingStatus.CANCELLED:
            start_datetime, end_datetime = self.booking_interval()
            possible_conflicts = Booking.objects.filter(
                hall=self.hall,
                occasion_date=self.occasion_date,
            ).exclude(status=self.BookingStatus.CANCELLED)
            if self.pk:
                possible_conflicts = possible_conflicts.exclude(pk=self.pk)

            for booking in possible_conflicts:
                conflict_start, conflict_end = booking.booking_interval()
                if start_datetime < conflict_end and end_datetime > conflict_start:
                    raise ValidationError("هذه القاعة محجوزة بالفعل في وقت متداخل مع هذا الحجز.")

    @property
    def remaining_amount(self):
        return self.total_price - self.amount_paid

    @property
    def deposit_amount(self):
        deposit = self.total_price * Decimal("0.25")
        return max(deposit, Decimal("3000"))

    def get_hall_base_price(self):
        occasion_code = self.occasion_type.name
        one_hour_price = MainServicePrice.objects.filter(
            hall=self.hall,
            occasion_type=self.occasion_type,
            duration_type=self.DurationType.ONE_HOUR,
            is_active=True
        ).first()

        if occasion_code in ["condolence", "aqeeqa"]:
            price_obj = MainServicePrice.objects.filter(
                hall=self.hall,
                occasion_type=self.occasion_type,
                duration_type="na",
                is_active=True
            ).first()
        else:
            price_obj = MainServicePrice.objects.filter(
                hall=self.hall,
                occasion_type=self.occasion_type,
                duration_type=self.duration_type,
                is_active=True
            ).first()

        if self.duration_type == self.DurationType.PHOTO_VIDEO_ZAFFA_OFFER and one_hour_price:
            return one_hour_price.price + self.calculate_extra_time_price(one_hour_price.price)

        if price_obj:
            return price_obj.price + self.calculate_extra_time_price(one_hour_price.price if one_hour_price else Decimal("0"))

        return Decimal("0")

    def calculate_extra_time_price(self, hourly_price):
        if not self.extra_minutes or not hourly_price:
            return Decimal("0")
        return (hourly_price * Decimal(str(self.extra_minutes))) / Decimal("60")

    def get_bundle_service_price(self, *keywords):
        service = None
        for keyword in keywords:
            service = Service.objects.filter(name__icontains=keyword, is_active=True).first()
            if service:
                break
        if not service:
            return Decimal("0")

        if service.is_hall_based:
            hall_price = ExtraServicePrice.objects.filter(
                service=service,
                hall=self.hall,
                is_active=True,
            ).first()
            if hall_price:
                return hall_price.price

        fixed_price = FixedServicePrice.objects.filter(service=service, is_active=True).first()
        if fixed_price:
            return fixed_price.price

        return Decimal("0")

    def calculate_offer_bundle_total(self):
        if self.duration_type != self.DurationType.PHOTO_VIDEO_ZAFFA_OFFER:
            return Decimal("0")
        existing_service_names = " ".join(str(item.service).lower() for item in self.services.all())
        total = Decimal("0")
        bundle_keywords = (
            ("فوتو", "photo"),
            ("فيديو", "video"),
            ("زفة", "zaffa"),
        )
        for keywords in bundle_keywords:
            if not any(keyword in existing_service_names for keyword in keywords):
                total += self.get_bundle_service_price(*keywords)
        return total

    def calculate_services_total(self):
        total = Decimal("0")
        for item in self.services.all():
            total += item.line_total
        total += self.calculate_offer_bundle_total()
        return total

    def refresh_totals(self, save=False):
        self.hall_price = self.get_hall_base_price()
        self.services_total = self.calculate_services_total()
        self.total_price = self.hall_price + self.services_total

        if save:
            super().save(update_fields=[
                "hall_price",
                "services_total",
                "total_price",
                "updated_at",
            ])

    def save(self, *args, **kwargs):
        self.hall_price = self.get_hall_base_price()

        if self.pk:
            self.services_total = self.calculate_services_total()
        else:
            self.services_total = Decimal("0")

        self.total_price = self.hall_price + self.services_total
        super().save(*args, **kwargs)


class BookingService(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        verbose_name="الحجز",
        related_name="services"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name="الخدمة"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="سعر الوحدة",
        default=0
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="الكمية"
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ملاحظة"
    )

    class Meta:
        verbose_name = "خدمة في الحجز"
        verbose_name_plural = "خدمات الحجز"

    def __str__(self):
        return f"{self.service} x{self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def get_service_price(self):
        if self.service.is_hall_based:
            hall_price = ExtraServicePrice.objects.filter(
                service=self.service,
                hall=self.booking.hall,
                is_active=True
            ).first()
            if hall_price:
                return hall_price.price

        fixed_price = FixedServicePrice.objects.filter(
            service=self.service,
            is_active=True
        ).first()
        if fixed_price:
            return fixed_price.price

        return Decimal("0")

    def save(self, *args, **kwargs):
        self.unit_price = self.get_service_price()
        super().save(*args, **kwargs)
        self.booking.refresh_totals(save=True)

    def delete(self, *args, **kwargs):
        booking = self.booking
        super().delete(*args, **kwargs)
        booking.refresh_totals(save=True)
