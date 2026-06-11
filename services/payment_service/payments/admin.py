from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order_id", "amount", "currency", "method", "status", "created_at")
    list_filter = ("method", "status", "created_at")
    search_fields = ("order_id", "customer_email", "transaction_id", "provider_reference")
    readonly_fields = ("transaction_id", "created_at", "updated_at")
