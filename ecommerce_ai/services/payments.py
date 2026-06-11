from decimal import Decimal
from types import SimpleNamespace

from django.conf import settings

from .http import request_json


def base_url():
    return settings.PAYMENT_SERVICE_URL.rstrip("/")


def payment_from_payload(data):
    payment = SimpleNamespace(**data)
    payment.amount = Decimal(str(payment.amount))
    return payment


def create_payment(order_id, amount, customer_email="", method="cod", currency="USD"):
    payload = {
        "order_id": order_id,
        "amount": str(amount),
        "customer_email": customer_email,
        "method": method,
        "currency": currency,
    }
    return payment_from_payload(request_json("POST", f"{base_url()}/api/payments/", payload))


def confirm_payment(payment_id, provider_reference=""):
    payload = {"provider_reference": provider_reference} if provider_reference else {}
    return payment_from_payload(request_json("POST", f"{base_url()}/api/payments/{payment_id}/confirm/", payload))


def get_payment(payment_id):
    return payment_from_payload(request_json("GET", f"{base_url()}/api/payments/{payment_id}/"))
