from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .cart_ops import cart_count, cart_totals, get_active_product, get_cart, save_cart
from .checkout_ops import checkout_customer_from_post, create_checkout_order, has_required_customer_fields
from .customer_session import auth_context, clear_current_customer, current_customer, set_current_customer
from .http_utils import json_body
from .models import Category, Order, Product
from .rag import get_chain
from .services import ai as ai_service
from .services import catalog as catalog_service
from .services import orders as order_service
from .services import users as user_service
from .services.http import ServiceError


@ensure_csrf_cookie
def home(request):
    if settings.USE_MICROSERVICES:
        categories = catalog_service.list_categories()
        products = catalog_service.list_products()
    else:
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
            **auth_context(request),
        },
    )


@ensure_csrf_cookie
def product_detail(request, product_id):
    if settings.USE_MICROSERVICES:
        try:
            product = catalog_service.get_product(product_id)
            related = [
                candidate
                for candidate in catalog_service.list_products()
                if candidate.id != product.id and candidate.category.id == product.category.id
            ][:4]
            if not related:
                related = [candidate for candidate in catalog_service.list_products() if candidate.id != product.id][:4]
        except ServiceError:
            return redirect("home")
    else:
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
            **auth_context(request),
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
            **auth_context(request),
        },
    )


@ensure_csrf_cookie
def checkout(request):
    cart_data = get_cart(request)
    items, subtotal, tax, total = cart_totals(cart_data)
    if not items:
        return redirect("cart")

    if request.method == "POST":
        customer = checkout_customer_from_post(request.POST)

        if not has_required_customer_fields(customer):
            messages.error(request, "Please complete all required checkout fields.")
        else:
            try:
                order = create_checkout_order(customer, items, subtotal, tax, total)
                save_cart(request, {})
                return redirect("checkout_success", order_id=order.id)
            except ServiceError as exc:
                messages.error(request, str(exc))
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
            **auth_context(request),
        },
    )


def checkout_success(request, order_id):
    if settings.USE_MICROSERVICES:
        try:
            order = order_service.get_order(order_id)
        except ServiceError:
            return redirect("home")
    else:
        order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
    return render(request, "ecommerce_ai/checkout_success.html", {"order": order, "cart_count": 0, **auth_context(request)})


@ensure_csrf_cookie
def register(request):
    if request.method == "POST":
        payload = {
            "email": request.POST.get("email", "").strip(),
            "password": request.POST.get("password", ""),
            "full_name": request.POST.get("full_name", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "address": request.POST.get("address", "").strip(),
            "city": request.POST.get("city", "").strip(),
            "postal_code": request.POST.get("postal_code", "").strip(),
        }
        try:
            customer = user_service.register_user(payload)
            set_current_customer(request, customer)
            messages.success(request, "Account created successfully.")
            return redirect("account")
        except ServiceError as exc:
            messages.error(request, str(exc))

    return render(request, "ecommerce_ai/register.html", {"cart_count": cart_count(get_cart(request)), **auth_context(request)})


@ensure_csrf_cookie
def login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        try:
            result = user_service.login_user(email, password)
            set_current_customer(request, result["user"])
            messages.success(request, "Signed in successfully.")
            return redirect("account")
        except ServiceError as exc:
            messages.error(request, str(exc))

    return render(request, "ecommerce_ai/login.html", {"cart_count": cart_count(get_cart(request)), **auth_context(request)})


def logout(request):
    clear_current_customer(request)
    return redirect("home")


@ensure_csrf_cookie
def account(request):
    customer = current_customer(request)
    if not customer:
        return redirect("login")

    try:
        profile = user_service.get_user(customer["id"])
    except ServiceError as exc:
        messages.error(request, str(exc))
        profile = None

    return render(
        request,
        "ecommerce_ai/account.html",
        {
            "profile": profile,
            "cart_count": cart_count(get_cart(request)),
            **auth_context(request),
        },
    )


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

    product = get_active_product(product_id)
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
    product = get_active_product(product_id)

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

    if settings.USE_MICROSERVICES:
        try:
            return JsonResponse(ai_service.ask(message))
        except ServiceError as exc:
            fallback_response = ask_local_rag(message)
            if fallback_response:
                return JsonResponse({"response": fallback_response, "source": "local-rag-fallback"})
            return JsonResponse(
                {
                    "error": (
                        f"{exc}. Start AI service or set AI_SERVICE_URL to the running AI service URL."
                    )
                },
                status=503,
            )

    response_text = ask_local_rag(message)
    if response_text:
        return JsonResponse({"response": response_text})

    return JsonResponse(
        {"error": "RAG system is not initialized. Ensure GROQ_API_KEY is configured and Neo4j is running."},
        status=500,
    )


def ask_local_rag(message):
    chain, rag_module = get_chain()
    if not chain:
        return None

    try:
        return rag_module.ask_question(chain, message)
    except Exception:
        return None
