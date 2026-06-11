from django.conf import settings
from django.db import transaction
from django.db.models import F

from .models import Order, OrderItem, Product
from .services import orders as order_service
from .services import payments as payment_service


def checkout_customer_from_post(post_data):
    first_name = post_data.get("first_name", "").strip()
    last_name = post_data.get("last_name", "").strip()
    return {
        "full_name": f"{first_name} {last_name}".strip(),
        "email": post_data.get("email", "").strip(),
        "phone": post_data.get("phone", "").strip(),
        "address": post_data.get("address", "").strip(),
        "city": post_data.get("city", "").strip(),
        "postal_code": post_data.get("postal_code", "").strip(),
    }


def has_required_customer_fields(customer):
    return all(
        [
            customer["full_name"],
            customer["email"],
            customer["address"],
            customer["city"],
            customer["postal_code"],
        ]
    )


def create_checkout_order(customer, items, subtotal, tax, total):
    if settings.USE_MICROSERVICES:
        return create_microservice_order(customer, items)
    return create_local_order(customer, items, subtotal, tax, total)


def create_microservice_order(customer, items):
    order_items = [
        {
            "product_id": item["id"],
            "product_name": item["name"],
            "unit_price": str(item["price"]),
            "quantity": item["quantity"],
        }
        for item in items
    ]
    order = order_service.create_order(customer, order_items)
    payment_service.create_payment(order.id, order.total, customer_email=customer["email"], method="cod")
    return order


def create_local_order(customer, items, subtotal, tax, total):
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
            full_name=customer["full_name"],
            email=customer["email"],
            phone=customer["phone"],
            address=customer["address"],
            city=customer["city"],
            postal_code=customer["postal_code"],
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

    return order
