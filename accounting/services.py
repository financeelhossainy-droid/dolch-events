from decimal import Decimal

from django.db import transaction

from .models import AccountingDetermination, CashTransaction, JournalEntry, JournalLine


def get_determination(event_type):
    return AccountingDetermination.objects.select_related(
        "debit_account",
        "credit_account",
    ).filter(event_type=event_type, is_active=True).first()


@transaction.atomic
def post_cash_transaction(cash_transaction):
    if cash_transaction.journal_entry_id:
        return cash_transaction.journal_entry

    event_type = (
        AccountingDetermination.EventType.CASH_IN
        if cash_transaction.transaction_type == CashTransaction.TransactionType.IN
        else AccountingDetermination.EventType.CASH_OUT
    )
    determination = get_determination(event_type)

    amount = cash_transaction.amount or Decimal("0")
    if amount <= 0 or not determination:
        return None

    entry = JournalEntry.objects.create(
        entry_date=cash_transaction.transaction_date,
        reference=f"CASH-{cash_transaction.pk}",
        description=cash_transaction.description,
        status=JournalEntry.EntryStatus.POSTED,
    )

    debit_account = determination.debit_account
    credit_account = determination.credit_account

    if cash_transaction.transaction_type == CashTransaction.TransactionType.IN:
        debit_account = cash_transaction.treasury.account
        credit_account = cash_transaction.account
    elif cash_transaction.transaction_type == CashTransaction.TransactionType.OUT:
        debit_account = cash_transaction.account
        credit_account = cash_transaction.treasury.account

    JournalLine.objects.create(
        entry=entry,
        account=debit_account,
        debit=amount,
        credit=0,
        description=cash_transaction.description,
    )
    JournalLine.objects.create(
        entry=entry,
        account=credit_account,
        debit=0,
        credit=amount,
        description=cash_transaction.description,
    )

    cash_transaction.journal_entry = entry
    cash_transaction.save(update_fields=["journal_entry"])
    return entry
