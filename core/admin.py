from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Hall, OccasionType, Service, MainServicePrice, ExtraServicePrice, FixedServicePrice


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display  = ("name", "is_active")
    list_filter   = ("is_active",)
    search_fields = ("name",)


@admin.register(OccasionType)
class OccasionTypeAdmin(admin.ModelAdmin):
    list_display  = ("name", "is_active")
    list_filter   = ("is_active",)
    search_fields = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ("name", "service_type", "is_hall_based", "is_active")
    list_filter   = ("service_type", "is_hall_based", "is_active")
    search_fields = ("name",)


@admin.register(MainServicePrice)
class MainServicePriceAdmin(admin.ModelAdmin):
    list_display  = ("hall", "occasion_type", "price", "is_active")
    list_filter   = ("hall", "occasion_type", "is_active")
    search_fields = ("hall__name", "occasion_type__name")


@admin.register(ExtraServicePrice)
class ExtraServicePriceAdmin(admin.ModelAdmin):
    list_display  = ("service", "hall", "price", "is_active")
    list_filter   = ("hall", "is_active")
    search_fields = ("service__name", "hall__name")


@admin.register(FixedServicePrice)
class FixedServicePriceAdmin(admin.ModelAdmin):
    list_display  = ("service", "price", "is_active")
    list_filter   = ("is_active",)
    search_fields = ("service__name",)