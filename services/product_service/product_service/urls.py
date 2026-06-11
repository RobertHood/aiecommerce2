from django.contrib import admin
from django.urls import path

from inventory import views


admin.site.site_header = "Nexus Product Service Admin"
admin.site.site_title = "Product Service"
admin.site.index_title = "Warehouse and Inventory Management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health, name="health"),
    path("api/warehouses/", views.warehouse_list_create, name="warehouse_list_create"),
    path("api/inventory/", views.inventory_list_create, name="inventory_list_create"),
    path("api/inventory/<int:item_id>/", views.inventory_detail, name="inventory_detail"),
    path("api/inventory/<int:item_id>/adjust/", views.inventory_adjust, name="inventory_adjust"),
    path("api/inventory/<int:item_id>/reserve/", views.inventory_reserve, name="inventory_reserve"),
    path("api/inventory/<int:item_id>/release/", views.inventory_release, name="inventory_release"),
    path("api/movements/", views.stock_movement_list, name="stock_movement_list"),
]
