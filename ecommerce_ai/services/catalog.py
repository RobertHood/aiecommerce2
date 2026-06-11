from decimal import Decimal
from types import SimpleNamespace

from django.conf import settings
from django.urls import reverse

from .http import request_json


class ProductDTO:
    def __init__(self, data):
        self.id = data["id"]
        self.category = SimpleNamespace(**data["category"])
        self.name = data["name"]
        self.slug = data["slug"]
        self.price = Decimal(str(data["price"]))
        original_price = data.get("original_price")
        self.original_price = None if original_price is None else Decimal(str(original_price))
        self.icon = data["icon"]
        self.color = data["color"]
        self.short_desc = data["short_desc"]
        self.description = data["description"]
        self.features = data.get("features", [])
        self.rating = Decimal(str(data["rating"]))
        self.reviews = data["reviews"]
        self.stock = data["stock"]
        self.is_active = data["is_active"]

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"product_id": self.id})

    @property
    def display_price(self):
        return int(self.price) if self.price == self.price.to_integral() else self.price

    @property
    def display_original_price(self):
        if not self.original_price:
            return None
        return int(self.original_price) if self.original_price == self.original_price.to_integral() else self.original_price

    @property
    def savings(self):
        if not self.original_price:
            return Decimal("0.00")
        return max(self.original_price - self.price, Decimal("0.00"))

    @property
    def in_stock(self):
        return self.stock > 0


def base_url():
    return settings.CATALOG_SERVICE_URL.rstrip("/")


def list_categories():
    data = request_json("GET", f"{base_url()}/api/categories/")
    return [SimpleNamespace(**category) for category in data.get("results", [])]


def list_products():
    data = request_json("GET", f"{base_url()}/api/products/")
    return [ProductDTO(product) for product in data.get("results", [])]


def get_product(product_id):
    return ProductDTO(request_json("GET", f"{base_url()}/api/products/{product_id}/"))
