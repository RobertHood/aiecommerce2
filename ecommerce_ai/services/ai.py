from django.conf import settings

from .http import request_json


def base_url():
    return settings.AI_SERVICE_URL.rstrip("/")


def ask(message):
    return request_json("POST", f"{base_url()}/api/chat/", {"message": message})
