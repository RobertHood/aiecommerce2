from types import SimpleNamespace

from django.conf import settings

from .http import request_json


def base_url():
    return settings.PRODUCT_SERVICE_URL.rstrip("/")


def list_warehouses():
    data = request_json("GET", f"{base_url()}/api/warehouses/")
    return [SimpleNamespace(**item) for item in data.get("results", [])]


def list_inventory():
    data = request_json("GET", f"{base_url()}/api/inventory/")
    return [SimpleNamespace(**item) for item in data.get("results", [])]


def reserve_inventory(item_id, quantity, reference=""):
    return request_json(
        "POST",
        f"{base_url()}/api/inventory/{item_id}/reserve/",
        {"quantity": quantity, "reference": reference},
    )
