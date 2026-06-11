from decimal import Decimal
from types import SimpleNamespace

from django.conf import settings

from .http import request_json


def base_url():
    return settings.ORDER_SERVICE_URL.rstrip("/")


def order_from_payload(data):
    order = SimpleNamespace(**data)
    order.total = Decimal(str(order.total))
    order.subtotal = Decimal(str(order.subtotal))
    order.tax = Decimal(str(order.tax))
    order.items = [SimpleNamespace(**item) for item in data.get("items", [])]
    return order


def create_order(customer, items):
    payload = {"customer": customer, "items": items}
    return order_from_payload(request_json("POST", f"{base_url()}/api/orders/", payload))


def get_order(order_id):
    return order_from_payload(request_json("GET", f"{base_url()}/api/orders/{order_id}/"))
