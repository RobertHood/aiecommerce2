from django.urls import path

from assistant import views


urlpatterns = [
    path("health/", views.health, name="health"),
    path("api/chat/", views.chat, name="chat"),
]
