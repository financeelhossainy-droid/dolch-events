from django.urls import path

from . import views

urlpatterns = [
    path("master-data/", views.master_data, name="master_data"),
    path("determination/", views.accounting_determination_list, name="accounting_determination_list"),
    path("accounts/", views.account_list, name="account_list"),
    path("treasury/", views.treasury_list, name="treasury_list"),
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("journal/", views.journal_entry_list, name="journal_entry_list"),
]
