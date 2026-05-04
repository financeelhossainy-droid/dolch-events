from django.urls import path

from . import views

urlpatterns = [
    path("modules/", views.module_hub, name="module_hub"),
    path("accounting/", views.accounting_module, name="accounting_module"),
    path("calendar/", views.calendar_module, name="calendar_module"),
    path("purchases/", views.purchases_module, name="purchases_module"),
    path("inventory/", views.inventory_module, name="inventory_module"),
    path("costing/", views.costing_module, name="costing_module"),
    path("reports/", views.reports_module, name="reports_module"),
]
