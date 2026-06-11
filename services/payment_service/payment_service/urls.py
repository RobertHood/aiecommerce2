from django.contrib import admin
from django.urls import path

from payments import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health, name="health"),
    path("api/payments/", views.payment_create, name="payment_create"),
    path("api/payments/<int:payment_id>/", views.payment_detail, name="payment_detail"),
    path("api/payments/<int:payment_id>/confirm/", views.payment_confirm, name="payment_confirm"),
    path("api/payments/<int:payment_id>/fail/", views.payment_fail, name="payment_fail"),
]
