from django.contrib import admin

from .models import Carrier, RouteEvent, Shipment


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "service_level", "base_fee", "is_active")
    list_filter = ("service_level", "is_active")
    search_fields = ("code", "name", "contact_phone")


class RouteEventInline(admin.TabularInline):
    model = RouteEvent
    extra = 0
    readonly_fields = ("status", "location", "note", "occurred_at")
    can_delete = False


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "order_id", "tracking_number", "carrier", "status", "destination_city", "estimated_delivery")
    list_filter = ("status", "carrier", "destination_city")
    search_fields = ("order_id", "tracking_number", "recipient_name", "destination_address")
    readonly_fields = ("tracking_number", "created_at", "updated_at")
    inlines = [RouteEventInline]


@admin.register(RouteEvent)
class RouteEventAdmin(admin.ModelAdmin):
    list_display = ("shipment", "status", "location", "occurred_at")
    list_filter = ("status", "occurred_at")
    search_fields = ("shipment__tracking_number", "shipment__order_id", "location", "note")
