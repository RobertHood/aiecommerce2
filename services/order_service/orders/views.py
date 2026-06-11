from decimal import Decimal
import json

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .client import ServiceError, reserve_stock
from .models import Order, OrderItem


TAX_RATE = Decimal("0.08")


def parse_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON format"}, status=400)


def decimal_to_string(value):
    return str(value)


def order_payload(order):
    return {
        "id": order.id,
        "full_name": order.full_name,
        "email": order.email,
        "phone": order.phone,
        "address": order.address,
        "city": order.city,
        "postal_code": order.postal_code,
        "status": order.status,
        "subtotal": decimal_to_string(order.subtotal),
        "tax": decimal_to_string(order.tax),
        "total": decimal_to_string(order.total),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "unit_price": decimal_to_string(item.unit_price),
                "quantity": item.quantity,
                "line_total": decimal_to_string(item.line_total),
            }
            for item in order.items.all()
        ],
    }


def health(request):
    return JsonResponse({"service": "orders", "status": "ok"})


@csrf_exempt
def order_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    customer = data.get("customer", {})
    items = data.get("items", [])
    required_customer_fields = ["full_name", "email", "address", "city", "postal_code"]
    if not all(customer.get(field) for field in required_customer_fields):
        return JsonResponse({"error": "Missing required customer fields"}, status=400)
    if not isinstance(items, list) or not items:
        return JsonResponse({"error": "items must be a non-empty list"}, status=400)

    try:
        normalized_items = []
        subtotal = Decimal("0.00")
        stock_items = []
        for item in items:
            quantity = int(item["quantity"])
            unit_price = Decimal(str(item["unit_price"]))
            if quantity <= 0:
                return JsonResponse({"error": "quantity must be positive"}, status=400)

            line_total = unit_price * quantity
            subtotal += line_total
            product_id = int(item["product_id"])
            normalized_items.append(
                {
                    "product_id": product_id,
                    "product_name": str(item["product_name"]),
                    "unit_price": unit_price,
                    "quantity": quantity,
                    "line_total": line_total,
                }
            )
            stock_items.append({"product_id": product_id, "quantity": quantity})

        tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
        total = subtotal + tax

        with transaction.atomic():
            order = Order.objects.create(
                full_name=customer["full_name"],
                email=customer["email"],
                phone=customer.get("phone", ""),
                address=customer["address"],
                city=customer["city"],
                postal_code=customer["postal_code"],
                subtotal=subtotal,
                tax=tax,
                total=total,
            )
            for item in normalized_items:
                OrderItem.objects.create(order=order, **item)
            reserve_stock(stock_items)

        return JsonResponse(order_payload(order), status=201)
    except ServiceError as exc:
        return JsonResponse({"error": str(exc)}, status=exc.status)
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"error": "Invalid order payload"}, status=400)


def order_detail(request, order_id):
    order = Order.objects.prefetch_related("items").filter(id=order_id).first()
    if not order:
        return JsonResponse({"error": "Order not found"}, status=404)
    return JsonResponse(order_payload(order))
