from django.contrib import admin
from django.utils.html import format_html

from .models import Account, AccountingDetermination, CashTransaction, JournalEntry, JournalLine, Supplier, Treasury


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name_ar", "name_en", "main_account_ar", "account_type", "is_active")
    list_filter = ("account_type", "main_account_ar", "is_active")
    search_fields = ("code", "name_ar", "name_en", "main_account_ar", "main_account_en")
    list_editable = ("is_active",)


@admin.register(Treasury)
class TreasuryAdmin(admin.ModelAdmin):
    list_display = ("name", "account", "opening_balance", "current_balance_display", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "account__code", "account__name_ar")

    @admin.display(description="الرصيد الحالي")
    def current_balance_display(self, obj):
        color = "#247a4b" if obj.current_balance >= 0 else "#b42318"
        return format_html('<strong style="color:{};">{}</strong>', color, obj.current_balance)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "account", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "phone", "account__code", "account__name_ar")


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 2
    autocomplete_fields = ("account",)


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "entry_date", "reference", "description", "status", "total_debit", "total_credit", "balanced_badge")
    list_filter = ("status", "entry_date")
    search_fields = ("reference", "description", "lines__account__code", "lines__account__name_ar")
    date_hierarchy = "entry_date"
    inlines = [JournalLineInline]

    @admin.display(description="متوازن")
    def balanced_badge(self, obj):
        if obj.is_balanced:
            return format_html('<span style="color:#247a4b;font-weight:bold;">نعم</span>')
        return format_html('<span style="color:#b42318;font-weight:bold;">لا</span>')


@admin.register(CashTransaction)
class CashTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction_date", "treasury", "transaction_type", "amount", "account", "supplier")
    list_filter = ("transaction_type", "treasury", "transaction_date")
    search_fields = ("description", "account__code", "account__name_ar", "supplier__name")
    date_hierarchy = "transaction_date"
    autocomplete_fields = ("treasury", "account", "supplier", "journal_entry")


@admin.register(AccountingDetermination)
class AccountingDeterminationAdmin(admin.ModelAdmin):
    list_display = ("event_type", "debit_account", "credit_account", "is_active")
    list_filter = ("event_type", "is_active")
    search_fields = (
        "debit_account__code",
        "debit_account__name_ar",
        "credit_account__code",
        "credit_account__name_ar",
    )
    autocomplete_fields = ("debit_account", "credit_account")
