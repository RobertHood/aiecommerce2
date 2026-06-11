from django.contrib import admin
from django.urls import path

from users import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", views.health, name="health"),
    path("api/users/", views.user_list_create, name="user_list_create"),
    path("api/users/login/", views.user_login, name="user_login"),
    path("api/users/<int:user_id>/", views.user_detail, name="user_detail"),
]
