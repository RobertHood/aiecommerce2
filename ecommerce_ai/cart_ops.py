from decimal import Decimal

from django.conf import settings

from .models import Product
from .services import catalog as catalog_service
from .services.http import ServiceError


TAX_RATE = Decimal("0.08")


def get_cart(request):
    return request.session.get("cart", {})


def save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def cart_count(cart):
    return sum(int(quantity) for quantity in cart.values())


def get_active_product(product_id):
    if settings.USE_MICROSERVICES:
        try:
            return catalog_service.get_product(product_id)
        except ServiceError:
            return None
    return Product.objects.filter(id=product_id, is_active=True).first()


def get_products_by_id(product_ids):
    if settings.USE_MICROSERVICES:
        products_by_id = {}
        for product_id in product_ids:
            product = get_active_product(product_id)
            if product:
                products_by_id[product.id] = product
        return products_by_id

    products = Product.objects.filter(id__in=product_ids, is_active=True).select_related("category")
    return {product.id: product for product in products}


def cart_totals(cart):
    product_ids = [int(product_id) for product_id in cart.keys() if str(product_id).isdigit()]
    products_by_id = get_products_by_id(product_ids)

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
