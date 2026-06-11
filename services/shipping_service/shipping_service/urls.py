from django.contrib import admin
from django.urls import path

from shipping import views


admin.site.site_header = "Nexus Shipping Service Admin"
admin.site.site_title = "Shipping Service"
admin.site.index_title = "Carrier, Shipment and Route Management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health, name="health"),
    path("api/carriers/", views.carrier_list_create, name="carrier_list_create"),
    path("api/shipments/", views.shipment_list_create, name="shipment_list_create"),
    path("api/shipments/<int:shipment_id>/", views.shipment_detail, name="shipment_detail"),
    path("api/shipments/<int:shipment_id>/assign/", views.shipment_assign, name="shipment_assign"),
    path("api/shipments/<int:shipment_id>/events/", views.shipment_event_create, name="shipment_event_create"),
]
