from django.contrib import admin
from django.urls import path

from catalog import views


admin.site.site_header = "Nexus Catalog Admin"
admin.site.site_title = "Catalog Admin"
admin.site.index_title = "Product Catalog Management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health, name="health"),
    path("api/categories/", views.category_list, name="category_list"),
    path("api/products/", views.product_list, name="product_list"),
    path("api/products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("api/stock/reserve/", views.reserve_stock, name="reserve_stock"),
]
