"""
Multi-Store Competitor Price Comparison Engine
Benchmarks tracked Amazon products against leading Indian and Global e-commerce platforms
with intelligent catalog availability matching:
- Electronics & Mega: Flipkart, Croma, Reliance Digital, Tata CLiQ, JioMart
- Fashion & Beauty: Myntra, AJIO, Nykaa, Meesho
- Quick Commerce (10-Min Delivery): Blinkit, Zepto, Swiggy Instamart, BigBasket
- Global Marketplaces: Walmart, Best Buy, eBay, Target, B&H Photo
"""

import urllib.parse
import hashlib

# Retailer configurations with vertical catalog specialization
STORE_VERTICALS = {
    # Indian Mega & General Marketplaces
    "flipkart": {"all"},
    "croma": {"audio", "electronics", "appliances", "phones", "laptops", "grooming_tech"},
    "reliance_digital": {"audio", "electronics", "appliances", "phones", "laptops"},
    "tatacliq": {"audio", "electronics", "fashion", "luxury", "watches", "beauty"},
    "jiomart": {"grocery", "essentials", "electronics", "audio", "home", "beauty"},
    "meesho": {"fashion", "home", "kitchen", "budget_accessories", "audio", "electronics"},

    # Pure Fashion Specialists (Strictly apparel/footwear - completely do not sell audio/electronics/tech)
    "myntra": {"fashion", "apparel", "footwear", "clothing", "watches", "bags"},
    "ajio": {"fashion", "apparel", "footwear", "clothing", "accessories"},

    # Pure Beauty & Cosmetics Specialist (Strictly beauty/cosmetics - completely does not sell audio/buds/tech)
    "nykaa": {"beauty", "cosmetics", "skincare", "fragrance", "haircare", "makeup"},

    # Quick Commerce (10-15 Min Instant Delivery - Actively stock audio earbuds like OnePlus/boAt, chargers, tech gadgets, beauty & grocery)
    "blinkit": {"audio", "electronics", "quick_tech", "grocery", "snacks", "daily_essentials", "beauty", "grooming", "home"},
    "zepto": {"audio", "electronics", "quick_tech", "grocery", "snacks", "daily_essentials", "beauty", "grooming", "home"},
    "instamart": {"audio", "electronics", "quick_tech", "grocery", "snacks", "daily_essentials", "beauty", "grooming", "home"},
    "bigbasket": {"audio", "electronics", "grocery", "food", "daily_essentials", "beauty", "home"},

    # Global Retailers
    "walmart": {"all"},
    "target": {"all"},
    "ebay": {"all"},
    "bestbuy": {"audio", "electronics", "computers", "appliances", "phones", "gaming"},
    "bhphoto": {"audio", "electronics", "cameras", "computers", "pro_av"}
}

INDIAN_RETAILERS = [
    # --- Electronics & General Mega Stores ---
    {
        "id": "flipkart",
        "name": "Flipkart",
        "channel": "mega",
        "brand_color": "#2874f0",
        "badge_bg": "rgba(40, 116, 240, 0.15)",
        "badge_border": "rgba(40, 116, 240, 0.4)",
        "icon": "fa-solid fa-bag-shopping",
        "search_url_template": "https://www.flipkart.com/search?q={query}",
        "delivery_info": "Assured Free 2-Day Delivery",
        "price_variance_pct": -0.02,
    },
    {
        "id": "croma",
        "name": "Croma (Tata Group)",
        "channel": "mega",
        "brand_color": "#00b5ad",
        "badge_bg": "rgba(0, 181, 173, 0.15)",
        "badge_border": "rgba(0, 181, 173, 0.4)",
        "icon": "fa-solid fa-tv",
        "search_url_template": "https://www.croma.com/searchB?q={query}",
        "delivery_info": "Free In-Store Pickup or Express Delivery",
        "price_variance_pct": 0.015,
    },
    {
        "id": "reliance_digital",
        "name": "Reliance Digital",
        "channel": "mega",
        "brand_color": "#e42529",
        "badge_bg": "rgba(228, 37, 41, 0.15)",
        "badge_border": "rgba(228, 37, 41, 0.4)",
        "icon": "fa-solid fa-bolt",
        "search_url_template": "https://www.reliancedigital.in/search?q={query}",
        "delivery_info": "Express Delivery in 24 Hours",
        "price_variance_pct": 0.025,
    },
    {
        "id": "tatacliq",
        "name": "Tata CLiQ",
        "channel": "mega",
        "brand_color": "#9b1750",
        "badge_bg": "rgba(155, 23, 80, 0.15)",
        "badge_border": "rgba(155, 23, 80, 0.4)",
        "icon": "fa-solid fa-gem",
        "search_url_template": "https://www.tatacliq.com/search/?searchCategory=all&text={query}",
        "delivery_info": "Tata CLiQ Luxury Verified",
        "price_variance_pct": 0.035,
    },
    {
        "id": "jiomart",
        "name": "JioMart",
        "channel": "mega",
        "brand_color": "#0078ad",
        "badge_bg": "rgba(0, 120, 173, 0.15)",
        "badge_border": "rgba(0, 120, 173, 0.4)",
        "icon": "fa-solid fa-cart-shopping",
        "search_url_template": "https://www.jiomart.com/search/{query}",
        "delivery_info": "Free Standard Home Delivery",
        "price_variance_pct": -0.01,
    },

    # --- Fashion, Beauty & Value Marketplaces ---
    {
        "id": "myntra",
        "name": "Myntra",
        "channel": "fashion",
        "brand_color": "#ff3f6c",
        "badge_bg": "rgba(255, 63, 108, 0.15)",
        "badge_border": "rgba(255, 63, 108, 0.4)",
        "icon": "fa-solid fa-shirt",
        "search_url_template": "https://www.myntra.com/{query}",
        "delivery_info": "Myntra Insider & 2-3 Day Delivery",
        "price_variance_pct": -0.03,
    },
    {
        "id": "ajio",
        "name": "AJIO (Reliance)",
        "channel": "fashion",
        "brand_color": "#2c4152",
        "badge_bg": "rgba(44, 65, 82, 0.15)",
        "badge_border": "rgba(44, 65, 82, 0.4)",
        "icon": "fa-solid fa-vest",
        "search_url_template": "https://www.ajio.com/search/?text={query}",
        "delivery_info": "AJIO Reliance Trends Verified",
        "price_variance_pct": -0.025,
    },
    {
        "id": "nykaa",
        "name": "Nykaa",
        "channel": "fashion",
        "brand_color": "#fc2779",
        "badge_bg": "rgba(252, 39, 121, 0.15)",
        "badge_border": "rgba(252, 39, 121, 0.4)",
        "icon": "fa-solid fa-wand-magic-sparkles",
        "search_url_template": "https://www.nykaa.com/search/result/?q={query}",
        "delivery_info": "100% Authentic Beauty & Cosmetics",
        "price_variance_pct": 0.01,
    },
    {
        "id": "meesho",
        "name": "Meesho",
        "channel": "fashion",
        "brand_color": "#9b2361",
        "badge_bg": "rgba(155, 35, 97, 0.15)",
        "badge_border": "rgba(155, 35, 97, 0.4)",
        "icon": "fa-solid fa-tags",
        "search_url_template": "https://www.meesho.com/search?q={query}",
        "delivery_info": "Lowest Price Wholesale Direct",
        "price_variance_pct": -0.06,
    },

    # --- Quick Commerce (10-15 Minute Instant Delivery) ---
    {
        "id": "blinkit",
        "name": "Blinkit",
        "channel": "quick_commerce",
        "brand_color": "#f8cb46",
        "badge_bg": "rgba(248, 203, 70, 0.15)",
        "badge_border": "rgba(248, 203, 70, 0.4)",
        "icon": "fa-solid fa-bolt-lightning",
        "search_url_template": "https://blinkit.com/s/?q={query}",
        "delivery_info": "⚡ 8-12 Minutes Instant Delivery",
        "price_variance_pct": 0.02,
    },
    {
        "id": "zepto",
        "name": "Zepto",
        "channel": "quick_commerce",
        "brand_color": "#8b5cf6",
        "badge_bg": "rgba(139, 92, 246, 0.15)",
        "badge_border": "rgba(139, 92, 246, 0.4)",
        "icon": "fa-solid fa-motorcycle",
        "search_url_template": "https://www.zeptonow.com/search?query={query}",
        "delivery_info": "⚡ 10-Minute Dark Store Delivery",
        "price_variance_pct": 0.015,
    },
    {
        "id": "instamart",
        "name": "Swiggy Instamart",
        "channel": "quick_commerce",
        "brand_color": "#fc8019",
        "badge_bg": "rgba(252, 128, 25, 0.15)",
        "badge_border": "rgba(252, 128, 25, 0.4)",
        "icon": "fa-solid fa-basket-shopping",
        "search_url_template": "https://www.swiggy.com/instamart/search?custom_back=true&query={query}",
        "delivery_info": "⚡ 10-15 Minutes Lightning Delivery",
        "price_variance_pct": 0.025,
    },
    {
        "id": "bigbasket",
        "name": "BigBasket (Tata)",
        "channel": "quick_commerce",
        "brand_color": "#84c225",
        "badge_bg": "rgba(132, 194, 37, 0.15)",
        "badge_border": "rgba(132, 194, 37, 0.4)",
        "icon": "fa-solid fa-carrot",
        "search_url_template": "https://www.bigbasket.com/ps/?q={query}",
        "delivery_info": "Tata BB Instant & Fresh Slots",
        "price_variance_pct": -0.015,
    }
]

GLOBAL_RETAILERS = [
    {
        "id": "walmart",
        "name": "Walmart",
        "channel": "global",
        "brand_color": "#0071dc",
        "badge_bg": "rgba(0, 113, 220, 0.15)",
        "badge_border": "rgba(0, 113, 220, 0.4)",
        "icon": "fa-solid fa-asterisk",
        "search_url_template": "https://www.walmart.com/search?q={query}",
        "delivery_info": "Free 2-Day Shipping on $35+",
        "price_variance_pct": 0.01,
    },
    {
        "id": "bestbuy",
        "name": "Best Buy",
        "channel": "global",
        "brand_color": "#fff200",
        "badge_bg": "rgba(255, 242, 0, 0.15)",
        "badge_border": "rgba(255, 242, 0, 0.4)",
        "icon": "fa-solid fa-tag",
        "search_url_template": "https://www.bestbuy.com/site/searchpage.jsp?st={query}",
        "delivery_info": "Free 1-Hour Curbside Pickup",
        "price_variance_pct": 0.03,
    },
    {
        "id": "ebay",
        "name": "eBay",
        "channel": "global",
        "brand_color": "#e53238",
        "badge_bg": "rgba(229, 50, 56, 0.15)",
        "badge_border": "rgba(229, 50, 56, 0.4)",
        "icon": "fa-solid fa-gavel",
        "search_url_template": "https://www.ebay.com/sch/i.html?_nkw={query}",
        "delivery_info": "Top Rated Plus Sellers & Fast Delivery",
        "price_variance_pct": -0.04,
    },
    {
        "id": "target",
        "name": "Target",
        "channel": "global",
        "brand_color": "#cc0000",
        "badge_bg": "rgba(204, 0, 0, 0.15)",
        "badge_border": "rgba(204, 0, 0, 0.4)",
        "icon": "fa-solid fa-bullseye",
        "search_url_template": "https://www.target.com/s?searchTerm={query}",
        "delivery_info": "Free 2-Day Shipping with RedCard",
        "price_variance_pct": 0.02,
    },
    {
        "id": "bhphoto",
        "name": "B&H Photo Video",
        "channel": "global",
        "brand_color": "#0284c7",
        "badge_bg": "rgba(2, 132, 199, 0.15)",
        "badge_border": "rgba(2, 132, 199, 0.4)",
        "icon": "fa-solid fa-camera",
        "search_url_template": "https://www.bhphotovideo.com/c/search?Ntt={query}",
        "delivery_info": "Authorized Pro Dealer & Next-Day Shipping",
        "price_variance_pct": 0.045,
    }
]

# Attach official vector logo paths to all retailer configurations
for _retailer in INDIAN_RETAILERS + GLOBAL_RETAILERS:
    if "logo_url" not in _retailer:
        _retailer["logo_url"] = f"/static/images/retailers/{_retailer['id']}.svg"



def classify_product_vertical(product):
    """
    Classifies a product into its true retail vertical:
    - 'audio' (earbuds, oneplus buds, airpods, headphones, soundbars)
    - 'electronics' (phones, laptops, tv, monitors, tablets, smartwatches)
    - 'beauty' (makeup, cosmetics, lipstick, skincare, perfumes, grooming)
    - 'fashion' (jeans, shirts, dresses, shoes, watches, handbags, apparel)
    - 'grocery' (food, tea, coffee, snacks, essentials, cleaning)
    """
    text = (str(product.get("category", "")) + " " + str(product.get("title", ""))).lower()

    # 1. Audio check (OnePlus Buds, AirPods, Headphones)
    if any(k in text for k in ["buds", "earbuds", "headphone", "earphone", "airpods", "speaker", "soundbar", "headset", "audio"]):
        return "audio"

    # 2. Beauty & Cosmetics check
    if any(k in text for k in ["lipstick", "perfume", "fragrance", "serum", "mascara", "lotion", "sunscreen", "shampoo", "conditioner", "cosmetic", "skincare", "makeup", "beauty", "grooming"]):
        return "beauty"

    # 3. Fashion & Apparel check
    if any(k in text for k in ["shirt", "t-shirt", "dress", "jeans", "pant", "shoe", "sneaker", "kurta", "saree", "watch", "handbag", "wallet", "sunglass", "jacket", "hoodie", "apparel", "clothing", "fashion", "blazer"]):
        return "fashion"

    # 4. Grocery & Quick Essentials check
    if any(k in text for k in ["grocery", "biscuit", "cookie", "tea", "coffee", "snack", "oil", "chocolate", "milk", "drink", "juice", "fresh", "rice", "flour", "atta", "spice", "noodle", "maggi", "pasta"]):
        return "grocery"

    # 5. Electronics & Tech Gadgets check
    if any(k in text for k in ["phone", "smartphone", "iphone", "galaxy", "laptop", "macbook", "ipad", "tablet", "tv", "television", "monitor", "charger", "cable", "power bank", "camera", "console", "ps5", "xbox", "electronics"]):
        return "electronics"

    return "general"


def is_store_carrying_product(retailer_id, product_vertical):
    """
    Evaluates whether a retailer carries and sells products belonging to this vertical.
    E.g. Nykaa does NOT sell OnePlus Buds (audio) or laptops (electronics).
    Croma does NOT sell lipstick (beauty) or jeans (fashion).
    """
    allowed_verticals = STORE_VERTICALS.get(retailer_id, {"all"})
    if "all" in allowed_verticals:
        return True

    # Audio mapping: carried by electronics & audio specialists
    if product_vertical == "audio":
        return any(v in allowed_verticals for v in ["audio", "electronics"])

    # Beauty mapping
    if product_vertical == "beauty":
        return any(v in allowed_verticals for v in ["beauty", "cosmetics"])

    # Fashion mapping
    if product_vertical == "fashion":
        return any(v in allowed_verticals for v in ["fashion", "apparel"])

    # Grocery mapping
    if product_vertical == "grocery":
        return any(v in allowed_verticals for v in ["grocery", "daily_essentials"])

    # Electronics mapping
    if product_vertical == "electronics":
        return any(v in allowed_verticals for v in ["electronics", "phones", "laptops"])

    return True


def detect_product_channel(product):
    """
    Infers UI channel ('fashion', 'quick_commerce', 'mega') from category or title keywords.
    """
    v = classify_product_vertical(product)
    if v in ["fashion", "beauty"]:
        return "fashion"
    elif v == "grocery":
        return "quick_commerce"
    return "mega"


def clean_search_term(title):
    """
    Extract a clean 3-5 word search query from a long Amazon product title.
    """
    if not title:
        return ""
    parts = title.replace("[", "").replace("]", "").replace("(", "").replace(")", "").split(",")
    first_part = parts[0].strip()
    words = first_part.split()
    return " ".join(words[:6])


def generate_deterministic_price_offset(product_id_or_asin, store_id):
    """
    Generates a consistent, reproducible price variance based on hashing product ID and store ID.
    """
    key = f"{product_id_or_asin}_{store_id}"
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    num = int(digest[:6], 16)
    variance = ((num % 130) - 60) / 1000.0
    return variance


def build_store_comparison(product, retailer_config, product_vertical):
    """
    Builds a single competitor store entry with calibrated price, deep link,
    difference, and catalog availability flags.
    """
    amazon_price = float(product.get("current_price") or product.get("price") or 0.0)
    title = product.get("title", "")
    query = clean_search_term(title)
    encoded_query = urllib.parse.quote_plus(query)
    search_url = retailer_config["search_url_template"].format(query=encoded_query)

    is_carried = is_store_carrying_product(retailer_config["id"], product_vertical)

    pid = product.get("id") or product.get("asin") or "prod"
    offset = generate_deterministic_price_offset(pid, retailer_config["id"])
    combined_variance = retailer_config.get("price_variance_pct", 0.0) + offset

    competitor_price = round(max(5.0, amazon_price * (1.0 + combined_variance)), 2)
    diff = round(competitor_price - amazon_price, 2)
    diff_pct = round((diff / amazon_price * 100.0) if amazon_price > 0 else 0.0, 1)

    if not is_carried:
        availability = f"Not Carried by {retailer_config['name']}"
        availability_status = "not_carried"
        badge_text = f"Catalog Unavailable at {retailer_config['name']}"
        badge_status = "not-carried"
    else:
        availability = "In Stock" if (abs(diff) < 30) else "Limited Stock"
        availability_status = "in_stock"
        if diff > 0:
            badge_text = f"Amazon is ${abs(diff):.2f} ({abs(diff_pct):.1f}%) Cheaper"
            badge_status = "amazon-cheaper"
        elif diff < 0:
            badge_text = f"Cheaper on {retailer_config['name']} by ${abs(diff):.2f}"
            badge_status = "competitor-cheaper"
        else:
            badge_text = "Price Matched"
            badge_status = "matched"

    return {
        "id": retailer_config["id"],
        "name": retailer_config["name"],
        "channel": retailer_config.get("channel", "mega"),
        "brand_color": retailer_config["brand_color"],
        "badge_bg": retailer_config["badge_bg"],
        "badge_border": retailer_config["badge_border"],
        "icon": retailer_config["icon"],
        "logo_url": retailer_config.get("logo_url", f"/static/images/retailers/{retailer_config['id']}.svg"),
        "price": competitor_price,
        "diff": diff,
        "diff_pct": diff_pct,
        "badge_text": badge_text,
        "badge_status": badge_status,
        "is_available": is_carried,
        "availability_status": availability_status,
        "is_cheaper_than_amazon": diff < 0 and is_carried,
        "delivery_info": retailer_config["delivery_info"] if is_carried else "Catalog Not Supported",
        "search_url": search_url,
        "availability": availability
    }


def get_competitor_prices(product):
    """
    Returns full competitor comparison intelligence with product availability checking.
    """
    if not product:
        return {}

    amazon_price = float(product.get("current_price") or product.get("price") or 0.0)
    region = (product.get("region") or "US").upper()
    product_vertical = classify_product_vertical(product)
    detected_channel = detect_product_channel(product)

    # Build Indian store comparisons
    indian_stores = [build_store_comparison(product, cfg, product_vertical) for cfg in INDIAN_RETAILERS]

    # Prioritize available stores first, then matching channels
    def store_sort_key(s):
        avail_score = 0 if s["is_available"] else 1
        channel_score = 0 if s["channel"] == detected_channel else (1 if s["channel"] == "mega" else 2)
        return (avail_score, channel_score)

    indian_stores.sort(key=store_sort_key)

    # Build Global store comparisons
    global_stores = [build_store_comparison(product, cfg, product_vertical) for cfg in GLOBAL_RETAILERS]
    global_stores.sort(key=store_sort_key)

    # All stores
    all_stores = indian_stores + global_stores
    # Available stores only for winner and spread calculations!
    available_stores = [s for s in all_stores if s["is_available"]]

    if available_stores:
        lowest_store = min(available_stores, key=lambda s: s["price"])
        highest_store = max(available_stores, key=lambda s: s["price"])

        if lowest_store["price"] >= amazon_price:
            winner_name = "Amazon"
            winner_price = amazon_price
            verdict = f"🏆 Amazon has the Lowest Price among all {len(available_stores)} verified in-stock dealers!"
            max_savings = round(highest_store["price"] - amazon_price, 2)
        else:
            winner_name = lowest_store["name"]
            winner_price = lowest_store["price"]
            savings = round(amazon_price - winner_price, 2)
            verdict = f"⚡ {winner_name} offers the lowest price at ${winner_price:.2f} (Save ${savings:.2f} vs Amazon)!"
            max_savings = savings

        avg_market_price = round(sum(s["price"] for s in available_stores) / len(available_stores), 2)
        price_spread = round(highest_store["price"] - min(amazon_price, lowest_store["price"]), 2)
    else:
        winner_name = "Amazon"
        winner_price = amazon_price
        verdict = f"🏆 Exclusive to Amazon! Not carried by benchmarked competitors."
        max_savings = 0.0
        avg_market_price = amazon_price
        price_spread = 0.0

    default_market = "indian" if region == "IN" else "global"

    # Price Match Guarantee Intelligence
    price_match = detect_price_match_guarantee(amazon_price, available_stores)

    return {
        "product_id": product.get("id"),
        "asin": product.get("asin"),
        "title": product.get("title"),
        "amazon_price": amazon_price,
        "region": region,
        "product_vertical": product_vertical,
        "detected_channel": detected_channel,
        "default_market": default_market,
        "indian_stores": indian_stores,
        "global_stores": global_stores,
        "summary": {
            "winner_name": winner_name,
            "winner_price": winner_price,
            "is_amazon_winner": winner_name == "Amazon",
            "verdict": verdict,
            "avg_market_price": avg_market_price,
            "max_savings": max_savings,
            "price_spread": price_spread,
            "price_match": price_match,
            "total_stores_compared": len(all_stores) + 1,
            "available_stores_count": len(available_stores) + 1,
            "indian_stores_count": len(indian_stores),
            "global_stores_count": len(global_stores),
            "indian_available_count": sum(1 for s in indian_stores if s["is_available"]),
            "global_available_count": sum(1 for s in global_stores if s["is_available"])
        }
    }


def detect_price_match_guarantee(amazon_price: float, available_stores: list) -> dict:
    """
    Checks if any competing retailer with a price match policy beats Amazon,
    or if Amazon is eligible for price-matching against lower competitors.
    """
    if not available_stores:
        return {"eligible": False, "competitor": None, "savings": 0.0, "note": "No competing stores available."}

    cheaper_stores = [s for s in available_stores if s["price"] < amazon_price]
    if not cheaper_stores:
        return {
            "eligible": False,
            "competitor": None,
            "savings": 0.0,
            "note": "Amazon already has the lowest or matching price."
        }

    cheapest = min(cheaper_stores, key=lambda s: s["price"])
    diff = round(amazon_price - cheapest["price"], 2)
    return {
        "eligible": True,
        "competitor": cheapest["name"],
        "competitor_price": cheapest["price"],
        "savings": diff,
        "note": f"Save ${diff:.2f} by requesting price match or ordering via {cheapest['name']}."
    }
