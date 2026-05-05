from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from accounting.models import AccountingDetermination, JournalEntry, JournalLine, Treasury


def get_active_determination(event_type):
    return AccountingDetermination.objects.select_related("debit_account", "credit_account").filter(
        event_type=event_type,
        is_active=True,
    ).first()


def get_default_treasury():
    return Treasury.objects.select_related("account").filter(is_active=True).order_by("id").first()


@transaction.atomic
def confirm_and_post_booking(booking, user):
    if booking.is_posted and booking.journal_entry_id:
        return booking.journal_entry

    if booking.total_price <= 0:
        booking.refresh_totals(save=True)

    deposit_det = get_active_determination(AccountingDetermination.EventType.BOOKING_DEPOSIT)
    revenue_det = get_active_determination(AccountingDetermination.EventType.BOOKING_REVENUE)
    treasury = get_default_treasury()

    if not deposit_det or not revenue_det:
        raise ValueError("Accounting Determination is incomplete for booking posting.")
    if not treasury:
        raise ValueError("No active treasury is configured.")

    amount_paid = booking.amount_paid or Decimal("0")
    remaining = booking.remaining_amount or Decimal("0")
    total = booking.total_price or Decimal("0")

    entry = JournalEntry.objects.create(
        entry_date=booking.booking_date,
        reference=f"BOOKING-{booking.pk}",
        description=f"ترحيل عقد حجز رقم {booking.pk} - {booking.client.name}",
        status=JournalEntry.EntryStatus.POSTED,
    )

    if amount_paid > 0:
        JournalLine.objects.create(
            entry=entry,
            account=treasury.account,
            debit=amount_paid,
            credit=0,
            description="مقدم حجز محصل",
        )

    if remaining > 0:
        JournalLine.objects.create(
            entry=entry,
            account=revenue_det.debit_account,
            debit=remaining,
            credit=0,
            description="استكمال مستحق على العميل",
        )

    if total > 0:
        JournalLine.objects.create(
            entry=entry,
            account=deposit_det.credit_account,
            debit=0,
            credit=total,
            description="إيرادات مؤجلة لعقد حجز",
        )

    booking.is_posted = True
    booking.posted_at = timezone.now()
    booking.posted_by = user if getattr(user, "is_authenticated", False) else None
    booking.journal_entry = entry
    booking.status = booking.BookingStatus.CONFIRMED
    booking.save(update_fields=["is_posted", "posted_at", "posted_by", "journal_entry", "status", "updated_at"])
    return entry
