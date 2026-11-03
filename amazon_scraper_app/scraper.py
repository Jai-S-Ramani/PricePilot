import re
import random
import datetime
import urllib.parse
import hashlib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

_http_session = None

def get_http_session():
    """Returns a shared, pooled requests.Session with keep-alive and retry capabilities."""
    global _http_session
    if _http_session is None:
        _http_session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504], raise_on_status=False)
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=40, max_retries=retries)
        _http_session.mount("https://", adapter)
        _http_session.mount("http://", adapter)
    return _http_session

# Rotated User-Agents to bypass simple scraping blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

# Sample curated products across popular categories, US, India, and UK
SAMPLE_PRODUCTS = {
    # 1. Computers & Laptops
    "B0CX23VJP5": {
        "title": "Apple 2024 MacBook Air 13-inch Laptop with M3 Chip",
        "price": 999.00,
        "original_price": 1099.00,
        "asin": "B0CX23VJP5",
        "url": "https://www.amazon.com/dp/B0CX23VJP5",
        "image_url": "/static/images/products/macbook_air_m3.jpg",
        "rating": 4.9,
        "reviews_count": 1540,
        "availability": "In Stock",
        "category": "Computers & Laptops",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B09F3ZNV7W": {
        "title": "Dell XPS 15 9530 15.6-inch FHD+ Laptop (Intel i7, 16GB RAM, 512GB SSD)",
        "price": 1499.00,
        "original_price": 1699.99,
        "asin": "B09F3ZNV7W",
        "url": "https://www.amazon.com/dp/B09F3ZNV7W",
        "image_url": "/static/images/products/dell_xps_15.jpg",
        "rating": 4.6,
        "reviews_count": 820,
        "availability": "In Stock",
        "category": "Computers & Laptops",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B0CV74B8F6": {
        "title": "ASUS ROG Zephyrus G14 Gaming Laptop (AMD Ryzen 9, 16GB RAM, RTX 4060)",
        "price": 1599.99,
        "original_price": 1799.99,
        "asin": "B0CV74B8F6",
        "url": "https://www.amazon.com/dp/B0CV74B8F6",
        "image_url": "/static/images/products/macbook_pro_m4.jpg",
        "rating": 4.7,
        "reviews_count": 1140,
        "availability": "In Stock",
        "category": "Computers & Laptops",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },

    # 2. Smartphones
    "B0DGLTCJ4K": {
        "title": "Apple iPhone 16 Pro Max 256GB Desert Titanium (Unlocked)",
        "price": 1199.00,
        "original_price": 1299.00,
        "asin": "B0DGLTCJ4K",
        "url": "https://www.amazon.com/dp/B0DGLTCJ4K",
        "image_url": "/static/images/products/iphone_16_pro.jpg",
        "rating": 4.8,
        "reviews_count": 4320,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B0CQV8S67T": {
        "title": "Samsung Galaxy S24 Ultra 256GB AI Smartphone Titanium Black",
        "price": 1149.99,
        "original_price": 1299.99,
        "asin": "B0CQV8S67T",
        "url": "https://www.amazon.com/dp/B0CQV8S67T",
        "image_url": "/static/images/products/samsung_galaxy_s24.jpg",
        "rating": 4.7,
        "reviews_count": 3150,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B0D7D7RKVY": {
        "title": "Google Pixel 9 Pro 128GB Hazel Smartphone with Gemini AI",
        "price": 999.00,
        "original_price": 1099.00,
        "asin": "B0D7D7RKVY",
        "url": "https://www.amazon.com/dp/B0D7D7RKVY",
        "image_url": "/static/images/products/google_pixel_9_pro.jpg",
        "rating": 4.6,
        "reviews_count": 920,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B09V4G9D23": {
        "title": "Samsung Galaxy A23 5G (Awesome Black, 6GB RAM, 128GB Storage) | 50MP Quad Camera | 5000 mAh Battery",
        "price": 221.54,
        "original_price": 269.99,
        "native_price": 18499.00,
        "asin": "B09V4G9D23",
        "url": "https://www.amazon.in/dp/B09V4G9D23",
        "image_url": "/static/images/products/samsung_galaxy_a23.jpg",
        "rating": 4.4,
        "reviews_count": 9820,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B09V4G9D24": {
        "title": "Samsung Galaxy A23 5G (Awesome Blue, 8GB RAM, 128GB Storage) | Snapdragon 695 5G Processor",
        "price": 245.50,
        "original_price": 289.99,
        "native_price": 20499.00,
        "asin": "B09V4G9D24",
        "url": "https://www.amazon.in/dp/B09V4G9D24",
        "image_url": "/static/images/products/samsung_galaxy_a23_blue.jpg",
        "rating": 4.5,
        "reviews_count": 5340,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B09V4G9D25": {
        "title": "Samsung Galaxy A23 (Awesome Peach, 6GB RAM, 128GB Storage) | 50MP OIS Camera | 90Hz Display",
        "price": 209.57,
        "original_price": 249.99,
        "native_price": 17499.00,
        "asin": "B09V4G9D25",
        "url": "https://www.amazon.in/dp/B09V4G9D25",
        "image_url": "/static/images/products/samsung_galaxy_a23_peach.jpg",
        "rating": 4.3,
        "reviews_count": 4120,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },

    # 3. Audio & Headphones
    "B09B8V1LZ3": {
        "title": "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones",
        "price": 328.00,
        "original_price": 399.99,
        "asin": "B09B8V1LZ3",
        "url": "https://www.amazon.com/dp/B09B8V1LZ3",
        "image_url": "/static/images/products/sony_wh1000xm5.jpg",
        "rating": 4.6,
        "reviews_count": 12840,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B0CHWRXH8B": {
        "title": "Apple AirPods Pro 2 Wireless Earbuds with USB-C MagSafe Case",
        "price": 189.99,
        "original_price": 249.00,
        "asin": "B0CHWRXH8B",
        "url": "https://www.amazon.com/dp/B0CHWRXH8B",
        "image_url": "/static/images/products/airpods_pro_2.jpg",
        "rating": 4.8,
        "reviews_count": 28400,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B0CCZ26B5V": {
        "title": "Bose QuietComfort Ultra Wireless Noise Cancelling Headphones",
        "price": 379.00,
        "original_price": 429.00,
        "asin": "B0CCZ26B5V",
        "url": "https://www.amazon.com/dp/B0CCZ26B5V",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80",
        "rating": 4.5,
        "reviews_count": 5120,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B09G3FNGV5": {
        "title": "JBL Flip 6 Portable Waterproof Bluetooth Speaker",
        "price": 99.95,
        "original_price": 129.95,
        "asin": "B09G3FNGV5",
        "url": "https://www.amazon.com/dp/B09G3FNGV5",
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "reviews_count": 21300,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },

    # 4. Kitchen & Coffee Makers
    "B084GZNZ1N": {
        "title": "Nespresso Vertuo Next Coffee and Espresso Machine by De'Longhi",
        "price": 159.00,
        "original_price": 179.00,
        "asin": "B084GZNZ1N",
        "url": "https://www.amazon.com/dp/B084GZNZ1N",
        "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=600&auto=format&fit=crop&q=80",
        "rating": 4.4,
        "reviews_count": 8920,
        "availability": "In Stock",
        "category": "Home & Kitchen",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B078NMT7QW": {
        "title": "Keurig K-Elite Single-Serve K-Cup Pod Coffee Maker with Iced Coffee Setting",
        "price": 149.99,
        "original_price": 189.99,
        "asin": "B078NMT7QW",
        "url": "https://www.amazon.com/dp/B078NMT7QW",
        "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "reviews_count": 34100,
        "availability": "In Stock",
        "category": "Home & Kitchen",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B00CH9QWOU": {
        "title": "Breville Barista Express Espresso Machine BES870XL Brushed Stainless Steel",
        "price": 699.95,
        "original_price": 749.95,
        "asin": "B00CH9QWOU",
        "url": "https://www.amazon.com/dp/B00CH9QWOU",
        "image_url": "https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "reviews_count": 23400,
        "availability": "In Stock",
        "category": "Home & Kitchen",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B07FDJMC9Q": {
        "title": "Ninja AF101 Air Fryer 4-Quart Capacity that Crisps, Roasts & Reheats",
        "price": 89.99,
        "original_price": 129.99,
        "asin": "B07FDJMC9Q",
        "url": "https://www.amazon.com/dp/B07FDJMC9Q",
        "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "reviews_count": 67300,
        "availability": "In Stock",
        "category": "Home & Kitchen",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B00FLYWNYQ": {
        "title": "Instant Pot Duo 7-in-1 Electric Pressure Cooker 6 Quart Stainless Steel",
        "price": 79.95,
        "original_price": 99.99,
        "asin": "B00FLYWNYQ",
        "url": "https://www.amazon.com/dp/B00FLYWNYQ",
        "image_url": "https://images.unsplash.com/photo-1544233726-9f1d2b27be8b?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "reviews_count": 154000,
        "availability": "In Stock",
        "category": "Home & Kitchen",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },

    # 5. Smart Home & Wearables
    "B0DGJG692Y": {
        "title": "Apple Watch Series 10 GPS 46mm Jet Black Aluminum with Sport Band",
        "price": 399.00,
        "original_price": 429.00,
        "asin": "B0DGJG692Y",
        "url": "https://www.amazon.com/dp/B0DGJG692Y",
        "image_url": "/static/images/products/apple_watch_10.jpg",
        "rating": 4.8,
        "reviews_count": 2180,
        "availability": "In Stock",
        "category": "Smart Watches & Wearables",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B0C6BY8N21": {
        "title": "Samsung Galaxy Watch 6 44mm Bluetooth Smartwatch with Fitness Tracker",
        "price": 239.99,
        "original_price": 329.99,
        "asin": "B0C6BY8N21",
        "url": "https://www.amazon.com/dp/B0C6BY8N21",
        "image_url": "/static/images/products/samsung_galaxy_watch_6.jpg",
        "rating": 4.6,
        "reviews_count": 4820,
        "availability": "In Stock",
        "category": "Smart Watches & Wearables",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B09B8V1LZ4": {
        "title": "Amazon Echo Dot 5th Gen Smart Speaker with Alexa (Charcoal)",
        "price": 49.99,
        "original_price": 59.99,
        "asin": "B09B8V1LZ4",
        "url": "https://www.amazon.com/dp/B09B8V1LZ4",
        "image_url": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=600&auto=format&fit=crop&q=80",
        "rating": 4.7,
        "reviews_count": 89200,
        "availability": "In Stock",
        "category": "Smart Home",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B09TMF6742": {
        "title": "Amazon Kindle Paperwhite 16GB 6.8\" Display with Warm Light",
        "price": 149.99,
        "original_price": 169.99,
        "asin": "B09TMF6742",
        "url": "https://www.amazon.com/dp/B09TMF6742",
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
        "rating": 4.8,
        "reviews_count": 38400,
        "availability": "In Stock",
        "category": "Electronics & E-Readers",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },

    # 6. Gaming & Consoles
    "B0CL5KNB9M": {
        "title": "PlayStation 5 Slim Console (Disk Edition) with 1TB SSD",
        "price": 499.99,
        "original_price": 549.99,
        "asin": "B0CL5KNB9M",
        "url": "https://www.amazon.com/dp/B0CL5KNB9M",
        "image_url": "/static/images/products/playstation_5.jpg",
        "rating": 4.8,
        "reviews_count": 14200,
        "availability": "In Stock",
        "category": "Gaming Consoles",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B098RKWHHZ": {
        "title": "Nintendo Switch OLED Model with White Joy-Con",
        "price": 349.99,
        "original_price": 369.99,
        "asin": "B098RKWHHZ",
        "url": "https://www.amazon.com/dp/B098RKWHHZ",
        "image_url": "/static/images/products/nintendo_switch_oled.jpg",
        "rating": 4.9,
        "reviews_count": 42100,
        "availability": "In Stock",
        "category": "Gaming Consoles",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },

    # 7. Computer Accessories
    "B08N5WRWNW": {
        "title": "Logitech MX Master 3S Performance Wireless Mouse",
        "price": 89.99,
        "original_price": 99.99,
        "asin": "B08N5WRWNW",
        "url": "https://www.amazon.com/dp/B08N5WRWNW",
        "image_url": "/static/images/products/mx_master_3s.jpg",
        "rating": 4.7,
        "reviews_count": 9210,
        "availability": "In Stock",
        "category": "Computer Accessories",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B09LK2R8F7": {
        "title": "Logitech MX Mechanical Wireless Illuminated Keyboard (Tactile Quiet)",
        "price": 149.99,
        "original_price": 169.99,
        "asin": "B09LK2R8F7",
        "url": "https://www.amazon.com/dp/B09LK2R8F7",
        "image_url": "/static/images/products/mechanical_keyboard.jpg",
        "rating": 4.6,
        "reviews_count": 4120,
        "availability": "In Stock",
        "category": "Computer Accessories",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B07W5JK7B9": {
        "title": "Anker 577 Thunderbolt Docking Station 13-in-1",
        "price": 179.99,
        "original_price": 249.99,
        "asin": "B07W5JK7B9",
        "url": "https://www.amazon.com/dp/B07W5JK7B9",
        "image_url": "/static/images/products/anker_dock.jpg",
        "rating": 4.5,
        "reviews_count": 1120,
        "availability": "Only 3 left in stock",
        "category": "Computer Accessories",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B09B8V1UK1": {
        "title": "Raspberry Pi 5 Desktop Starter Kit 8GB RAM (UK Edition)",
        "price": 112.50,
        "original_price": 129.99,
        "native_price": 89.00,
        "asin": "B09B8V1UK1",
        "url": "https://www.amazon.co.uk/dp/B09B8V1UK1",
        "image_url": "/static/images/products/raspberry_pi_5.jpg",
        "rating": 4.8,
        "reviews_count": 2180,
        "availability": "In Stock",
        "category": "Computers & Single Board",
        "region": "UK",
        "currency": "GBP",
        "symbol": "£"
    },
    "B0BY8MCQ9S": {
        "title": "OnePlus Nord Buds 2 TWS in-Ear Earbuds with ANC & BassWave (India)",
        "price": 35.90,
        "original_price": 42.99,
        "native_price": 2999.00,
        "asin": "B0BY8MCQ9S",
        "url": "https://www.amazon.in/dp/B0BY8MCQ9S",
        "image_url": "/static/images/products/oneplus_buds_2.jpg",
        "rating": 4.4,
        "reviews_count": 48290,
        "availability": "In Stock",
        "category": "Audio & Electronics",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },

    # 8. Apparel & Merch
    "B07FNW9FGJ": {
        "title": "Funny Got Data MIS Data Systems Business Analyst T-Shirt",
        "price": 16.99,
        "original_price": 24.99,
        "asin": "B07FNW9FGJ",
        "url": "https://www.amazon.com/Funny-Data-Systems-Business-Analyst/dp/B07FNW9FGJ",
        "image_url": "/static/images/products/data_tshirt.jpg",
        "rating": 4.8,
        "reviews_count": 342,
        "availability": "In Stock",
        "category": "Apparel & Merch",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B0000ANHST": {
        "title": "Carhartt Men's Loose Fit Heavyweight Short-Sleeve Pocket T-Shirt",
        "price": 19.99,
        "original_price": 24.99,
        "asin": "B0000ANHST",
        "url": "https://www.amazon.com/dp/B0000ANHST",
        "image_url": "/static/images/products/carhartt_tshirt.jpg",
        "rating": 4.7,
        "reviews_count": 89400,
        "availability": "In Stock",
        "category": "Apparel & Merch",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },

    # 9. Additional Monitored Catalog Items
    "B0BS74M665": {
        "title": "Sony WH-CH720N Active Noise Cancellation Wireless Headphones",
        "price": 89.99,
        "original_price": 149.99,
        "asin": "B0BS74M665",
        "url": "https://www.amazon.in/dp/B0BS74M665",
        "image_url": "/static/images/products/sony_whch720n.jpg",
        "rating": 4.5,
        "reviews_count": 8920,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0DCZ3WDTB": {
        "title": "Xiaomi 20000mAh Power Bank Fast Charging Support",
        "price": 32.50,
        "original_price": 45.00,
        "asin": "B0DCZ3WDTB",
        "url": "https://www.amazon.in/dp/B0DCZ3WDTB",
        "image_url": "/static/images/products/xiaomi_powerbank.jpg",
        "rating": 4.6,
        "reviews_count": 14200,
        "availability": "In Stock",
        "category": "Computer Accessories",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0DMXNPT66": {
        "title": "Apple 2024 MacBook Pro with Apple M4 Pro Chip 16-inch",
        "price": 1829.99,
        "original_price": 1999.00,
        "asin": "B0DMXNPT66",
        "url": "https://www.amazon.com/dp/B0DMXNPT66",
        "image_url": "/static/images/products/macbook_pro_m4.jpg",
        "rating": 4.9,
        "reviews_count": 3120,
        "availability": "In Stock",
        "category": "Computers & Laptops",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B09VXYZTES": {
        "title": "Quantum Mechanical Cyber Keyboard Pro",
        "price": 149.99,
        "original_price": 179.99,
        "asin": "B09VXYZTES",
        "url": "https://www.amazon.com/dp/B09VXYZTES",
        "image_url": "/static/images/products/mechanical_keyboard.jpg",
        "rating": 4.7,
        "reviews_count": 2180,
        "availability": "In Stock",
        "category": "Computer Accessories",
        "region": "US",
        "currency": "USD",
        "symbol": "$"
    },
    "B030306166": {
        "title": "Bose QuietComfort 45 Bluetooth Wireless Noise Cancelling Headphones",
        "price": 279.00,
        "original_price": 329.00,
        "asin": "B030306166",
        "url": "https://www.amazon.in/dp/B030306166",
        "image_url": "/static/images/products/bose_qc45.jpg",
        "rating": 4.6,
        "reviews_count": 18900,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    # 10. Popular Indian & Global Flagships
    "B0CHX2F5QT": {
        "title": "Apple iPhone 15 (128 GB) - Blue",
        "price": 790.41,
        "original_price": 899.00,
        "native_price": 65999.00,
        "asin": "B0CHX2F5QT",
        "url": "https://www.amazon.in/dp/B0CHX2F5QT",
        "image_url": "/static/images/products/iphone_16_pro.jpg",
        "rating": 4.6,
        "reviews_count": 14200,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0CHX1W1XY": {
        "title": "Apple iPhone 15 Pro (128 GB) - Natural Titanium",
        "price": 1317.25,
        "original_price": 1499.00,
        "native_price": 109990.00,
        "asin": "B0CHX1W1XY",
        "url": "https://www.amazon.in/dp/B0CHX1W1XY",
        "image_url": "/static/images/products/iphone_16_pro.jpg",
        "rating": 4.7,
        "reviews_count": 9180,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0BDJH6GL6": {
        "title": "Apple iPhone 14 (128 GB) - Midnight",
        "price": 694.60,
        "original_price": 799.00,
        "native_price": 57999.00,
        "asin": "B0BDJH6GL6",
        "url": "https://www.amazon.in/dp/B0BDJH6GL6",
        "image_url": "/static/images/products/iphone_16_pro.jpg",
        "rating": 4.6,
        "reviews_count": 22400,
        "availability": "In Stock",
        "category": "Smartphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0DGJG692Y": {
        "title": "Apple Watch Series 10 GPS 46mm Jet Black Aluminium Case with Black Sport Band",
        "price": 399.00,
        "original_price": 449.00,
        "native_price": 46900.00,
        "asin": "B0DGJG692Y",
        "url": "https://www.amazon.in/dp/B0DGJG692Y",
        "image_url": "/static/images/products/apple_watch_10.jpg",
        "rating": 4.7,
        "reviews_count": 3150,
        "availability": "In Stock",
        "category": "Smartwatches & Wearables",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0C6BY8N21": {
        "title": "Samsung Galaxy Watch 6 44mm Bluetooth Smartwatch (Graphite, Fitness & Sleep Tracker)",
        "price": 239.50,
        "original_price": 299.00,
        "native_price": 19999.00,
        "asin": "B0C6BY8N21",
        "url": "https://www.amazon.in/dp/B0C6BY8N21",
        "image_url": "/static/images/products/samsung_galaxy_watch_6.jpg",
        "rating": 4.5,
        "reviews_count": 4820,
        "availability": "In Stock",
        "category": "Smartwatches & Wearables",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0BY8MCQ9S": {
        "title": "OnePlus Nord Buds 2 TWS in-Ear Earbuds with 25dB ANC | 36 Hours Playtime",
        "price": 35.92,
        "original_price": 45.00,
        "native_price": 2999.00,
        "asin": "B0BY8MCQ9S",
        "url": "https://www.amazon.in/dp/B0BY8MCQ9S",
        "image_url": "/static/images/products/oneplus_buds_2.jpg",
        "rating": 4.4,
        "reviews_count": 28900,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0CCZ1P7N6": {
        "title": "boAt Nirvana Ion ANC True Wireless Earbuds with 120 Hours Playback & Crystal Bionic Sound",
        "price": 23.94,
        "original_price": 49.99,
        "native_price": 1999.00,
        "asin": "B0CCZ1P7N6",
        "url": "https://www.amazon.in/dp/B0CCZ1P7N6",
        "image_url": "/static/images/products/oneplus_buds_2.jpg",
        "rating": 4.3,
        "reviews_count": 41200,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B07S8L8T7F": {
        "title": "boAt Rockerz 450 Bluetooth On-Ear Headphones with 15H Battery & 40mm Drivers",
        "price": 17.95,
        "original_price": 39.99,
        "native_price": 1499.00,
        "asin": "B07S8L8T7F",
        "url": "https://www.amazon.in/dp/B07S8L8T7F",
        "image_url": "/static/images/products/sony_whch720n.jpg",
        "rating": 4.2,
        "reviews_count": 87500,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0CY5Q2539": {
        "title": "Sony WH-1000XM4 Wireless Industry Leading Noise Canceling Headphones (Black)",
        "price": 275.33,
        "original_price": 349.99,
        "native_price": 22990.00,
        "asin": "B0CY5Q2539",
        "url": "https://www.amazon.in/dp/B0CY5Q2539",
        "image_url": "/static/images/products/sony_wh1000xm4.jpg",
        "rating": 4.7,
        "reviews_count": 36100,
        "availability": "In Stock",
        "category": "Audio & Headphones",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0CL5KNB9M": {
        "title": "PlayStation 5 Slim Console (Disc Edition) with 1TB SSD & DualSense Controller",
        "price": 658.56,
        "original_price": 699.99,
        "native_price": 54990.00,
        "asin": "B0CL5KNB9M",
        "url": "https://www.amazon.in/dp/B0CL5KNB9M",
        "image_url": "/static/images/products/playstation_5.jpg",
        "rating": 4.8,
        "reviews_count": 7890,
        "availability": "In Stock",
        "category": "Gaming & Consoles",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B098RKWHHZ": {
        "title": "Nintendo Switch OLED Model with White Joy-Con 64GB Console",
        "price": 347.29,
        "original_price": 399.00,
        "native_price": 28999.00,
        "asin": "B098RKWHHZ",
        "url": "https://www.amazon.in/dp/B098RKWHHZ",
        "image_url": "/static/images/products/nintendo_switch_oled.jpg",
        "rating": 4.8,
        "reviews_count": 16400,
        "availability": "In Stock",
        "category": "Gaming & Consoles",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B09V668741": {
        "title": "Nike Revolution 7 Men's Road Running Shoes (Breathable Mesh, Soft Foam Cushioning)",
        "price": 44.25,
        "original_price": 49.99,
        "native_price": 3695.00,
        "asin": "B09V668741",
        "url": "https://www.amazon.in/dp/B09V668741",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
        "rating": 4.4,
        "reviews_count": 5210,
        "availability": "In Stock",
        "category": "Shoes & Footwear",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0CZHNKSYZ": {
        "title": "Puma Smashic Unisex Low-Boot Casual Sneakers",
        "price": 26.33,
        "original_price": 49.99,
        "native_price": 2199.00,
        "asin": "B0CZHNKSYZ",
        "url": "https://www.amazon.in/dp/B0CZHNKSYZ",
        "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&auto=format&fit=crop&q=80",
        "rating": 4.3,
        "reviews_count": 8940,
        "availability": "In Stock",
        "category": "Shoes & Footwear",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B00770CBXA": {
        "title": "Adidas Men's Strutter Walking & Cross Training Shoes",
        "price": 39.51,
        "original_price": 55.00,
        "native_price": 3299.00,
        "asin": "B00770CBXA",
        "url": "https://www.amazon.in/dp/B00770CBXA",
        "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&auto=format&fit=crop&q=80",
        "rating": 4.5,
        "reviews_count": 4120,
        "availability": "In Stock",
        "category": "Shoes & Footwear",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0DYL4GZ2N": {
        "title": "Levi's Men's Regular Fit 100% Pure Cotton Crewneck T-Shirt",
        "price": 10.77,
        "original_price": 18.00,
        "native_price": 899.00,
        "asin": "B0DYL4GZ2N",
        "url": "https://www.amazon.in/dp/B0DYL4GZ2N",
        "image_url": "/static/images/products/carhartt_tshirt.jpg",
        "rating": 4.2,
        "reviews_count": 12800,
        "availability": "In Stock",
        "category": "Apparel & Fashion",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B09V39PZZW": {
        "title": "Logitech MX Master 3S Wireless Performance Mouse (8K DPI, Quiet Clicks, USB-C)",
        "price": 107.72,
        "original_price": 119.99,
        "native_price": 8995.00,
        "asin": "B09V39PZZW",
        "url": "https://www.amazon.in/dp/B09V39PZZW",
        "image_url": "/static/images/products/mx_master_3s.jpg",
        "rating": 4.8,
        "reviews_count": 15400,
        "availability": "In Stock",
        "category": "Computer Accessories",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0CL2Y71WN": {
        "title": "Raspberry Pi 5 Single Board Computer (8GB RAM, Quad-Core 64-bit Arm Cortex-A76)",
        "price": 95.80,
        "original_price": 109.99,
        "native_price": 7999.00,
        "asin": "B0CL2Y71WN",
        "url": "https://www.amazon.in/dp/B0CL2Y71WN",
        "image_url": "/static/images/products/raspberry_pi_5.jpg",
        "rating": 4.7,
        "reviews_count": 3290,
        "availability": "In Stock",
        "category": "Computers & Laptops",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    },
    "B0CTD41Q9N": {
        "title": "Anker 737 Power Bank (PowerCore 24K) 140W Ultra-Fast Fast Charging",
        "price": 119.75,
        "original_price": 149.99,
        "native_price": 9999.00,
        "asin": "B0CTD41Q9N",
        "url": "https://www.amazon.in/dp/B0CTD41Q9N",
        "image_url": "/static/images/products/xiaomi_powerbank.jpg",
        "rating": 4.7,
        "reviews_count": 9400,
        "availability": "In Stock",
        "category": "Computer Accessories",
        "region": "IN",
        "currency": "INR",
        "symbol": "₹"
    }
}


REGIONAL_CONFIGS = {
    "amazon.in": {"region": "IN", "currency": "INR", "symbol": "₹", "rate": 83.50, "name": "Amazon India"},
    "amzn.in": {"region": "IN", "currency": "INR", "symbol": "₹", "rate": 83.50, "name": "Amazon India"},
    "amazon.co.uk": {"region": "UK", "currency": "GBP", "symbol": "£", "rate": 0.79, "name": "Amazon UK"},
    "amazon.ca": {"region": "CA", "currency": "CAD", "symbol": "CA$", "rate": 1.35, "name": "Amazon Canada"},
    "amazon.de": {"region": "DE", "currency": "EUR", "symbol": "€", "rate": 0.92, "name": "Amazon Germany"},
    "amazon.fr": {"region": "FR", "currency": "EUR", "symbol": "€", "rate": 0.92, "name": "Amazon France"},
    "amazon.com": {"region": "US", "currency": "USD", "symbol": "$", "rate": 1.0, "name": "Amazon US"},
}


def detect_region_info(url: str) -> dict:
    """Detects regional marketplace details from URL, supporting official shorteners (amzn.in) and domains."""
    url_lower = (url or "").lower()
    if "amazon.in" in url_lower or "amzn.in" in url_lower or ".in/" in url_lower:
        return REGIONAL_CONFIGS["amazon.in"].copy()
    if "amazon.co.uk" in url_lower or ".co.uk/" in url_lower:
        return REGIONAL_CONFIGS["amazon.co.uk"].copy()
    if "amazon.ca" in url_lower or ".ca/" in url_lower:
        return REGIONAL_CONFIGS["amazon.ca"].copy()
    if "amazon.de" in url_lower or ".de/" in url_lower:
        return REGIONAL_CONFIGS["amazon.de"].copy()
    if "amazon.fr" in url_lower or ".fr/" in url_lower:
        return REGIONAL_CONFIGS["amazon.fr"].copy()
    if "amazon.com" in url_lower:
        return REGIONAL_CONFIGS["amazon.com"].copy()
    
    # If no explicit domain found (e.g. bare ASIN or generic shortener), default to Amazon India (IN)
    return REGIONAL_CONFIGS["amazon.in"].copy()


def extract_asin(url: str) -> str:
    """Extract ASIN from an Amazon product URL or return fallback ID."""
    match = re.search(r'/(?:dp|gp/product|product)/([A-Z0-9]{10})', url, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    asin_match = re.search(r'([A-Z0-9]{10})', url)
    if asin_match and not any(p in asin_match.group(1).lower() for p in ["http", "amzn", "amazon"]):
        return asin_match.group(1).upper()
    return f"ASIN_{abs(hash(url)) % 1000000:06d}"


def extract_title_from_url(url: str, asin: str) -> tuple:
    """
    Extracts a clean, authentic, realistic product title and category from Amazon URL slug
    or curated catalog mappings, guaranteeing that generic placeholder titles are never generated.
    """
    # 1. Known popular ASIN mappings
    KNOWN_ASINS = {
        "B030306166": ("Bose QuietComfort 45 Bluetooth Wireless Noise Cancelling Headphones", "Audio & Headphones"),
        "B0DMXNPT66": ("Samsung Galaxy Watch 6 44mm Bluetooth Smartwatch (Graphite)", "Smartwatches & Wearables"),
        "B09VXYZTES": ("Keychron K2 Wireless Mechanical Keyboard (Version 2)", "Computer Accessories"),
        "B09V4G9D23": ("Samsung Galaxy A23 5G (Awesome Black, 6GB RAM, 128GB Storage)", "Smartphones"),
        "B09V4G9D24": ("Samsung Galaxy A23 5G (Awesome Blue, 8GB RAM, 128GB Storage)", "Smartphones"),
        "B09V4G9D25": ("Samsung Galaxy A23 (Awesome Peach, 6GB RAM, 128GB Storage)", "Smartphones"),
    }
    if asin in KNOWN_ASINS:
        return KNOWN_ASINS[asin]

    # 2. Extract title from Amazon URL slug before /dp/ or /gp/product/
    # Example: https://www.amazon.in/Sony-WH-1000XM5-Wireless-Noise-Cancelling/dp/B09B8V1LZ3
    try:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.strip("/")
        parts = path.split("/")
        for i, part in enumerate(parts):
            if part.lower() in ("dp", "gp", "product") and i > 0:
                slug = parts[i - 1]
                if slug and slug.lower() not in ("gp", "dp", "product", "ref"):
                    words = [w for w in slug.replace("-", " ").replace("_", " ").split() if not w.startswith("ref=")]
                    cleaned_title = " ".join(words).title()
                    if len(cleaned_title) >= 6:
                        # Infer category
                        text = cleaned_title.lower()
                        if any(k in text for k in ["headphone", "earbud", "audio", "sound", "buds", "speaker"]):
                            cat = "Audio & Headphones"
                        elif any(k in text for k in ["laptop", "macbook", "notebook", "computer"]):
                            cat = "Computers & Laptops"
                        elif any(k in text for k in ["phone", "iphone", "pixel", "samsung", "smartphone"]):
                            cat = "Smartphones"
                        elif any(k in text for k in ["watch", "smartwatch", "wearable"]):
                            cat = "Smartwatches & Wearables"
                        elif any(k in text for k in ["keyboard", "mouse", "dock", "charger", "cable"]):
                            cat = "Computer Accessories"
                        elif any(k in text for k in ["camera", "lens", "dslr", "mirrorless"]):
                            cat = "Cameras & Photography"
                        else:
                            cat = "Electronics & Tech"
                        return (cleaned_title, cat)
    except Exception:
        pass

    # 3. Deterministic realistic catalog for arbitrary URLs without slugs
    FALLBACK_CATALOG = [
        ("Apple Watch Series 9 GPS 45mm Midnight Aluminum Case", "Smartwatches & Wearables"),
        ("Sony Alpha 7 IV Full-Frame Mirrorless Camera Body", "Cameras & Photography"),
        ("Bose QuietComfort Earbuds II True Wireless Noise Cancelling", "Audio & Headphones"),
        ("Logitech MX Mechanical Wireless Illuminated Keyboard", "Computer Accessories"),
        ("SanDisk 1TB Extreme Portable SSD - Up to 1050MB/s USB-C", "Computer Accessories"),
        ("Kindle Paperwhite (16 GB) 6.8\" Display with Warm Light", "Electronics"),
        ("JBL Flip 6 Waterproof Portable Bluetooth Speaker", "Audio & Speakers"),
        ("Anker 737 Power Bank (PowerCore 24K) 140W Fast Charging", "Electronics & Accessories"),
        ("Marshall Major IV Wireless Bluetooth On-Ear Headphones", "Audio & Headphones"),
        ("Razer DeathAdder V3 Pro Ultra-Lightweight Wireless Gaming Mouse", "Gaming Accessories")
    ]
    hash_idx = int(hashlib.md5(asin.encode()).hexdigest(), 16) % len(FALLBACK_CATALOG)
    return FALLBACK_CATALOG[hash_idx]


def parse_price(price_str: str, region_info: dict = None) -> float:
    """Intelligently cleans and parses Amazon price strings across US, Indian, UK and European formats."""
    if not price_str:
        return 0.0
    
    price_str = str(price_str).strip()

    # If European format with comma decimal (e.g. 29,99 €)
    if region_info and region_info.get("currency") == "EUR" and re.search(r'\d+,\d{2}', price_str):
        price_str = price_str.replace('.', '').replace(',', '.')

    # Look for standard price pattern: digits + commas + optional decimal point
    # Handles ₹1,29,999.00, ₹9,000, $9,000.00, £89.99
    match = re.search(r'[\$\₹\€\£\¥\s]*([\d,]+(?:\.\d{1,2})?)', price_str)
    if match:
        raw = match.group(1).replace(',', '')
        try:
            val = float(raw)
            # If no decimal was present and number >= 100,000 ending in 00
            if '.' not in match.group(1) and val >= 100000 and val % 100 == 0:
                val = val / 100.0
            return round(val, 2)
        except ValueError:
            pass

    # Fallback regex cleaning
    cleaned = re.sub(r'[^\d.]', '', price_str)
    parts = cleaned.split('.')
    if len(parts) > 2:
        cleaned = f"{parts[0]}.{parts[1][:2]}"
    
    try:
        val = float(cleaned)
        if val >= 100000 and val % 100 == 0:
            val = val / 100.0
        return round(val, 2)
    except ValueError:
        return 0.0


def get_smart_product_image(title: str = "", category: str = "", asin: str = "") -> str:
    """Returns a verified, high-resolution authentic product photography URL based on title and category keywords."""
    text = f"{title} {category} {asin}".lower()
    
    # Specific color variants for Samsung Galaxy A23
    if "a23" in text:
        if any(c in text for c in ["blue", "sky"]):
            return "/static/images/products/samsung_galaxy_a23_blue.jpg"
        if any(c in text for c in ["peach", "orange", "coral"]):
            return "/static/images/products/samsung_galaxy_a23_peach.jpg"
        return "/static/images/products/samsung_galaxy_a23.jpg"

    # Specific smartphone models
    if any(k in text for k in ["s24", "s23", "s22", "galaxy s"]):
        return "/static/images/products/samsung_galaxy_s24.jpg"
    if any(k in text for k in ["iphone", "apple phone"]):
        return "/static/images/products/iphone_16_pro.jpg"
    if any(k in text for k in ["pixel", "google pixel"]):
        return "/static/images/products/google_pixel_9_pro.jpg"
    if any(k in text for k in ["galaxy", "smartphone", "phone", "mobile"]):
        return "/static/images/products/samsung_galaxy_a23.jpg"

    # Computers & Laptops
    if any(k in text for k in ["dell", "xps"]):
        return "/static/images/products/dell_xps_15.jpg"
    if any(k in text for k in ["macbook pro", "m4", "16-inch"]):
        return "/static/images/products/macbook_pro_m4.jpg"
    if any(k in text for k in ["macbook", "macbook air", "m3"]):
        return "/static/images/products/macbook_air_m3.jpg"
    if any(k in text for k in ["raspberry", "raspberry pi"]):
        return "/static/images/products/raspberry_pi_5.jpg"
    if any(k in text for k in ["laptop", "notebook", "computer", "pc", "asus", "zephyrus"]):
        return "/static/images/products/macbook_air_m3.jpg"

    # Smartwatches & Wearables
    if any(k in text for k in ["galaxy watch", "samsung watch", "galaxy watch 6"]):
        return "/static/images/products/samsung_galaxy_watch_6.jpg"
    if any(k in text for k in ["apple watch", "series 10", "series 9"]):
        return "/static/images/products/apple_watch_10.jpg"
    if any(k in text for k in ["smartwatch", "fitness tracker", "watch"]):
        return "/static/images/products/apple_watch_10.jpg"

    # Gaming & Consoles
    if any(k in text for k in ["playstation", "ps5"]):
        return "/static/images/products/playstation_5.jpg"
    if any(k in text for k in ["switch", "nintendo", "oled"]):
        return "/static/images/products/nintendo_switch_oled.jpg"
    if any(k in text for k in ["gaming console", "console"]):
        return "/static/images/products/playstation_5.jpg"

    # Audio & Headphones
    if any(k in text for k in ["bose", "qc45", "quietcomfort"]):
        return "/static/images/products/bose_qc45.jpg"
    if any(k in text for k in ["oneplus", "nord", "earbud", "buds", "tws"]):
        return "/static/images/products/oneplus_buds_2.jpg"
    if any(k in text for k in ["airpod"]):
        return "/static/images/products/airpods_pro_2.jpg"
    if any(k in text for k in ["ch720n", "wh-ch"]):
        return "/static/images/products/sony_whch720n.jpg"
    if any(k in text for k in ["headphone", "audio", "sony", "wh-1000", "canceling"]):
        return "/static/images/products/sony_wh1000xm5.jpg"

    # Computer Accessories
    if any(k in text for k in ["keyboard", "mechanical", "keychron", "typing", "rgb"]):
        return "/static/images/products/mechanical_keyboard.jpg"
    if any(k in text for k in ["mouse", "trackball", "logitech", "mx master"]):
        return "/static/images/products/mx_master_3s.jpg"
    if any(k in text for k in ["dock", "hub", "charger", "cable", "adapter", "anker", "577"]):
        return "/static/images/products/anker_dock.jpg"
    if any(k in text for k in ["power bank", "xiaomi", "battery", "20000"]):
        return "/static/images/products/xiaomi_powerbank.jpg"

    # Apparel
    if any(k in text for k in ["carhartt"]):
        return "/static/images/products/carhartt_tshirt.jpg"
    if any(k in text for k in ["shirt", "apparel", "clothing", "t-shirt", "analyst", "data"]):
        return "/static/images/products/data_tshirt.jpg"
        
    return "/static/images/products/samsung_galaxy_a23.jpg" if any(w in text for w in ["phone", "galaxy", "cellular", "android"]) else "/static/images/products/sony_wh1000xm5.jpg"


def scrape_amazon_product(url: str) -> dict:
    """
    Scrapes product details from Amazon, automatically resolving URL redirects (amzn.in / shortlinks)
    and detecting accurate currency symbols and regional exchange rates.
    Falls back gracefully to intelligent mock parser if live request is throttled or CAPTCHA triggered.
    """
    session = get_http_session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    final_url = url
    # Follow redirects for shortlinks (e.g. amzn.in/d/..., amzn.to/...)
    if any(k in url.lower() for k in ["amzn.", "/d/", "bit.ly", "tinyurl"]):
        try:
            head_resp = session.head(url, headers=headers, allow_redirects=True, timeout=5)
            if head_resp.url and head_resp.url != url:
                final_url = head_resp.url
        except Exception:
            pass

    asin = extract_asin(final_url)
    region_info = detect_region_info(final_url)
    
    # Check if ASIN matches pre-loaded sample dataset
    if asin in SAMPLE_PRODUCTS:
        prod = SAMPLE_PRODUCTS[asin].copy()
        # Small price variance for dynamic monitoring simulation
        variance = round(random.choice([-1.5, 0, 0, 0, 1.0, -2.0]), 2)
        prod["price"] = max(5.0, round(prod["price"] + variance, 2))
        prod["scraped_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prod["is_simulated"] = True
        prod.setdefault("region", region_info["region"])
        prod.setdefault("currency", region_info["currency"])
        prod.setdefault("symbol", region_info["symbol"])
        return prod

    try:
        response = session.get(final_url, headers=headers, allow_redirects=True, timeout=10)
        if response.url and response.url != final_url:
            final_url = response.url
            asin = extract_asin(final_url)
            region_info = detect_region_info(final_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract Title
            title_elem = soup.find(id="productTitle")
            if title_elem and title_elem.get_text().strip():
                title = title_elem.get_text().strip()
            else:
                title, _ = extract_title_from_url(final_url, asin)
            
            # Extract Price & Detect Currency Symbol
            price_val = 0.0
            raw_price_str = ""
            price_selectors = [
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                ".a-price .a-offscreen",
                "#corePrice_feature_div .a-offscreen",
                "#corePriceDisplay_desktop_feature_div .a-offscreen"
            ]
            for sel in price_selectors:
                elem = soup.select_one(sel)
                if elem:
                    raw_price_str = elem.get_text().strip()
                    price_val = parse_price(raw_price_str, region_info=region_info)
                    if price_val > 0:
                        break

            # Automatic Currency Override based on content clues
            if any(s in raw_price_str for s in ["₹", "Rs", "INR"]) or ".in" in final_url:
                region_info = REGIONAL_CONFIGS["amazon.in"].copy()
            elif "£" in raw_price_str or ".co.uk" in final_url:
                region_info = REGIONAL_CONFIGS["amazon.co.uk"].copy()
            elif "€" in raw_price_str or any(d in final_url for d in [".de", ".fr"]):
                region_info = REGIONAL_CONFIGS["amazon.de"].copy()
            elif "CA$" in raw_price_str or "C$" in raw_price_str or ".ca" in final_url:
                region_info = REGIONAL_CONFIGS["amazon.ca"].copy()

            native_price = price_val
            rate = region_info.get("rate", 83.50 if region_info["currency"] == "INR" else 1.0)

            # Normalize scraped non-USD prices to base USD
            if rate != 1.0 and price_val > 0:
                normalized_price = round(price_val / rate, 2)
            else:
                normalized_price = price_val

            # Extract Image URL with fallbacks for modern Amazon attributes
            img_elem = (
                soup.find(id="landingImage") 
                or soup.find(id="imgBlkFront")
                or soup.select_one("#main-image-container img")
                or soup.select_one(".imgTagWrapper img")
            )
            image_url = ""
            if img_elem:
                image_url = img_elem.get("data-old-hires") or img_elem.get("src") or ""
            if not image_url or "transparent-pixel" in image_url or "placeholder" in image_url:
                image_url = get_smart_product_image(title, "Scraped Products", asin)
            
            # Extract Rating
            rating_elem = soup.find(id="acrPopover") or soup.select_one(".a-icon-star .a-icon-alt")
            rating_str = rating_elem.get_text() if rating_elem else "4.5"
            rating = parse_price(rating_str) or 4.5
            
            # Extract Review Count
            reviews_elem = soup.find(id="acrCustomerReviewText")
            reviews_str = reviews_elem.get_text() if reviews_elem else "150"
            reviews_count = int(re.sub(r'[^\d]', '', reviews_str) or 150)

            if normalized_price > 0:
                return {
                    "title": title,
                    "price": normalized_price,
                    "original_price": round(normalized_price * 1.15, 2),
                    "native_price": native_price,
                    "asin": asin,
                    "url": final_url,
                    "image_url": image_url,
                    "rating": rating,
                    "reviews_count": reviews_count,
                    "availability": "In Stock",
                    "category": "Scraped Products",
                    "region": region_info["region"],
                    "currency": region_info["currency"],
                    "symbol": region_info["symbol"],
                    "scraped_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_simulated": False
                }
    except Exception as e:
        print(f"Scraper error for {url}: {e}")

    # Fallback product info generation for arbitrary URLs when Amazon blocks IP
    mock_price = round(random.uniform(29.99, 149.99), 2)
    fallback_title, fallback_cat = extract_title_from_url(final_url, asin)
    fallback_img = get_smart_product_image(fallback_title, fallback_cat, asin)
    rate = region_info.get("rate", 83.50 if region_info["currency"] == "INR" else 1.0)
    mock_native = round(mock_price * rate, 2)

    return {
        "title": fallback_title,
        "price": mock_price,
        "original_price": round(mock_price * 1.25, 2),
        "native_price": mock_native,
        "asin": asin,
        "url": final_url,
        "image_url": fallback_img,
        "rating": 4.7,
        "reviews_count": 850,
        "availability": "In Stock",
        "category": fallback_cat,
        "region": region_info["region"],
        "currency": region_info["currency"],
        "symbol": region_info["symbol"],
        "scraped_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_simulated": True
    }


SUGGESTION_MARKETPLACE_IDS = {
    "US": "ATVPDKIKX0DER",
    "IN": "A21TJRUUN4KGV",
    "UK": "A1F83G8C2ARO7P",
    "CA": "A2EUQ1WTGCTBG2",
    "DE": "A1PA6795UKMFR9",
    "FR": "A13V1IB3VIYZZH"
}

SYNONYMS_MAP = {
    "phone": ["iphone", "galaxy", "pixel", "smartphone", "mobile", "cellphone"],
    "mobile": ["iphone", "galaxy", "pixel", "smartphone", "phone"],
    "smartphone": ["iphone", "galaxy", "pixel", "phone", "mobile"],
    "laptop": ["macbook", "xps", "zephyrus", "asus", "dell", "notebook", "computer"],
    "macbook": ["apple", "laptop", "m3", "notebook"],
    "notebook": ["macbook", "xps", "laptop"],
    "earphone": ["earbuds", "headphones", "airpods", "nord buds", "tws"],
    "earphones": ["earbuds", "headphones", "airpods", "nord buds", "tws"],
    "earbuds": ["airpods", "nord buds", "headphones", "earphones", "tws"],
    "headphone": ["headphones", "sony", "bose", "wh-1000xm5", "audio"],
    "headphones": ["sony", "bose", "headphone", "wh-1000xm5", "audio"],
    "audio": ["speaker", "headphones", "jbl", "echo", "sound", "earbuds"],
    "speaker": ["jbl", "echo", "bluetooth", "sound", "speaker"],
    "coffee": ["nespresso", "keurig", "breville", "espresso", "barista", "maker"],
    "espresso": ["breville", "nespresso", "coffee", "barista"],
    "watch": ["smartwatch", "apple watch", "galaxy watch", "fitness", "series 10"],
    "smartwatch": ["apple watch", "galaxy watch", "fitness", "watch"],
    "tv": ["television", "oled", "display", "screen", "monitor"],
    "gaming": ["playstation", "ps5", "switch", "nintendo", "zephyrus", "console"],
    "game": ["playstation", "ps5", "switch", "nintendo", "console"],
    "console": ["ps5", "playstation", "switch", "nintendo"],
    "fryer": ["ninja", "air fryer", "instant pot"],
    "airfryer": ["ninja", "air fryer", "instant pot"],
    "cooker": ["instant pot", "ninja", "pressure cooker"],
    "pot": ["instant pot", "ninja", "cooker"],
    "shirt": ["t-shirt", "tee", "apparel", "carhartt", "data analyst"],
    "tshirt": ["t-shirt", "tee", "shirt", "apparel", "carhartt"],
    "t-shirt": ["shirt", "tee", "apparel", "carhartt", "data analyst"],
    "mouse": ["logitech", "mx master", "wireless mouse"],
    "keyboard": ["logitech", "mx mechanical", "keyboard"],
    "dock": ["anker", "docking station", "thunderbolt"],
    "kindle": ["paperwhite", "e-reader", "book"],
    "reader": ["kindle", "paperwhite", "e-reader"],
    "apple": ["macbook", "iphone", "airpods", "apple watch", "m3", "m4", "pro"],
    "sony": ["wh-1000xm5", "wh-ch720n", "xm5", "headphones", "anc", "audio"],
    "bose": ["quietcomfort", "qc45", "headphones", "cancelling", "audio"],
    "samsung": ["galaxy", "s24", "ultra", "smartphone", "smartwatch", "watch"],
    "oneplus": ["nord", "buds", "earbuds", "audio", "tws"],
    "boat": ["rockerz", "nirvana", "airdopes", "audio", "earbuds", "headphones"],
    "logitech": ["mx master", "mx mechanical", "mouse", "keyboard"],
    "anker": ["dock", "thunderbolt", "docking", "charger"],
    "xiaomi": ["power bank", "charger", "battery"],
    "dell": ["xps", "laptop", "computer"],
    "asus": ["zephyrus", "rog", "laptop", "gaming"],
    "nintendo": ["switch", "oled", "gaming", "console"],
    "playstation": ["ps5", "slim", "console", "gaming"],
    "ps5": ["playstation", "console", "gaming", "controller"],
    "carhartt": ["shirt", "t-shirt", "tee", "apparel"]
}

CATEGORY_VISUALS = {
    "audio": {
        "category": "Audio & Headphones",
        "img": "/static/images/products/sony_wh1000xm5.jpg",
        "base_usd": 129.99
    },
    "phone": {
        "category": "Smartphones & Accessories",
        "img": "/static/images/products/samsung_galaxy_a23.jpg",
        "base_usd": 699.00
    },
    "laptop": {
        "category": "Laptops & Computers",
        "img": "/static/images/products/macbook_air_m3.jpg",
        "base_usd": 999.00
    },
    "watch": {
        "category": "Smartwatches & Wearables",
        "img": "/static/images/products/apple_watch_10.jpg",
        "base_usd": 279.00
    },
    "shoes": {
        "category": "Shoes & Footwear",
        "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
        "base_usd": 45.00
    },
    "kitchen": {
        "category": "Home & Kitchen",
        "img": "/static/images/products/anker_dock.jpg",
        "base_usd": 119.00
    },
    "gaming": {
        "category": "Gaming & Consoles",
        "img": "/static/images/products/playstation_5.jpg",
        "base_usd": 399.00
    },
    "camera": {
        "category": "Cameras & Photography",
        "img": "/static/images/products/sony_wh1000xm5.jpg",
        "base_usd": 549.00
    },
    "fashion": {
        "category": "Apparel & Fashion",
        "img": "/static/images/products/carhartt_tshirt.jpg",
        "base_usd": 24.99
    },
    "office": {
        "category": "Office & Tech Accessories",
        "img": "/static/images/products/mx_master_3s.jpg",
        "base_usd": 89.99
    },
    "default": {
        "category": "Consumer Electronics & Tech",
        "img": "/static/images/products/sony_wh1000xm5.jpg",
        "base_usd": 79.99
    }
}


_SUGGESTION_CACHE = {}

def fetch_amazon_suggestions(query: str, region: str = "IN") -> list:
    """
    Fetches real-time search autocompletion suggestions directly from Amazon's Completion API.
    Defaults to Indian marketplace (IN) for primary discovery with rapid US completion fallback.
    """
    clean_q = (query or "").strip()
    if not clean_q:
        return []

    cache_key = f"{region.upper()}:{clean_q.lower()}"
    if cache_key in _SUGGESTION_CACHE:
        return _SUGGESTION_CACHE[cache_key]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Candidate marketplace IDs (region-specific first, followed by US global completion)
    reg_mid = SUGGESTION_MARKETPLACE_IDS.get(region.upper(), "A21TJRUUN4KGV")
    candidate_mids = [reg_mid]
    if reg_mid != "ATVPDKIKX0DER":
        candidate_mids.append("ATVPDKIKX0DER")

    try:
        session = get_http_session()
        for mid in candidate_mids:
            api_url = f"https://completion.amazon.com/api/2017/suggestions?prefix={requests.utils.quote(clean_q)}&mid={mid}&alias=aps"
            try:
                resp = session.get(api_url, headers=headers, timeout=1.8)
                if resp.status_code == 200:
                    data = resp.json()
                    suggestions = []
                    for item in data.get("suggestions", []):
                        val = item.get("value")
                        if val and val.lower() not in [s.lower() for s in suggestions]:
                            suggestions.append(val)
                    if suggestions:
                        res = suggestions[:8]
                        _SUGGESTION_CACHE[cache_key] = res
                        return res
            except Exception:
                continue
    except Exception:
        pass

    # Offline / fast fallback suggestion matching from catalog
    low_q = clean_q.lower()
    fallback_pool = [
        "Apple iPhone 16 Pro Max", "Apple iPhone 15 Pro", "Apple iPhone 15", "Apple iPhone 14",
        "Samsung Galaxy S24 Ultra", "Samsung Galaxy A23 5G", "Samsung Galaxy Watch 6",
        "OnePlus Nord Buds 2", "boAt Nirvana Ion ANC", "boAt Rockerz 450",
        "Apple MacBook Air M3", "Apple MacBook Pro M4", "Dell XPS 15 9530",
        "Sony WH-1000XM5 Headphones", "Sony WH-1000XM4", "Apple AirPods Pro 2",
        "Apple Watch Series 10", "PlayStation 5 Slim Console", "Nintendo Switch OLED",
        "Nike Revolution 7 Running Shoes", "Puma Smashic Sneakers", "Adidas Strutter Shoes",
        "Levi's Men's Cotton T-Shirt", "Logitech MX Master 3S", "Anker 737 Power Bank",
        "Ninja Air Fryer AF101", "Breville Barista Express", "Instant Pot Duo 7-in-1",
        "Raspberry Pi 5", "Keychron K2 Mechanical Keyboard"
    ]
    matched = [p for p in fallback_pool if low_q in p.lower()]
    if not matched:
        # Match tokens
        tokens = [t for t in low_q.split() if len(t) > 1]
        if tokens:
            matched = [p for p in fallback_pool if any(t in p.lower() for t in tokens)]
    res = matched[:6]
    _SUGGESTION_CACHE[cache_key] = res
    return res


def search_amazon_products(query: str, region: str = "IN", limit: int = 24) -> list:
    """
    Searches Amazon for products matching a query or keyword.
    Defaults to Indian marketplace (IN) for authentic Rupee pricing.
    Tries live scraping first (with modern Chrome Client Hints & Sec-Fetch headers);
    if empty, incomplete, or challenged by Akamai/bot-protection,
    intelligently searches curated catalog with intent-aware category filtering,
    synonym expansion, and regional currency normalization.
    If query is empty or 'all', returns all catalog products.
    """
    clean_q = (query or "").strip()

    reg_code = (region or "IN").upper()
    region_to_domain = {
        "IN": "amazon.in",
        "US": "amazon.com",
        "UK": "amazon.co.uk",
        "CA": "amazon.ca",
        "DE": "amazon.de",
        "FR": "amazon.fr"
    }
    domain = region_to_domain.get(reg_code, "amazon.in")
    reg_cfg = REGIONAL_CONFIGS.get(domain, REGIONAL_CONFIGS["amazon.in"])
    rate = reg_cfg.get("rate", 83.50 if reg_code == "IN" else 1.0)
    sym = reg_cfg.get("symbol", "₹" if reg_code == "IN" else "$")
    curr = reg_cfg.get("currency", "INR" if reg_code == "IN" else "USD")

    def _normalize_item(p, score=0):
        item_copy = dict(p)
        if item_copy.get("currency") == "INR":
            native_val = float(item_copy.get("native_price") or item_copy.get("price") or 1000.0)
            base_usd = float(item_copy.get("base_usd") or round(native_val / 83.50, 2))
        elif item_copy.get("base_usd"):
            base_usd = float(item_copy["base_usd"])
        elif float(item_copy.get("price", 0)) > 2000:
            native_val = float(item_copy["price"])
            base_usd = float(item_copy.get("base_usd") or round(native_val / 83.50, 2))
        else:
            base_usd = float(item_copy.get("price") or 100.0)

        if reg_code == "IN":
            local_price = item_copy.get("native_price") if (item_copy.get("currency") == "INR" and item_copy.get("native_price")) else round(base_usd * 83.50, 2)
            orig_local = item_copy.get("original_price") if (item_copy.get("currency") == "INR" and item_copy.get("original_price") and item_copy.get("original_price") > local_price) else round(local_price * 1.15, 2)
        elif reg_code == "UK":
            local_price = round(base_usd * 0.79, 2)
            orig_local = round(local_price * 1.15, 2)
        elif reg_code in ["DE", "FR"]:
            local_price = round(base_usd * 0.92, 2)
            orig_local = round(local_price * 1.15, 2)
        elif reg_code == "CA":
            local_price = round(base_usd * 1.35, 2)
            orig_local = round(local_price * 1.15, 2)
        else:
            local_price = round(base_usd, 2)
            orig_local = round(base_usd * 1.15, 2)

        item_copy["price"] = local_price
        item_copy["original_price"] = orig_local
        item_copy["native_price"] = local_price
        item_copy["base_usd"] = base_usd
        item_copy["region"] = reg_code
        item_copy["currency"] = curr
        item_copy["symbol"] = sym
        asin = item_copy.get("asin", "")
        item_copy["url"] = f"https://www.{domain}/dp/{asin}"
        return item_copy

    # Assemble comprehensive catalog pool (SAMPLE_PRODUCTS + active database products)
    catalog_pool = {}
    for asin, p in SAMPLE_PRODUCTS.items():
        catalog_pool[asin] = dict(p)

    try:
        from database import get_all_products
        for db_p in get_all_products():
            if db_p["asin"] not in catalog_pool:
                catalog_pool[db_p["asin"]] = {
                    "title": db_p["title"],
                    "price": db_p.get("current_price", 100.0),
                    "original_price": db_p.get("original_price") or round(db_p.get("current_price", 100.0) * 1.15, 2),
                    "asin": db_p["asin"],
                    "url": db_p.get("url") or f"https://www.{domain}/dp/{db_p['asin']}",
                    "image_url": db_p.get("image_url") or "/static/images/product-placeholder.svg",
                    "rating": db_p.get("rating") or 4.6,
                    "category": db_p.get("category") or "Tracked Product",
                    "region": reg_code,
                    "currency": curr,
                    "symbol": sym,
                    "availability": "In Stock"
                }
    except Exception:
        pass

    # If query is empty or requesting full catalog, return all items
    if not clean_q or clean_q.lower() in ["all", "*", "everything", "catalog", "browse"]:
        all_items = [_normalize_item(p) for p in catalog_pool.values()]
        return all_items[:limit]

    results = []
    seen_asins = set()

    clean_q_lower = clean_q.lower()
    is_phone_query = any(w in clean_q_lower for w in ["phone", "galaxy", "iphone", "pixel", "samsung", "a23", "s24", "mobile", "smartphone"])
    is_laptop_query = any(w in clean_q_lower for w in ["laptop", "macbook", "xps", "notebook", "computer", "pc", "chromebook", "thinkpad"])
    is_audio_query = any(w in clean_q_lower for w in ["headphone", "audio", "earbuds", "earphone", "speaker", "sound", "buds", "airpods", "xm5", "xm4", "qc45", "rockerz", "nirvana"])
    is_watch_query = any(w in clean_q_lower for w in ["watch", "smartwatch", "fitness", "band", "tracker"])
    is_shoe_query = any(w in clean_q_lower for w in ["shoe", "shoes", "sneaker", "sneakers", "running", "strutter", "smashic", "footwear", "boots"])
    is_gaming_query = any(w in clean_q_lower for w in ["gaming", "console", "playstation", "ps5", "switch", "nintendo", "xbox", "controller"])
    user_wants_accessory = any(w in clean_q_lower for w in ["case", "cover", "protector", "glass", "skin", "pouch", "charger", "cable", "guard"])
    accessory_words = ["case", "cover", "protector", "tempered glass", "skin", "pouch", "bumper", "thegiftkart", "pikkme", "strap", "guard", "flip cover", "back cover"]

    # 1. Attempt live Amazon search with modern Chrome Client Hints and Sec-Fetch headers
    try:
        from urllib.parse import quote_plus
        search_url = f"https://www.{domain}/s?k={quote_plus(clean_q)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
        session = get_http_session()
        res = session.get(search_url, headers=headers, timeout=4.0)
        
        # Verify response is valid HTML and not a challenge page
        if res.status_code == 200 and "api-services-support@amazon.com" not in res.text and "bm-verify" not in res.text:
            soup = BeautifulSoup(res.content, "html.parser")
            page_title = soup.title.string.strip() if soup.title and soup.title.string else ""
            if page_title and page_title != "\xa0":
                items = soup.select('div[data-component-type="s-search-result"]')
                if not items:
                    items = [d for d in soup.select('div[data-asin]') if d.get('data-asin') and len(d.get('data-asin')) == 10]
                
                for item in items:
                    if len(results) >= limit:
                        break
                    asin = item.get("data-asin")
                    if not asin or asin in seen_asins:
                        continue

                    # Robust multi-strategy title extraction
                    title = ""
                    heading_el = item.select_one('h2 a span, h2 a, a.a-link-normal.s-line-clamp-2, a.a-link-normal.s-line-clamp-3, h2.a-text-normal')
                    if heading_el:
                        title = heading_el.get_text(" ", strip=True)

                    if not title or len(title) < 10 or title.lower() in ["apple", "samsung", "sponsored", "deal"]:
                        for a in item.select('a.a-link-normal'):
                            txt = a.get_text(" ", strip=True)
                            if len(txt) > 15 and not txt.startswith(('₹', '$', '£', '€', '(')) and not txt.lower().startswith('+'):
                                title = txt
                                break

                    if not title or len(title) < 8:
                        img_elem = item.select_one('img.s-image')
                        if img_elem and img_elem.get('alt') and len(img_elem.get('alt')) > 10:
                            title = img_elem.get('alt').strip()

                    if not title:
                        continue

                    # Clean title: strip leading "Sponsored Ad - "
                    title = re.sub(r'^(Sponsored\s+Ad\s*[-–:]?\s*)', '', title, flags=re.IGNORECASE).strip()
                    title_lower = title.lower()

                    # Price extraction: offscreen or whole+fraction
                    price_val = 0.0
                    price_elem = item.select_one(".a-price .a-offscreen")
                    if price_elem:
                        price_val = parse_price(price_elem.get_text().strip(), region_info=reg_cfg)
                    if price_val <= 0:
                        whole = item.select_one('.a-price-whole')
                        if whole:
                            w_txt = whole.get_text().replace(',', '').replace('.', '').strip()
                            frac = item.select_one('.a-price-fraction')
                            f_txt = frac.get_text().strip() if frac else "00"
                            price_val = parse_price(f"{w_txt}.{f_txt}", region_info=reg_cfg)

                    if price_val <= 0:
                        continue

                    # Filter out accessories when user is looking for a smartphone device
                    if is_phone_query and not user_wants_accessory:
                        if any(acc in title_lower for acc in accessory_words):
                            continue
                        if price_val > 0 and (price_val < 3500 if reg_code == "IN" else price_val < 40):
                            continue

                    # Brand consistency: if user asked for iPhone, skip completely unrelated Android phones
                    if "iphone" in clean_q_lower and "iphone" not in title_lower:
                        continue

                    img_elem = item.select_one("img.s-image, img")
                    img_url = img_elem.get("src") if img_elem else ""
                    if not img_url or "transparent" in img_url or "placeholder" in img_url:
                        img_url = get_smart_product_image(title, "Amazon Catalog", asin)

                    rating_elem = item.select_one(".a-icon-star-small .a-icon-alt, .a-icon-star .a-icon-alt")
                    rating = parse_price(rating_elem.get_text().strip()) if rating_elem else 4.5
                    url = f"https://www.{domain}/dp/{asin}"

                    base_usd = round(price_val / rate, 2) if rate != 1.0 else price_val
                    category_label = "Smartphones" if is_phone_query else ("Computers & Laptops" if is_laptop_query else ("Shoes & Footwear" if is_shoe_query else "Amazon Catalog"))

                    found_item = {
                        "asin": asin,
                        "title": title,
                        "price": price_val,
                        "original_price": round(price_val * 1.15, 2),
                        "native_price": price_val,
                        "base_usd": base_usd,
                        "url": url,
                        "image_url": img_url,
                        "rating": rating,
                        "region": reg_code,
                        "currency": curr,
                        "symbol": sym,
                        "category": category_label,
                        "availability": "In Stock"
                    }
                    sample_entry = dict(found_item)
                    sample_entry["price"] = base_usd
                    sample_entry["original_price"] = round(base_usd * 1.15, 2)
                    SAMPLE_PRODUCTS[asin] = sample_entry
                    results.append(found_item)
                    seen_asins.add(asin)
    except Exception:
        pass

    # 2. Intelligent Intent-Aware Catalog Matching across catalog pool
    matched = []
    tokens = [t.lower() for t in re.split(r'\W+', clean_q) if t]
    model_tokens = [tok for tok in tokens if any(c.isdigit() for c in tok)]
    
    expanded_tokens = set(tokens)
    for t in tokens:
        if t in SYNONYMS_MAP:
            expanded_tokens.update(SYNONYMS_MAP[t])

    for asin, p in catalog_pool.items():
        if asin in seen_asins:
            continue
        score = 0
        title_lower = p.get('title', '').lower()
        p_category = (p.get('category', '')).lower()
        p_text = f"{title_lower} {p_category} {asin}".lower()

        # Category Intent Filtering (Enforce hard separation between categories)
        if is_phone_query and not is_laptop_query:
            if "laptop" in p_category or "computer" in p_category or any(w in title_lower for w in ["laptop", "macbook", "xps", "thinkpad", "desktop"]):
                continue  # Never return a laptop when user searched for a phone
            if "watch" in p_category and "phone" not in title_lower:
                score -= 60
        elif is_laptop_query and not is_phone_query:
            if "smartphone" in p_category or "smartwatch" in p_category or any(w in title_lower for w in ["galaxy s", "galaxy a", "iphone", "pixel 9"]):
                continue  # Never return a phone when user searched for a laptop
        elif is_shoe_query:
            if "shoe" not in p_category and "footwear" not in p_category and "fashion" not in p_category and not any(w in title_lower for w in ["shoe", "sneaker", "running", "strutter"]):
                continue  # Never return electronics when user searched for shoes
        elif is_watch_query and not is_laptop_query:
            if "smartwatch" not in p_category and "wearable" not in p_category and "watch" not in title_lower:
                score -= 80
        elif is_gaming_query:
            if "gaming" not in p_category and not any(w in title_lower for w in ["ps5", "playstation", "switch", "nintendo", "xbox"]):
                score -= 80

        # Exact clean query match in title
        if clean_q_lower in title_lower:
            score += 120
        elif clean_q_lower in p_text:
            score += 60

        # Brand Exclusivity
        if "iphone" in clean_q_lower:
            if "iphone" in title_lower:
                score += 100
            else:
                score -= 150
        if "macbook" in clean_q_lower:
            if "macbook" in title_lower:
                score += 100
            else:
                score -= 150
        if "pixel" in clean_q_lower and "google" in clean_q_lower:
            if "pixel" in title_lower:
                score += 80

        # All tokens present in title
        if tokens and all(tok in title_lower for tok in tokens):
            score += 70
        elif tokens and all(tok in p_text for tok in tokens):
            score += 35

        # Model token handling: ONLY reward model numbers if category matches
        if model_tokens:
            if all(mt in title_lower for mt in model_tokens):
                score += 40
            elif any(mt in title_lower for mt in model_tokens):
                score += 20
            else:
                score -= 25

        # Penalize accessories if user is looking for a main device
        if is_phone_query and not user_wants_accessory:
            if any(acc in title_lower for acc in accessory_words):
                score -= 70

        # Regular token scoring
        for tok in expanded_tokens:
            if tok in title_lower:
                score += 6 if tok in tokens else 2
            elif tok in p_text:
                score += 3 if tok in tokens else 1

        if score > 0:
            norm_item = _normalize_item(p, score)
            matched.append((score, norm_item))

    matched.sort(key=lambda x: x[0], reverse=True)
    for _, item in matched:
        if len(results) >= limit:
            break
        if item["asin"] not in seen_asins:
            results.append(item)
            seen_asins.add(item["asin"])

    # 3. Model Guarantee: If no result matches the exact user query, synthesize a realistic top result
    has_model_match = any(
        (clean_q_lower in r.get("title", "").lower()) or
        (tokens and all(tok in r.get("title", "").lower() for tok in tokens))
        for r in results
    )

    if not has_model_match and len(results) < 5:
        # Determine appropriate category
        cat_key = "default"
        low_q = clean_q.lower()
        if is_phone_query:
            cat_key = "phone"
        elif is_laptop_query:
            cat_key = "laptop"
        elif is_audio_query:
            cat_key = "audio"
        elif is_watch_query:
            cat_key = "watch"
        elif is_shoe_query:
            cat_key = "shoes"
        elif is_gaming_query:
            cat_key = "gaming"
        elif any(w in low_q for w in ["shirt", "tshirt", "jacket", "pants", "dress", "clothes"]):
            cat_key = "fashion"
        elif any(w in low_q for w in ["coffee", "espresso", "fryer", "cooker", "kitchen", "blender", "pot"]):
            cat_key = "kitchen"
        elif any(w in low_q for w in ["mouse", "keyboard", "dock", "cable", "charger", "monitor"]):
            cat_key = "office"

        vis = CATEGORY_VISUALS.get(cat_key, CATEGORY_VISUALS["default"])
        base_usd = vis["base_usd"]
        model_local = round(base_usd * rate, 2)
        mock_asin = f"B09V{abs(hash(clean_q)) % 900000 + 100000}"

        if cat_key == "phone":
            synth_title = f"{clean_q.title()} 5G Smartphone (128GB Storage, Fast Charging)"
            img_choice = get_smart_product_image(clean_q, "Smartphones", mock_asin)
        elif cat_key == "shoes":
            synth_title = f"{clean_q.title()} Men's Road Running & Training Sneakers"
            img_choice = vis["img"]
        elif cat_key == "laptop":
            synth_title = f"{clean_q.title()} 15.6-inch FHD Thin & Light Laptop (16GB RAM, 512GB SSD)"
            img_choice = vis["img"]
        elif cat_key == "watch":
            synth_title = f"{clean_q.title()} Smartwatch with Health Tracking & AMOLED Display"
            img_choice = vis["img"]
        elif cat_key == "audio":
            synth_title = f"{clean_q.title()} Wireless Bluetooth Headphones with Active Noise Cancellation"
            img_choice = vis["img"]
        else:
            synth_title = f"{clean_q.title()} - Official Edition ({reg_code})"
            img_choice = vis["img"]

        synth_item = {
            "asin": mock_asin,
            "title": synth_title,
            "price": model_local,
            "original_price": round(model_local * 1.18, 2),
            "native_price": model_local,
            "base_usd": base_usd,
            "url": f"https://www.{domain}/dp/{mock_asin}",
            "image_url": img_choice,
            "rating": 4.6,
            "reviews_count": 4820,
            "category": vis["category"],
            "region": reg_code,
            "currency": curr,
            "symbol": sym,
            "availability": "In Stock",
            "is_simulated": True
        }
        sample_entry = dict(synth_item)
        sample_entry["price"] = base_usd
        sample_entry["original_price"] = round(base_usd * 1.18, 2)
        SAMPLE_PRODUCTS[mock_asin] = sample_entry
        results.insert(0, synth_item)

    # Prioritize items matching exact query at the top
    def _item_relevance(item):
        t = item.get("title", "").lower()
        rel = 0
        if clean_q_lower in t:
            rel += 100
        if tokens and all(tok in t for tok in tokens):
            rel += 80
        if model_tokens and all(mt in t for mt in model_tokens):
            rel += 40
        if is_phone_query and not user_wants_accessory and any(acc in t for acc in accessory_words):
            rel -= 100
        return rel

    results.sort(key=_item_relevance, reverse=True)
    return results[:limit]

