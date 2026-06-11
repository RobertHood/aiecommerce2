from decimal import Decimal

from django.db import migrations


PRODUCTS = [
    {
        "category": ("Accessories", "accessories"),
        "name": "AeroCharge GaN 100W",
        "slug": "aerocharge-gan-100w",
        "price": Decimal("79.00"),
        "original_price": Decimal("99.00"),
        "icon": "fa-bolt",
        "color": "#f59e0b",
        "short_desc": "Compact 100W GaN charger for laptops, tablets, and phones.",
        "description": "A travel-ready USB-C charger with four ports, smart power sharing, and temperature protection.",
        "features": [
            "100W total USB-C output",
            "Three USB-C ports and one USB-A port",
            "GaN thermal efficiency",
            "Foldable plug for travel",
            "Over-current and over-temperature protection",
        ],
        "rating": Decimal("4.7"),
        "reviews": 764,
        "stock": 55,
    },
    {
        "category": ("Computing", "computing"),
        "name": "PixelDock Thunderbolt Hub",
        "slug": "pixeldock-thunderbolt-hub",
        "price": Decimal("249.00"),
        "original_price": Decimal("299.00"),
        "icon": "fa-network-wired",
        "color": "#0ea5e9",
        "short_desc": "Thunderbolt dock with display, Ethernet, card reader, and fast charging.",
        "description": "A single-cable workstation dock for creators and developers who need more ports on a laptop.",
        "features": [
            "Dual 4K monitor output",
            "2.5 Gb Ethernet",
            "SD and microSD card readers",
            "90W laptop charging",
            "Aluminum heat-dissipating body",
        ],
        "rating": Decimal("4.6"),
        "reviews": 421,
        "stock": 18,
    },
    {
        "category": ("Networking", "networking"),
        "name": "HomeMesh WiFi 7 Router",
        "slug": "homemesh-wifi-7-router",
        "price": Decimal("349.00"),
        "original_price": Decimal("429.00"),
        "icon": "fa-wifi",
        "color": "#14b8a6",
        "short_desc": "Tri-band WiFi 7 mesh router for low-latency whole-home coverage.",
        "description": "A high-speed router for streaming, gaming, smart home devices, and dense apartment networks.",
        "features": [
            "WiFi 7 tri-band connectivity",
            "Up to 5,000 sq ft mesh coverage",
            "Low-latency gaming mode",
            "Built-in parental controls",
            "2.5 Gb WAN/LAN port",
        ],
        "rating": Decimal("4.8"),
        "reviews": 613,
        "stock": 25,
    },
    {
        "category": ("Home Entertainment", "home-entertainment"),
        "name": "StreamBeam 4K Projector",
        "slug": "streambeam-4k-projector",
        "price": Decimal("699.00"),
        "original_price": Decimal("849.00"),
        "icon": "fa-video",
        "color": "#8b5cf6",
        "short_desc": "Portable 4K smart projector with auto focus and vivid HDR color.",
        "description": "A living-room and dorm-friendly projector with built-in streaming apps and powerful speakers.",
        "features": [
            "4K UHD projection",
            "Auto focus and keystone correction",
            "HDR10 support",
            "Built-in 20W stereo speakers",
            "Wi-Fi and Bluetooth casting",
        ],
        "rating": Decimal("4.5"),
        "reviews": 338,
        "stock": 12,
    },
    {
        "category": ("Tablets", "tablets"),
        "name": "NovaTab S12",
        "slug": "novatab-s12",
        "price": Decimal("549.00"),
        "original_price": Decimal("649.00"),
        "icon": "fa-tablet-screen-button",
        "color": "#06b6d4",
        "short_desc": "12-inch tablet for note-taking, streaming, and lightweight productivity.",
        "description": "A slim tablet with a bright display, stylus support, and enough power for study or travel.",
        "features": [
            "12.2-inch 120 Hz display",
            "Stylus and keyboard cover support",
            "128 GB storage",
            "Quad speakers",
            "All-day battery life",
        ],
        "rating": Decimal("4.6"),
        "reviews": 986,
        "stock": 30,
    },
    {
        "category": ("Gaming", "gaming"),
        "name": "GameSphere Handheld",
        "slug": "gamesphere-handheld",
        "price": Decimal("599.00"),
        "original_price": Decimal("699.00"),
        "icon": "fa-gamepad",
        "color": "#ef4444",
        "short_desc": "Portable gaming PC with a 120 Hz display and ergonomic controls.",
        "description": "A handheld gaming system for PC titles, cloud gaming, and couch co-op sessions.",
        "features": [
            "7-inch 120 Hz display",
            "Custom performance profiles",
            "Hall-effect joysticks",
            "512 GB NVMe storage",
            "USB-C external display support",
        ],
        "rating": Decimal("4.7"),
        "reviews": 744,
        "stock": 16,
    },
    {
        "category": ("Smart Home", "smart-home"),
        "name": "SecureCam Mini 2K",
        "slug": "securecam-mini-2k",
        "price": Decimal("129.00"),
        "original_price": Decimal("159.00"),
        "icon": "fa-shield-halved",
        "color": "#22c55e",
        "short_desc": "Indoor/outdoor 2K security camera with AI motion alerts.",
        "description": "A compact camera for home monitoring with night vision, local storage, and app notifications.",
        "features": [
            "2K video with HDR",
            "AI person and package detection",
            "Color night vision",
            "IP65 weather resistance",
            "Local microSD recording",
        ],
        "rating": Decimal("4.4"),
        "reviews": 1142,
        "stock": 48,
    },
    {
        "category": ("Audio", "audio"),
        "name": "EchoBuds Lite",
        "slug": "echobuds-lite",
        "price": Decimal("89.00"),
        "original_price": Decimal("119.00"),
        "icon": "fa-ear-listen",
        "color": "#6366f1",
        "short_desc": "Lightweight true wireless earbuds with ANC and clear calls.",
        "description": "Everyday earbuds with active noise cancellation, low-latency mode, and pocketable charging case.",
        "features": [
            "Active noise cancellation",
            "28-hour total battery with case",
            "Low-latency gaming mode",
            "IPX5 sweat resistance",
            "Four-microphone call clarity",
        ],
        "rating": Decimal("4.5"),
        "reviews": 1760,
        "stock": 70,
    },
    {
        "category": ("Computing", "computing"),
        "name": "UltraView 32 Monitor",
        "slug": "ultraview-32-monitor",
        "price": Decimal("449.00"),
        "original_price": Decimal("549.00"),
        "icon": "fa-display",
        "color": "#3b82f6",
        "short_desc": "32-inch 4K monitor for coding, design, and entertainment.",
        "description": "A sharp productivity monitor with accurate color, USB-C display input, and ergonomic stand.",
        "features": [
            "32-inch 4K IPS panel",
            "98% DCI-P3 color coverage",
            "USB-C display and 65W charging",
            "Height, tilt, and swivel stand",
            "Eye comfort low-blue-light mode",
        ],
        "rating": Decimal("4.8"),
        "reviews": 532,
        "stock": 20,
    },
    {
        "category": ("Smart Home", "smart-home"),
        "name": "SmartAir Purifier X",
        "slug": "smartair-purifier-x",
        "price": Decimal("229.00"),
        "original_price": Decimal("279.00"),
        "icon": "fa-wind",
        "color": "#84cc16",
        "short_desc": "Connected air purifier with HEPA filtration and air quality tracking.",
        "description": "A quiet smart purifier for bedrooms and offices with app control and real-time PM2.5 monitoring.",
        "features": [
            "True HEPA H13 filter",
            "PM2.5 and VOC sensors",
            "Quiet sleep mode",
            "App and voice assistant control",
            "Covers rooms up to 500 sq ft",
        ],
        "rating": Decimal("4.6"),
        "reviews": 689,
        "stock": 34,
    },
]


def seed_catalog(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    categories = {}
    for product in PRODUCTS:
        category_name, category_slug = product["category"]
        category, _ = Category.objects.get_or_create(
            slug=category_slug,
            defaults={"name": category_name},
        )
        categories[category_slug] = category

    for product in PRODUCTS:
        category_slug = product["category"][1]
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
    slugs = [product["slug"] for product in PRODUCTS]
    category_slugs = {product["category"][1] for product in PRODUCTS}
    Product.objects.filter(slug__in=slugs).delete()
    Category.objects.filter(slug__in=category_slugs, products__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_seed_initial_catalog"),
    ]

    operations = [
        migrations.RunPython(seed_catalog, unseed_catalog),
    ]
