from django.contrib import admin
from django.urls import path

from orders import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health, name="health"),
    path("api/orders/", views.order_create, name="order_create"),
    path("api/orders/<int:order_id>/", views.order_detail, name="order_detail"),
]
