import json

from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Product


def decimal_to_string(value):
    return None if value is None else str(value)


def product_payload(product):
    return {
        "id": product.id,
        "category": {
            "id": product.category_id,
            "name": product.category.name,
            "slug": product.category.slug,
        },
        "name": product.name,
        "slug": product.slug,
        "price": decimal_to_string(product.price),
        "original_price": decimal_to_string(product.original_price),
        "icon": product.icon,
        "color": product.color,
        "short_desc": product.short_desc,
        "description": product.description,
        "features": product.features,
        "rating": decimal_to_string(product.rating),
        "reviews": product.reviews,
        "stock": product.stock,
        "is_active": product.is_active,
    }


def parse_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON format"}, status=400)


def health(request):
    return JsonResponse({"service": "catalog", "status": "ok"})


def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return JsonResponse(
        {
            "results": [
                {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                    "description": category.description,
                }
                for category in categories
            ]
        }
    )


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    return JsonResponse({"results": [product_payload(product) for product in products]})


def product_detail(request, product_id):
    product = Product.objects.filter(id=product_id, is_active=True).select_related("category").first()
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)
    return JsonResponse(product_payload(product))


@csrf_exempt
def reserve_stock(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    items = data.get("items", [])
    if not isinstance(items, list) or not items:
        return JsonResponse({"error": "items must be a non-empty list"}, status=400)

    try:
        with transaction.atomic():
            reserved = []
            for item in items:
                product_id = int(item["product_id"])
                quantity = int(item["quantity"])
                if quantity <= 0:
                    return JsonResponse({"error": "quantity must be positive"}, status=400)

                product = Product.objects.select_for_update().filter(id=product_id, is_active=True).first()
                if not product:
                    return JsonResponse({"error": f"Product {product_id} not found"}, status=404)
                if product.stock < quantity:
                    return JsonResponse(
                        {"error": f"{product.name} does not have enough stock", "available_stock": product.stock},
                        status=409,
                    )

                Product.objects.filter(id=product.id).update(stock=F("stock") - quantity)
                reserved.append({"product_id": product.id, "quantity": quantity})

        return JsonResponse({"success": True, "reserved": reserved})
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"error": "Invalid stock reservation payload"}, status=400)
