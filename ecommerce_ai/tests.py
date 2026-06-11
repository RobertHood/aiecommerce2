from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, Product


class StoreFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Laptops", slug="laptops")
        self.product = Product.objects.create(
            category=self.category,
            name="Test Laptop",
            slug="test-laptop",
            price=Decimal("999.00"),
            original_price=Decimal("1199.00"),
            short_desc="Portable test computer.",
            description="A laptop used for automated tests.",
            features=["16 GB RAM", "1 TB SSD"],
            stock=5,
            rating=Decimal("4.8"),
            reviews=10,
        )

    def test_home_lists_products(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Laptop")

    def test_cart_add_update_and_remove(self):
        add_response = self.client.post(
            reverse("cart_add"),
            data={"product_id": self.product.id, "quantity": 2},
            content_type="application/json",
        )

        self.assertEqual(add_response.status_code, 200)
        self.assertEqual(add_response.json()["cart_count"], 2)

        update_response = self.client.post(
            reverse("cart_update"),
            data={"product_id": self.product.id, "quantity": 3},
            content_type="application/json",
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["cart_count"], 3)
        self.assertEqual(update_response.json()["subtotal"], "2997.00")

        remove_response = self.client.post(
            reverse("cart_remove"),
            data={"product_id": self.product.id},
            content_type="application/json",
        )

        self.assertEqual(remove_response.status_code, 200)
        self.assertEqual(remove_response.json()["cart_count"], 0)

    def test_checkout_creates_order_and_reduces_stock(self):
        self.client.post(
            reverse("cart_add"),
            data={"product_id": self.product.id, "quantity": 2},
            content_type="application/json",
        )

        response = self.client.post(
            reverse("checkout"),
            data={
                "first_name": "Alex",
                "last_name": "Morgan",
                "email": "alex@example.com",
                "phone": "+6600000000",
                "address": "123 Market Street",
                "city": "Bangkok",
                "postal_code": "10110",
            },
        )

        self.assertEqual(response.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, Decimal("2157.84"))

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
