from decimal import Decimal
import importlib
import json

from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Category, Order, OrderItem, Product


TAX_RATE = Decimal("0.08")


def get_cart(request):
    return request.session.get("cart", {})


def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def cart_count(cart):
    return sum(int(quantity) for quantity in cart.values())


def cart_totals(cart):
    product_ids = [int(product_id) for product_id in cart.keys() if str(product_id).isdigit()]
    products = Product.objects.filter(id__in=product_ids, is_active=True).select_related("category")
    products_by_id = {product.id: product for product in products}

    items = []
    subtotal = Decimal("0.00")

    for product_id, quantity in cart.items():
        if not str(product_id).isdigit():
            continue

        product = products_by_id.get(int(product_id))
        if not product:
            continue

        quantity = max(int(quantity), 0)
        if quantity <= 0:
            continue

        line_total = product.price * quantity
        subtotal += line_total
        items.append(
            {
                "product": product,
                "id": product.id,
                "name": product.name,
                "category": product.category.name,
                "price": product.price,
                "original_price": product.original_price,
                "icon": product.icon,
                "color": product.color,
                "quantity": quantity,
                "line_total": line_total,
                "stock": product.stock,
            }
        )

    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
    total = subtotal + tax
    return items, subtotal, tax, total


def json_body(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON format"}, status=400)


rag_chain = None
rag_module = None


def get_chain():
    global rag_chain, rag_module
    if rag_chain is None:
        try:
            rag_module = importlib.import_module("rag_chat")
            rag_chain = rag_module.setup_rag()
        except ImportError:
            return None
    return rag_chain


@ensure_csrf_cookie
def home(request):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True).select_related("category")
    cart = get_cart(request)
    return render(
        request,
        "ecommerce_ai/index.html",
        {
            "categories": categories,
            "products": products,
            "cart_count": cart_count(cart),
        },
    )


@ensure_csrf_cookie
def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        id=product_id,
        is_active=True,
    )
    related = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(id=product.id)
        .select_related("category")[:4]
    )
    if not related:
        related = Product.objects.filter(is_active=True).exclude(id=product.id).select_related("category")[:4]

    cart = get_cart(request)
    return render(
        request,
        "ecommerce_ai/product_detail.html",
        {
            "product": product,
            "related": related,
            "cart_count": cart_count(cart),
            "savings": product.savings,
        },
    )


@ensure_csrf_cookie
def cart(request):
    cart_data = get_cart(request)
    items, subtotal, tax, total = cart_totals(cart_data)
    return render(
        request,
        "ecommerce_ai/cart.html",
        {
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "cart_count": cart_count(cart_data),
        },
    )


@ensure_csrf_cookie
def checkout(request):
    cart_data = get_cart(request)
    items, subtotal, tax, total = cart_totals(cart_data)
    if not items:
        return redirect("cart")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        full_name = f"{first_name} {last_name}".strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()

        if not all([full_name, email, address, city, postal_code]):
            messages.error(request, "Please complete all required checkout fields.")
        else:
            try:
                with transaction.atomic():
                    locked_products = {
                        product.id: product
                        for product in Product.objects.select_for_update().filter(
                            id__in=[item["id"] for item in items],
                            is_active=True,
                        )
                    }

                    for item in items:
                        product = locked_products.get(item["id"])
                        if not product or product.stock < item["quantity"]:
                            raise ValueError(f"{item['name']} does not have enough stock.")

                    order = Order.objects.create(
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        address=address,
                        city=city,
                        postal_code=postal_code,
                        subtotal=subtotal,
                        tax=tax,
                        total=total,
                    )

                    for item in items:
                        product = locked_products[item["id"]]
                        line_total = product.price * item["quantity"]
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            unit_price=product.price,
                            quantity=item["quantity"],
                            line_total=line_total,
                        )
                        Product.objects.filter(id=product.id).update(stock=F("stock") - item["quantity"])

                save_cart(request, {})
                return redirect("checkout_success", order_id=order.id)
            except ValueError as exc:
                messages.error(request, str(exc))

    return render(
        request,
        "ecommerce_ai/checkout.html",
        {
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "cart_count": cart_count(cart_data),
        },
    )


def checkout_success(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
    return render(request, "ecommerce_ai/checkout_success.html", {"order": order, "cart_count": 0})


def cart_add(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = json_body(request)
    if error:
        return error

    try:
        product_id = int(data.get("product_id"))
        quantity = max(int(data.get("quantity", 1)), 1)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid product or quantity"}, status=400)

    product = Product.objects.filter(id=product_id, is_active=True).first()
    if not product:
        return JsonResponse({"error": "Product not found"}, status=404)

    if product.stock <= 0:
        return JsonResponse({"error": "Product is out of stock"}, status=400)

    cart_data = get_cart(request)
    current_quantity = int(cart_data.get(str(product_id), 0))
    cart_data[str(product_id)] = min(current_quantity + quantity, product.stock)
    save_cart(request, cart_data)
    return JsonResponse({"success": True, "cart_count": cart_count(cart_data)})


def cart_remove(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = json_body(request)
    if error:
        return error

    product_id = str(data.get("product_id"))
    cart_data = get_cart(request)
    cart_data.pop(product_id, None)
    save_cart(request, cart_data)

    items, subtotal, tax, total = cart_totals(cart_data)
    return JsonResponse(
        {
            "success": True,
            "cart_count": cart_count(cart_data),
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
        }
    )


def cart_update(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = json_body(request)
    if error:
        return error

    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid product or quantity"}, status=400)

    cart_data = get_cart(request)
    product = Product.objects.filter(id=product_id, is_active=True).first()

    if quantity <= 0:
        cart_data.pop(str(product_id), None)
    elif not product:
        return JsonResponse({"error": "Product not found"}, status=404)
    else:
        cart_data[str(product_id)] = min(quantity, product.stock)

    save_cart(request, cart_data)
    items, subtotal, tax, total = cart_totals(cart_data)
    return JsonResponse(
        {
            "success": True,
            "cart_count": cart_count(cart_data),
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
        }
    )


def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = json_body(request)
    if error:
        return error

    message = data.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    chain = get_chain()
    if not chain:
        return JsonResponse(
            {"error": "RAG system is not initialized. Ensure GROQ_API_KEY is configured and Neo4j is running."},
            status=500,
        )

    try:
        response_text = rag_module.ask_question(chain, message)
        return JsonResponse({"response": response_text})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
