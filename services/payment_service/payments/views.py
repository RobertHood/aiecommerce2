from decimal import Decimal
import json
import uuid

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Payment


def parse_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON format"}, status=400)


def payment_payload(payment):
    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "customer_email": payment.customer_email,
        "amount": str(payment.amount),
        "currency": payment.currency,
        "method": payment.method,
        "status": payment.status,
        "transaction_id": payment.transaction_id,
        "provider_reference": payment.provider_reference,
        "failure_reason": payment.failure_reason,
        "created_at": payment.created_at.isoformat(),
        "updated_at": payment.updated_at.isoformat(),
    }


def health(request):
    return JsonResponse({"service": "payments", "status": "ok"})


@csrf_exempt
def payment_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    try:
        order_id = int(data["order_id"])
        amount = Decimal(str(data["amount"]))
        if amount <= 0:
            return JsonResponse({"error": "amount must be positive"}, status=400)
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"error": "order_id and amount are required"}, status=400)

    method = data.get("method", Payment.METHOD_COD)
    if method not in dict(Payment.METHOD_CHOICES):
        return JsonResponse({"error": "Invalid payment method"}, status=400)

    payment = Payment.objects.create(
        order_id=order_id,
        amount=amount,
        currency=data.get("currency", "USD"),
        method=method,
        customer_email=data.get("customer_email", ""),
    )
    return JsonResponse(payment_payload(payment), status=201)


def payment_detail(request, payment_id):
    payment = Payment.objects.filter(id=payment_id).first()
    if not payment:
        return JsonResponse({"error": "Payment not found"}, status=404)
    return JsonResponse(payment_payload(payment))


@csrf_exempt
def payment_confirm(request, payment_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    payment = Payment.objects.filter(id=payment_id).first()
    if not payment:
        return JsonResponse({"error": "Payment not found"}, status=404)
    if payment.status != Payment.STATUS_PENDING:
        return JsonResponse({"error": "Only pending payments can be confirmed"}, status=409)

    payment.status = Payment.STATUS_SUCCEEDED
    payment.provider_reference = data.get("provider_reference") or f"SIM-{uuid.uuid4().hex[:12]}"
    payment.save(update_fields=["status", "provider_reference", "updated_at"])
    return JsonResponse(payment_payload(payment))


@csrf_exempt
def payment_fail(request, payment_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    payment = Payment.objects.filter(id=payment_id).first()
    if not payment:
        return JsonResponse({"error": "Payment not found"}, status=404)
    if payment.status != Payment.STATUS_PENDING:
        return JsonResponse({"error": "Only pending payments can be failed"}, status=409)

    payment.status = Payment.STATUS_FAILED
    payment.failure_reason = data.get("failure_reason", "Payment failed")
    payment.save(update_fields=["status", "failure_reason", "updated_at"])
    return JsonResponse(payment_payload(payment))
