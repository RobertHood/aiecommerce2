from django.contrib import admin

from .models import InventoryItem, StockMovement, Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "city", "is_active", "created_at")
    list_filter = ("is_active", "city")
    search_fields = ("code", "name", "address", "city")


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ("movement_type", "quantity", "reference", "note", "created_at")
    can_delete = False


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "product_name",
        "warehouse",
        "quantity_available",
        "quantity_reserved",
        "quantity_total",
        "reorder_level",
        "needs_reorder",
    )
    list_filter = ("warehouse",)
    search_fields = ("sku", "product_name", "product_id")
    readonly_fields = ("updated_at",)
    inlines = [StockMovementInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("inventory_item", "movement_type", "quantity", "reference", "created_at")
    list_filter = ("movement_type", "created_at")
    search_fields = ("inventory_item__sku", "inventory_item__product_name", "reference")
