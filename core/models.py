from django.db import models

# Create your models here.
from django.db import models


class Hall(models.Model):
    class HallName(models.TextChoices):
        ROYAL   = "royal",   "القاعة الملكية"
        DIAMOND = "diamond", "القاعة الماسية"

    name      = models.CharField(max_length=20, choices=HallName.choices, unique=True, verbose_name="اسم القاعة")
    is_active = models.BooleanField(default=True, verbose_name="مفعّلة")

    class Meta:
        verbose_name        = "قاعة"
        verbose_name_plural = "القاعات"

    def __str__(self):
        return self.get_name_display()


class OccasionType(models.Model):
    class OccasionName(models.TextChoices):
        WEDDING           = "wedding",   "فرح إسلامي"
        MARRIAGE_CONTRACT = "contract",  "كتب كتاب"
        CONDOLENCE        = "condolence","عزاء"
        AQEEQA            = "aqeeqa",    "عقيقة"
        BUSINESS_MEETING  = "meeting",   "اجتماعات عمل"

    name      = models.CharField(max_length=30, choices=OccasionName.choices, unique=True, verbose_name="نوع المناسبة")
    is_active = models.BooleanField(default=True, verbose_name="مفعّل")

    class Meta:
        verbose_name        = "نوع مناسبة"
        verbose_name_plural = "أنواع المناسبات"

    def __str__(self):
        return self.get_name_display()


class Service(models.Model):
    class ServiceType(models.TextChoices):
        MAIN  = "main",  "خدمة رئيسية"
        EXTRA = "extra", "خدمة إضافية"

    name          = models.CharField(max_length=120, unique=True, verbose_name="اسم الخدمة")
    service_type  = models.CharField(max_length=10, choices=ServiceType.choices, verbose_name="نوع الخدمة")
    is_hall_based = models.BooleanField(default=False, verbose_name="سعرها يختلف حسب القاعة")
    is_active     = models.BooleanField(default=True, verbose_name="مفعّلة")

    class Meta:
        verbose_name        = "خدمة"
        verbose_name_plural = "الخدمات"

    def __str__(self):
        return self.name


class MainServicePrice(models.Model):
    class DurationType(models.TextChoices):
        ONE_HOUR  = "1h", "ساعة"
        TWO_HOURS = "2h", "ساعتان"
        PHOTO_VIDEO_ZAFFA_OFFER = "photo_video_zaffa_offer", "عرض فوتو + فيديو + زفة"
        NONE      = "na", "غير مرتبط بمدة"

    hall          = models.ForeignKey(Hall, on_delete=models.PROTECT, verbose_name="القاعة", related_name="prices")
    occasion_type = models.ForeignKey(OccasionType, on_delete=models.PROTECT, verbose_name="نوع المناسبة", related_name="prices")
    duration_type = models.CharField(
        max_length=30,
        choices=DurationType.choices,
        default=DurationType.NONE,
        verbose_name="المدة"
    )
    price         = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    is_active     = models.BooleanField(default=True, verbose_name="مفعّل")

    class Meta:
        verbose_name        = "سعر إيجار"
        verbose_name_plural = "أسعار الإيجار"
        unique_together     = ("hall", "occasion_type", "duration_type")

    def __str__(self):
        return f"{self.hall} | {self.occasion_type} | {self.duration_type} -> {self.price}"


class ExtraServicePrice(models.Model):
    service   = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="الخدمة", related_name="hall_prices")
    hall      = models.ForeignKey(Hall, on_delete=models.PROTECT, verbose_name="القاعة", related_name="extra_prices")
    price     = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    is_active = models.BooleanField(default=True, verbose_name="مفعّل")

    class Meta:
        verbose_name        = "سعر خدمة إضافية"
        verbose_name_plural = "أسعار الخدمات الإضافية"
        unique_together     = ("service", "hall")

    def __str__(self):
        return f"{self.service} | {self.hall} -> {self.price}"


class FixedServicePrice(models.Model):
    service   = models.OneToOneField(Service, on_delete=models.PROTECT, verbose_name="الخدمة", related_name="fixed_price")
    price     = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر الثابت")
    is_active = models.BooleanField(default=True, verbose_name="مفعّل")

    class Meta:
        verbose_name        = "سعر ثابت"
        verbose_name_plural = "أسعار ثابتة"

    def __str__(self):
        return f"{self.service} -> {self.price}"
