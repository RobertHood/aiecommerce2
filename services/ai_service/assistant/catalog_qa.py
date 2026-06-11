import json
import re
from decimal import Decimal, InvalidOperation
from urllib.error import URLError
from urllib.request import urlopen

from django.conf import settings


FALLBACK_PRODUCTS = [
    {
        "name": "Quantum Audio Pro",
        "category": {"name": "Audio"},
        "price": "299.00",
        "original_price": "399.00",
        "short_desc": "Noise-cancelling wireless headphones with adaptive sound profiles.",
        "description": "Premium wireless headphones with ANC, adaptive EQ, and long battery life.",
        "features": ["30-hour battery life", "Adaptive noise cancellation", "Hi-Res Audio"],
        "rating": "4.8",
        "reviews": 1243,
        "stock": 15,
    },
    {
        "name": "DevStation X1",
        "category": {"name": "Computing"},
        "price": "1499.00",
        "original_price": "1799.00",
        "short_desc": "High-performance computing machine designed for developers.",
        "description": "A developer workstation with fast CPU, 32 GB RAM, 2 TB NVMe SSD, and 4K OLED display.",
        "features": ["Intel Core i9 class performance", "32 GB DDR5 RAM", "2 TB NVMe SSD", "4K OLED Display"],
        "rating": "4.9",
        "reviews": 528,
        "stock": 8,
    },
    {
        "name": "Vision X Content Kit",
        "category": {"name": "Photography"},
        "price": "899.00",
        "original_price": "1099.00",
        "short_desc": "4K mirrorless camera with AI-assisted focus tracking.",
        "description": "A compact content creation camera kit for video, travel, and small studio teams.",
        "features": ["26 MP sensor", "4K 120 fps video", "AI subject tracking", "5-axis stabilisation"],
        "rating": "4.7",
        "reviews": 892,
        "stock": 22,
    },
    {
        "name": "LifeTracker Smartwatch",
        "category": {"name": "Wearables"},
        "price": "199.00",
        "original_price": "249.00",
        "short_desc": "Advanced biometrics monitoring with 7-day battery life.",
        "description": "A smartwatch for activity tracking, health signals, GPS, and daily notifications.",
        "features": ["7-day battery", "ECG and SpO2", "GPS", "Sleep tracking", "50 m water resistance"],
        "rating": "4.6",
        "reviews": 2104,
        "stock": 40,
    },
    {
        "name": "AeroCharge GaN 100W",
        "category": {"name": "Accessories"},
        "price": "79.00",
        "original_price": "99.00",
        "short_desc": "Compact 100W GaN charger for laptops, tablets, and phones.",
        "description": "A travel-ready USB-C charger with four ports and smart power sharing.",
        "features": ["100W USB-C output", "Four ports", "GaN efficiency", "Foldable plug"],
        "rating": "4.7",
        "reviews": 764,
        "stock": 55,
    },
    {
        "name": "PixelDock Thunderbolt Hub",
        "category": {"name": "Computing"},
        "price": "249.00",
        "original_price": "299.00",
        "short_desc": "Thunderbolt dock with display, Ethernet, card reader, and fast charging.",
        "description": "A single-cable workstation dock for creators and developers.",
        "features": ["Dual 4K output", "2.5 Gb Ethernet", "SD readers", "90W laptop charging"],
        "rating": "4.6",
        "reviews": 421,
        "stock": 18,
    },
    {
        "name": "HomeMesh WiFi 7 Router",
        "category": {"name": "Networking"},
        "price": "349.00",
        "original_price": "429.00",
        "short_desc": "Tri-band WiFi 7 mesh router for low-latency whole-home coverage.",
        "description": "A high-speed router for streaming, gaming, smart home, and dense apartment networks.",
        "features": ["WiFi 7", "Mesh coverage", "Gaming mode", "Parental controls", "2.5 Gb port"],
        "rating": "4.8",
        "reviews": 613,
        "stock": 25,
    },
    {
        "name": "StreamBeam 4K Projector",
        "category": {"name": "Home Entertainment"},
        "price": "699.00",
        "original_price": "849.00",
        "short_desc": "Portable 4K smart projector with auto focus and vivid HDR color.",
        "description": "A smart projector with built-in streaming apps and powerful speakers.",
        "features": ["4K UHD", "Auto focus", "HDR10", "20W stereo speakers", "Wi-Fi casting"],
        "rating": "4.5",
        "reviews": 338,
        "stock": 12,
    },
    {
        "name": "NovaTab S12",
        "category": {"name": "Tablets"},
        "price": "549.00",
        "original_price": "649.00",
        "short_desc": "12-inch tablet for note-taking, streaming, and lightweight productivity.",
        "description": "A slim tablet with a bright display, stylus support, and all-day battery.",
        "features": ["12.2-inch 120 Hz display", "Stylus support", "128 GB storage", "Quad speakers"],
        "rating": "4.6",
        "reviews": 986,
        "stock": 30,
    },
    {
        "name": "GameSphere Handheld",
        "category": {"name": "Gaming"},
        "price": "599.00",
        "original_price": "699.00",
        "short_desc": "Portable gaming PC with a 120 Hz display and ergonomic controls.",
        "description": "A handheld gaming system for PC titles, cloud gaming, and couch co-op sessions.",
        "features": ["120 Hz display", "Performance profiles", "Hall-effect joysticks", "512 GB NVMe"],
        "rating": "4.7",
        "reviews": 744,
        "stock": 16,
    },
    {
        "name": "SecureCam Mini 2K",
        "category": {"name": "Smart Home"},
        "price": "129.00",
        "original_price": "159.00",
        "short_desc": "Indoor/outdoor 2K security camera with AI motion alerts.",
        "description": "A compact camera for home monitoring with night vision and app notifications.",
        "features": ["2K HDR video", "AI detection", "Color night vision", "IP65 weather resistance"],
        "rating": "4.4",
        "reviews": 1142,
        "stock": 48,
    },
    {
        "name": "EchoBuds Lite",
        "category": {"name": "Audio"},
        "price": "89.00",
        "original_price": "119.00",
        "short_desc": "Lightweight true wireless earbuds with ANC and clear calls.",
        "description": "Everyday earbuds with ANC, low-latency mode, and pocketable charging case.",
        "features": ["ANC", "28-hour battery", "Low-latency mode", "IPX5 sweat resistance"],
        "rating": "4.5",
        "reviews": 1760,
        "stock": 70,
    },
    {
        "name": "UltraView 32 Monitor",
        "category": {"name": "Computing"},
        "price": "449.00",
        "original_price": "549.00",
        "short_desc": "32-inch 4K monitor for coding, design, and entertainment.",
        "description": "A sharp productivity monitor with accurate color, USB-C input, and ergonomic stand.",
        "features": ["32-inch 4K IPS", "98% DCI-P3", "USB-C 65W charging", "Ergonomic stand"],
        "rating": "4.8",
        "reviews": 532,
        "stock": 20,
    },
    {
        "name": "SmartAir Purifier X",
        "category": {"name": "Smart Home"},
        "price": "229.00",
        "original_price": "279.00",
        "short_desc": "Connected air purifier with HEPA filtration and air quality tracking.",
        "description": "A quiet smart purifier for bedrooms and offices with app control and real-time PM2.5 monitoring.",
        "features": ["HEPA H13", "PM2.5 sensors", "Quiet sleep mode", "App and voice control"],
        "rating": "4.6",
        "reviews": 689,
        "stock": 34,
    },
]


CATEGORY_ALIASES = {
    "audio": ["audio", "headphone", "headphones", "earbud", "earbuds", "music", "anc", "noise"],
    "computing": ["computing", "computer", "laptop", "developer", "monitor", "dock", "workstation", "coding"],
    "photography": ["photography", "camera", "content", "creator", "video", "vlog"],
    "wearables": ["wearables", "watch", "smartwatch", "fitness", "health", "gps"],
    "accessories": ["accessories", "charger", "charge", "usb", "gan", "adapter"],
    "networking": ["networking", "router", "wifi", "wi-fi", "mesh", "internet"],
    "home entertainment": ["home entertainment", "projector", "streaming", "movie", "cinema", "tv"],
    "tablets": ["tablets", "tablet", "note", "stylus", "study"],
    "gaming": ["gaming", "game", "games", "handheld", "console"],
    "smart home": ["smart home", "camera", "security", "purifier", "air", "home"],
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "for",
    "i",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "please",
    "show",
    "the",
    "to",
    "what",
    "which",
    "you",
}


def fetch_catalog_products():
    base_url = getattr(settings, "CATALOG_SERVICE_URL", "").rstrip("/")
    if not base_url:
        return FALLBACK_PRODUCTS, "fallback"

    try:
        with urlopen(f"{base_url}/api/products/", timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError):
        return FALLBACK_PRODUCTS, "fallback"

    products = payload.get("results", [])
    if not products:
        return FALLBACK_PRODUCTS, "fallback"
    return products, "catalog_service"


def answer_catalog_question(message):
    products, source = fetch_catalog_products()
    question = normalize(message)

    if is_greeting(question):
        return (
            "Hi! I am the Nexus Store assistant. You can ask me about product prices, stock, categories, "
            "or recommendations for laptops, audio, gaming, smart home, networking, cameras, and accessories.",
            source,
        )

    if asks_for_categories(question):
        categories = sorted({category_name(product) for product in products})
        return f"We currently sell these categories: {', '.join(categories)}.", source

    if asks_for_catalog_list(question):
        top_products = sorted(products, key=product_rating, reverse=True)[:8]
        lines = [format_product_line(product) for product in top_products]
        return "Here are some products available in the store:\n" + "\n".join(lines), source

    matched_product = best_product_match(question, products)
    if matched_product and product_name(matched_product).lower() in question:
        return describe_product(matched_product), source

    category = detect_category(question)
    if category:
        matches = filter_products_by_category_or_alias(products, category)
        if matches:
            matches = rank_products(matches, question)[:4]
            intro = f"For {category}, I recommend:\n"
            return intro + "\n".join(format_product_line(product) for product in matches), source

    if matched_product and asks_for_product_detail(question, matched_product):
        return describe_product(matched_product), source

    if asks_for_budget(question):
        matches = sorted(products, key=product_price)[:5]
        return "The most budget-friendly options are:\n" + "\n".join(format_product_line(product) for product in matches), source

    if asks_for_premium(question):
        matches = sorted(products, key=product_price, reverse=True)[:5]
        return "The premium/high-performance options are:\n" + "\n".join(format_product_line(product) for product in matches), source

    if asks_for_recommendation(question):
        matches = rank_products(products, question)[:5]
        return "Based on rating, stock, and relevance, I would suggest:\n" + "\n".join(
            format_product_line(product) for product in matches
        ), source

    if matched_product:
        return describe_product(matched_product), source

    return (
        "I can help with Nexus Store product questions. Try asking: "
        "'recommend a gaming device', 'price of DevStation X1', 'what audio products are in stock', "
        "or 'show cheap products'.",
        source,
    )


def normalize(value):
    return re.sub(r"\s+", " ", value.lower()).strip()


def is_greeting(question):
    return question in {"hi", "hello", "hey", "xin chao", "chao", "chao ban"}


def asks_for_categories(question):
    return any(term in question for term in ["category", "categories", "danh muc"])


def asks_for_catalog_list(question):
    terms = ["all products", "list products", "what products", "show products", "san pham nao", "tat ca san pham"]
    return any(term in question for term in terms)


def asks_for_budget(question):
    return any(term in question for term in ["cheap", "budget", "affordable", "lowest price", "gia re", "re nhat"])


def asks_for_premium(question):
    return any(term in question for term in ["premium", "expensive", "best", "highest price", "powerful", "cao cap"])


def asks_for_recommendation(question):
    terms = ["recommend", "suggest", "should i buy", "which one", "tu van", "goi y", "nen mua"]
    return any(term in question for term in terms)


def asks_for_product_detail(question, product):
    detail_terms = ["price", "stock", "feature", "detail", "rating", "review", "gia", "con hang", "tinh nang"]
    return product_name(product).lower() in question or any(term in question for term in detail_terms)


def detect_category(question):
    for category, aliases in CATEGORY_ALIASES.items():
        if any(alias in question for alias in aliases):
            return category
    return None


def filter_products_by_category_or_alias(products, category):
    aliases = CATEGORY_ALIASES.get(category, [category])
    exact_matches = [product for product in products if category == category_name(product).lower()]
    if exact_matches:
        return exact_matches

    matches = []
    for product in products:
        haystack = product_text(product)
        if category in category_name(product).lower() or any(alias in haystack for alias in aliases):
            matches.append(product)
    return matches


def best_product_match(question, products):
    best = None
    best_score = 0
    query_tokens = query_keywords(question)
    for product in products:
        name = product_name(product).lower()
        haystack = product_text(product)
        score = 0
        if name in question:
            score += 20
        for token in query_tokens:
            if token in name:
                score += 5
            elif token in haystack:
                score += 1
        if score > best_score:
            best = product
            best_score = score
    return best if best_score >= 3 else None


def query_keywords(question):
    return [token for token in re.findall(r"[a-z0-9]+", question) if len(token) > 2 and token not in STOPWORDS]


def rank_products(products, question):
    query_tokens = query_keywords(question)

    def score(product):
        haystack = product_text(product)
        relevance = sum(1 for token in query_tokens if token in haystack)
        return (relevance * 10) + float(product_rating(product)) + min(int(product.get("stock") or 0), 20) / 20

    return sorted(products, key=score, reverse=True)


def describe_product(product):
    features = product.get("features") or []
    feature_text = "; ".join(str(feature) for feature in features[:4])
    availability = "in stock" if int(product.get("stock") or 0) > 0 else "out of stock"
    original_price = product.get("original_price")
    original = f" (was ${format_price(original_price)})" if original_price else ""
    return (
        f"{product_name(product)} is a {category_name(product)} product priced at ${format_price(product.get('price'))}"
        f"{original}. It is currently {availability} with {product.get('stock', 0)} units available. "
        f"Rating: {product.get('rating', '0.0')}/5 from {product.get('reviews', 0)} reviews. "
        f"{product.get('short_desc') or product.get('description', '')} "
        f"Key features: {feature_text}."
    )


def format_product_line(product):
    return (
        f"- {product_name(product)} ({category_name(product)}): ${format_price(product.get('price'))}, "
        f"stock {product.get('stock', 0)}, rating {product.get('rating', '0.0')}/5"
    )


def product_text(product):
    features = " ".join(str(feature) for feature in product.get("features") or [])
    parts = [
        product_name(product),
        category_name(product),
        product.get("short_desc", ""),
        product.get("description", ""),
        features,
    ]
    return normalize(" ".join(parts))


def product_name(product):
    return product.get("name", "Unknown product")


def category_name(product):
    category = product.get("category") or {}
    if isinstance(category, dict):
        return category.get("name", "Uncategorized")
    return str(category or "Uncategorized")


def product_price(product):
    try:
        return Decimal(str(product.get("price", "0")))
    except (InvalidOperation, TypeError):
        return Decimal("0")


def product_rating(product):
    try:
        return Decimal(str(product.get("rating", "0")))
    except (InvalidOperation, TypeError):
        return Decimal("0")


def format_price(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError):
        return "0.00"
    return f"{amount:.2f}"
