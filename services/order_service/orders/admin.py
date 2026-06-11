from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_id", "product_name", "unit_price", "quantity", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "address")
    readonly_fields = ("subtotal", "tax", "total", "created_at")
    inlines = [OrderItemInline]
