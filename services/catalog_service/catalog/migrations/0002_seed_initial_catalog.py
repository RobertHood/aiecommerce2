from decimal import Decimal

from django.db import migrations


PRODUCTS = [
    {
        "category": ("Audio", "audio"),
        "name": "Quantum Audio Pro",
        "slug": "quantum-audio-pro",
        "price": Decimal("299.00"),
        "original_price": Decimal("399.00"),
        "icon": "fa-headphones",
        "color": "#6366f1",
        "short_desc": "Noise-cancelling wireless headphones with adaptive sound profiles.",
        "description": "Wireless headphones with adaptive noise cancellation and long battery life.",
        "features": [
            "30-hour battery life with ANC on",
            "Adaptive noise cancellation",
            "Hi-Res Audio certified",
            "Multi-device Bluetooth pairing",
            "Foldable, premium build",
        ],
        "rating": Decimal("4.8"),
        "reviews": 1243,
        "stock": 15,
    },
    {
        "category": ("Computing", "computing"),
        "name": "DevStation X1",
        "slug": "devstation-x1",
        "price": Decimal("1499.00"),
        "original_price": Decimal("1799.00"),
        "icon": "fa-laptop-code",
        "color": "#a855f7",
        "short_desc": "High-performance computing machine designed for developers.",
        "description": "A powerful developer workstation with fast memory, SSD storage, and a sharp display.",
        "features": [
            "Intel Core i9 class performance",
            "32 GB DDR5 RAM",
            "2 TB NVMe SSD",
            "4K OLED Display",
            "Ubuntu / Windows dual-boot ready",
        ],
        "rating": Decimal("4.9"),
        "reviews": 528,
        "stock": 8,
    },
    {
        "category": ("Photography", "photography"),
        "name": "Vision X Content Kit",
        "slug": "vision-x-content-kit",
        "price": Decimal("899.00"),
        "original_price": Decimal("1099.00"),
        "icon": "fa-camera",
        "color": "#ec4899",
        "short_desc": "4K mirrorless camera with AI-assisted focus tracking.",
        "description": "A compact mirrorless camera kit for travel creators and small studio teams.",
        "features": [
            "26 MP full-frame CMOS sensor",
            "4K 120 fps video",
            "AI subject tracking autofocus",
            "5-axis in-body stabilisation",
            "Wi-Fi and Bluetooth streaming",
        ],
        "rating": Decimal("4.7"),
        "reviews": 892,
        "stock": 22,
    },
    {
        "category": ("Wearables", "wearables"),
        "name": "LifeTracker Smartwatch",
        "slug": "lifetracker-smartwatch",
        "price": Decimal("199.00"),
        "original_price": Decimal("249.00"),
        "icon": "fa-stopwatch",
        "color": "#10b981",
        "short_desc": "Advanced biometrics monitoring with 7-day battery life.",
        "description": "A smartwatch for activity tracking, health signals, GPS, and daily notifications.",
        "features": [
            "7-day battery life",
            "Continuous ECG and SpO2 monitoring",
            "GPS + GLONASS",
            "Sleep tracking with REM analysis",
            "Water resistant to 50 m",
        ],
        "rating": Decimal("4.6"),
        "reviews": 2104,
        "stock": 40,
    },
]


def seed_catalog(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    categories = {}
    for product in PRODUCTS:
        category_name, category_slug = product["category"]
        category, _ = Category.objects.get_or_create(slug=category_slug, defaults={"name": category_name})
        categories[category_slug] = category

    for product in PRODUCTS:
        category_name, category_slug = product["category"]
        Product.objects.update_or_create(
            slug=product["slug"],
            defaults={
                "category": categories[category_slug],
                "name": product["name"],
                "price": product["price"],
                "original_price": product["original_price"],
                "icon": product["icon"],
                "color": product["color"],
                "short_desc": product["short_desc"],
                "description": product["description"],
                "features": product["features"],
                "rating": product["rating"],
                "reviews": product["reviews"],
                "stock": product["stock"],
                "is_active": True,
            },
        )


def unseed_catalog(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    Category = apps.get_model("catalog", "Category")
    Product.objects.filter(slug__in=[product["slug"] for product in PRODUCTS]).delete()
    Category.objects.filter(slug__in=[product["category"][1] for product in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_catalog, unseed_catalog),
    ]
