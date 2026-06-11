from types import SimpleNamespace

from django.conf import settings

from .http import request_json


def base_url():
    return settings.USER_SERVICE_URL.rstrip("/")


def user_from_payload(data):
    return SimpleNamespace(**data)


def register_user(payload):
    return user_from_payload(request_json("POST", f"{base_url()}/api/users/", payload))


def login_user(email, password):
    data = request_json("POST", f"{base_url()}/api/users/login/", {"email": email, "password": password})
    data["user"] = user_from_payload(data["user"])
    return data


def get_user(user_id):
    return user_from_payload(request_json("GET", f"{base_url()}/api/users/{user_id}/"))


def update_user(user_id, payload):
    return user_from_payload(request_json("PATCH", f"{base_url()}/api/users/{user_id}/", payload))
