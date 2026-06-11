from types import SimpleNamespace

from django.conf import settings

from .http import request_json


def base_url():
    return settings.SHIPPING_SERVICE_URL.rstrip("/")


def list_carriers():
    data = request_json("GET", f"{base_url()}/api/carriers/")
    return [SimpleNamespace(**item) for item in data.get("results", [])]


def create_shipment(payload):
    return SimpleNamespace(**request_json("POST", f"{base_url()}/api/shipments/", payload))


def assign_carrier(shipment_id, carrier_id):
    return SimpleNamespace(
        **request_json("POST", f"{base_url()}/api/shipments/{shipment_id}/assign/", {"carrier_id": carrier_id})
    )


def add_route_event(shipment_id, status, location="", note=""):
    return SimpleNamespace(
        **request_json(
            "POST",
            f"{base_url()}/api/shipments/{shipment_id}/events/",
            {"status": status, "location": location, "note": note},
        )
    )
