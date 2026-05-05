from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from accounting.models import Account, AccountingDetermination, CashTransaction, JournalEntry, Supplier, Treasury
from bookings.models import Booking, BookingService, Client
from core.models import ExtraServicePrice, FixedServicePrice, Hall, MainServicePrice, OccasionType, Service


def perms_for(model, actions):
    content_type = ContentType.objects.get_for_model(model)
    app_label = content_type.app_label
    model_name = content_type.model
    permissions = []
    for action in actions:
        codename = f"{action}_{model_name}"
        permission = Permission.objects.filter(content_type=content_type, codename=codename).first()
        if permission:
            permissions.append(permission)
    return permissions


class Command(BaseCommand):
    help = "Create ERP authority matrix groups based on segregation of duties."

    def handle(self, *args, **options):
        matrix = {
            "Booking Moderator": [
                *perms_for(Client, ["add", "change", "view"]),
                *perms_for(Booking, ["add", "change", "view"]),
                *perms_for(BookingService, ["add", "change", "delete", "view"]),
                *perms_for(Hall, ["view"]),
                *perms_for(OccasionType, ["view"]),
                *perms_for(Service, ["view"]),
            ],
            "Booking Manager": [
                *perms_for(Client, ["add", "change", "view"]),
                *perms_for(Booking, ["add", "change", "view"]),
                *perms_for(BookingService, ["add", "change", "delete", "view"]),
                Permission.objects.get(codename="can_confirm_booking"),
                *perms_for(Hall, ["view"]),
                *perms_for(OccasionType, ["view"]),
                *perms_for(Service, ["view"]),
                *perms_for(MainServicePrice, ["view"]),
                *perms_for(ExtraServicePrice, ["view"]),
                *perms_for(FixedServicePrice, ["view"]),
            ],
            "Cashier": [
                *perms_for(Treasury, ["view"]),
                *perms_for(CashTransaction, ["add", "view"]),
                *perms_for(Account, ["view"]),
                *perms_for(Supplier, ["view"]),
                *perms_for(JournalEntry, ["view"]),
            ],
            "Accountant": [
                *perms_for(Account, ["add", "change", "view"]),
                *perms_for(AccountingDetermination, ["add", "change", "view"]),
                *perms_for(Treasury, ["add", "change", "view"]),
                *perms_for(Supplier, ["add", "change", "view"]),
                *perms_for(CashTransaction, ["add", "change", "view"]),
                *perms_for(JournalEntry, ["add", "change", "view"]),
            ],
            "Inventory Keeper": [
                *perms_for(Service, ["view"]),
            ],
            "Auditor": [
                *perms_for(Client, ["view"]),
                *perms_for(Booking, ["view"]),
                *perms_for(BookingService, ["view"]),
                *perms_for(Account, ["view"]),
                *perms_for(AccountingDetermination, ["view"]),
                *perms_for(Treasury, ["view"]),
                *perms_for(Supplier, ["view"]),
                *perms_for(CashTransaction, ["view"]),
                *perms_for(JournalEntry, ["view"]),
            ],
        }

        for group_name, permissions in matrix.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS("Authority matrix groups created/updated."))
