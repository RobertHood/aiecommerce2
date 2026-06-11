from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "created_at")
    search_fields = ("email", "full_name", "phone")
    readonly_fields = ("password_hash", "created_at", "updated_at")
