import json
import uuid

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Carrier, RouteEvent, Shipment


def parse_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON format"}, status=400)


def carrier_payload(carrier):
    return {
        "id": carrier.id,
        "code": carrier.code,
        "name": carrier.name,
        "contact_phone": carrier.contact_phone,
        "service_level": carrier.service_level,
        "base_fee": str(carrier.base_fee),
        "is_active": carrier.is_active,
    }


def route_event_payload(event):
    return {
        "id": event.id,
        "status": event.status,
        "location": event.location,
        "note": event.note,
        "occurred_at": event.occurred_at.isoformat(),
    }


def shipment_payload(shipment):
    return {
        "id": shipment.id,
        "order_id": shipment.order_id,
        "carrier": None if not shipment.carrier else carrier_payload(shipment.carrier),
        "tracking_number": shipment.tracking_number,
        "recipient_name": shipment.recipient_name,
        "recipient_phone": shipment.recipient_phone,
        "destination_address": shipment.destination_address,
        "destination_city": shipment.destination_city,
        "postal_code": shipment.postal_code,
        "status": shipment.status,
        "estimated_delivery": None if not shipment.estimated_delivery else shipment.estimated_delivery.isoformat(),
        "route_events": [route_event_payload(event) for event in shipment.route_events.all()],
    }


def health(request):
    return JsonResponse({"service": "shipping", "status": "ok"})


@csrf_exempt
def carrier_list_create(request):
    if request.method == "GET":
        carriers = Carrier.objects.all()
        return JsonResponse({"results": [carrier_payload(carrier) for carrier in carriers]})
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    code = str(data.get("code", "")).strip().lower()
    name = str(data.get("name", "")).strip()
    if not code or not name:
        return JsonResponse({"error": "code and name are required"}, status=400)

    carrier, created = Carrier.objects.get_or_create(
        code=code,
        defaults={
            "name": name,
            "contact_phone": data.get("contact_phone", ""),
            "service_level": data.get("service_level", "standard"),
            "base_fee": data.get("base_fee", 0),
        },
    )
    return JsonResponse(carrier_payload(carrier), status=201 if created else 200)


@csrf_exempt
def shipment_list_create(request):
    if request.method == "GET":
        shipments = Shipment.objects.select_related("carrier").prefetch_related("route_events")
        return JsonResponse({"results": [shipment_payload(shipment) for shipment in shipments]})
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    try:
        shipment = Shipment.objects.create(
            order_id=int(data["order_id"]),
            recipient_name=str(data["recipient_name"]).strip(),
            recipient_phone=str(data.get("recipient_phone", "")).strip(),
            destination_address=str(data["destination_address"]).strip(),
            destination_city=str(data["destination_city"]).strip(),
            postal_code=str(data.get("postal_code", "")).strip(),
            estimated_delivery=data.get("estimated_delivery") or None,
        )
        RouteEvent.objects.create(
            shipment=shipment,
            status=Shipment.STATUS_PENDING,
            location=data.get("origin_location", "Warehouse"),
            note="Shipment created",
        )
        return JsonResponse(shipment_payload(shipment), status=201)
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"error": "Invalid shipment payload"}, status=400)


def shipment_detail(request, shipment_id):
    shipment = Shipment.objects.select_related("carrier").prefetch_related("route_events").filter(id=shipment_id).first()
    if not shipment:
        return JsonResponse({"error": "Shipment not found"}, status=404)
    return JsonResponse(shipment_payload(shipment))


@csrf_exempt
def shipment_assign(request, shipment_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    shipment = Shipment.objects.select_related("carrier").filter(id=shipment_id).first()
    if not shipment:
        return JsonResponse({"error": "Shipment not found"}, status=404)

    try:
        carrier = Carrier.objects.get(id=int(data["carrier_id"]), is_active=True)
    except (KeyError, ValueError, Carrier.DoesNotExist):
        return JsonResponse({"error": "Valid carrier_id is required"}, status=400)

    shipment.carrier = carrier
    shipment.status = Shipment.STATUS_ASSIGNED
    shipment.tracking_number = shipment.tracking_number or f"NX-{uuid.uuid4().hex[:10].upper()}"
    shipment.save(update_fields=["carrier", "status", "tracking_number", "updated_at"])
    RouteEvent.objects.create(
        shipment=shipment,
        status=Shipment.STATUS_ASSIGNED,
        location=data.get("location", "Dispatch center"),
        note=f"Assigned to {carrier.name}",
    )
    return JsonResponse(shipment_payload(shipment))


@csrf_exempt
def shipment_event_create(request, shipment_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    shipment = Shipment.objects.select_related("carrier").filter(id=shipment_id).first()
    if not shipment:
        return JsonResponse({"error": "Shipment not found"}, status=404)

    status = data.get("status")
    if status not in dict(Shipment.STATUS_CHOICES):
        return JsonResponse({"error": "Invalid shipment status"}, status=400)

    shipment.status = status
    shipment.save(update_fields=["status", "updated_at"])
    RouteEvent.objects.create(
        shipment=shipment,
        status=status,
        location=data.get("location", ""),
        note=data.get("note", ""),
    )
    return JsonResponse(shipment_payload(shipment))
