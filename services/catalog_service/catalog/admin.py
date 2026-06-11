from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description_preview", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    @admin.display(description="Description")
    def description_preview(self, obj):
        if not obj.description:
            return "-"
        return obj.description[:80] + ("..." if len(obj.description) > 80 else "")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    list_editable = ("price", "stock", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "short_desc", "description")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic information", {
            "fields": ("category", "name", "slug", "is_active"),
        }),
        ("Pricing and stock", {
            "fields": ("price", "original_price", "stock"),
        }),
        ("Display", {
            "fields": ("icon", "color", "rating", "reviews"),
        }),
        ("Content", {
            "fields": ("short_desc", "description", "features"),
        }),
        ("System", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
