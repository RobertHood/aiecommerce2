import json

from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Customer


def parse_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON format"}, status=400)


def customer_payload(customer):
    return {
        "id": customer.id,
        "email": customer.email,
        "full_name": customer.full_name,
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
        "postal_code": customer.postal_code,
        "role": customer.role,
        "is_active": customer.is_active,
        "created_at": customer.created_at.isoformat(),
        "updated_at": customer.updated_at.isoformat(),
    }


def health(request):
    return JsonResponse({"service": "users", "status": "ok"})


@csrf_exempt
def user_list_create(request):
    if request.method == "GET":
        customers = Customer.objects.all()
        return JsonResponse({"results": [customer_payload(customer) for customer in customers]})

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    full_name = str(data.get("full_name", "")).strip()
    if not email or not password or not full_name:
        return JsonResponse({"error": "email, password and full_name are required"}, status=400)
    if Customer.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=409)

    customer = Customer.objects.create(
        email=email,
        password_hash=make_password(password),
        full_name=full_name,
        phone=str(data.get("phone", "")).strip(),
        address=str(data.get("address", "")).strip(),
        city=str(data.get("city", "")).strip(),
        postal_code=str(data.get("postal_code", "")).strip(),
    )
    return JsonResponse(customer_payload(customer), status=201)


@csrf_exempt
def user_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    customer = Customer.objects.filter(email=email, is_active=True).first()
    if not customer or not check_password(password, customer.password_hash):
        return JsonResponse({"error": "Invalid email or password"}, status=401)

    return JsonResponse({"authenticated": True, "user": customer_payload(customer)})


@csrf_exempt
def user_detail(request, user_id):
    customer = Customer.objects.filter(id=user_id).first()
    if not customer:
        return JsonResponse({"error": "User not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(customer_payload(customer))

    if request.method not in ["PATCH", "PUT"]:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    updatable_fields = ["full_name", "phone", "address", "city", "postal_code", "is_active", "role"]
    for field in updatable_fields:
        if field in data:
            setattr(customer, field, data[field])
    if data.get("password"):
        customer.password_hash = make_password(str(data["password"]))
    customer.save()
    return JsonResponse(customer_payload(customer))
