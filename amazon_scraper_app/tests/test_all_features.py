"""
Comprehensive Test Suite for Amazon Price Tracker & Intelligence Dashboard
Covers:
1. Scraper multi-region detection, ASIN extraction, and price parsing
2. Database volatility calculation, predictive recommendation engine, and portfolio KPIs
3. Background scheduler controls (status, toggle, interval)
4. Flask API endpoints and CSV dataset export
"""

import unittest
import json
import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from scraper import detect_region_info, extract_asin, parse_price
from database import get_product_stats, get_portfolio_kpis, get_all_products
from scheduler import BackgroundPriceScheduler, price_scheduler
from app import app


class TestMultiRegionScraper(unittest.TestCase):
    """Test multi-region domain parsing, currency detection, and price normalization."""

    def test_extract_asin_standard(self):
        url = "https://www.amazon.com/dp/B07FNW9FGJ?ref=some_ref"
        asin = extract_asin(url)
        self.assertEqual(asin, "B07FNW9FGJ")

    def test_extract_asin_gp_product(self):
        url = "https://www.amazon.in/gp/product/B0BY8MCQ9S"
        asin = extract_asin(url)
        self.assertEqual(asin, "B0BY8MCQ9S")

    def test_extract_asin_raw(self):
        self.assertEqual(extract_asin("B09B8V1LZ3"), "B09B8V1LZ3")

    def test_detect_regions(self):
        test_cases = [
            ("https://www.amazon.com/dp/B07FNW9FGJ", "US", "USD", "$"),
            ("https://www.amazon.in/dp/B0BY8MCQ9S", "IN", "INR", "₹"),
            ("https://www.amazon.co.uk/dp/B09B8V1UK1", "UK", "GBP", "£"),
            ("https://www.amazon.ca/dp/B08N5WRWNW", "CA", "CAD", "CA$"),
            ("https://www.amazon.de/dp/B0CX23VJP5", "DE", "EUR", "€"),
        ]
        for url, expected_region, expected_curr, expected_sym in test_cases:
            info = detect_region_info(url)
            self.assertEqual(info["region"], expected_region, f"Failed region for {url}")
            self.assertEqual(info["currency"], expected_curr, f"Failed currency for {url}")
            self.assertEqual(info["symbol"], expected_sym, f"Failed symbol for {url}")

    def test_parse_price_various_currencies(self):
        self.assertEqual(parse_price("$199.99"), 199.99)
        self.assertEqual(parse_price("₹2,499.00"), 2499.0)
        self.assertEqual(parse_price("£49.50"), 49.50)
        self.assertEqual(parse_price("39,99 €", {"currency": "EUR"}), 39.99)
        self.assertEqual(parse_price("CA$ 120.00"), 120.0)


class TestPredictiveEngineAndAnalytics(unittest.TestCase):
    """Test price volatility algorithms and recommendation signals."""

    def test_product_stats_buy_now_target_met(self):
        # Current price ($80) is below target ($90)
        stats = get_product_stats(product_id=999999, current_price=80.0, original_price=100.0, target_price=90.0)
        self.assertEqual(stats["recommendation"], "BUY_NOW")

    def test_product_stats_for_seeded_products(self):
        # Product 1 is seeded in the database
        stats = get_product_stats(product_id=1, current_price=19.99, original_price=24.99, target_price=19.00)
        self.assertIn("recommendation", stats)
        self.assertIn(stats["recommendation"], ["BUY_NOW", "FAIR_PRICE", "WAIT"])
        self.assertIn(stats["volatility"], ["Stable", "Moderate", "High"])
        self.assertGreaterEqual(stats["discount_pct"], 0.0)

    def test_portfolio_kpis(self):
        kpis = get_portfolio_kpis()
        self.assertIn("total_products", kpis)
        self.assertIn("active_deals", kpis)
        self.assertIn("total_savings", kpis)
        self.assertIn("avg_discount", kpis)
        self.assertGreaterEqual(kpis["total_products"], 0)


class TestBackgroundScheduler(unittest.TestCase):
    """Test background daemon controls and status reports using an isolated test instance."""

    def setUp(self):
        # Create a dedicated, isolated test instance of the scheduler
        self.scheduler = BackgroundPriceScheduler(interval_minutes=20)

    def tearDown(self):
        # Ensure test instance is stopped cleanly
        if self.scheduler.is_running:
            self.scheduler.stop()

    def test_scheduler_status(self):
        status = self.scheduler.get_status()
        self.assertIn("running", status)
        self.assertIn("interval_minutes", status)
        self.assertEqual(status["interval_minutes"], 20)

    def test_scheduler_interval_change(self):
        self.scheduler.set_interval(15)
        self.assertEqual(self.scheduler.interval_minutes, 15)

    def test_scheduler_stop_start(self):
        self.scheduler.start()
        self.assertTrue(self.scheduler.is_running)
        self.scheduler.stop()
        self.assertFalse(self.scheduler.is_running)


class TestFlaskEndpoints(unittest.TestCase):
    """Test web dashboard routes, API JSON responses, and CSV export."""

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Amazon Price Tracker', response.data)

    def test_dashboard_page_loads(self):
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'PricePilot' in response.data or b'Amazon Tracker' in response.data)

    def test_api_products_endpoint(self):
        response = self.app.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "success")
        self.assertIsInstance(data.get("products"), list)
        if len(data["products"]) > 0:
            p = data["products"][0]
            self.assertIn("recommendation", p)
            self.assertIn("volatility", p)
            self.assertIn("discount_pct", p)

    def test_api_kpis_endpoint(self):
        response = self.app.get('/api/kpis')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("kpis", data)

    def test_api_scheduler_status_endpoint(self):
        response = self.app.get('/api/scheduler/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("scheduler", data)

    def test_api_scheduler_toggle_endpoint(self):
        response = self.app.post('/api/scheduler/toggle')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("scheduler", data)
        # Ensure it is running again
        if not data["scheduler"]["running"]:
            self.app.post('/api/scheduler/toggle')

    def test_api_scheduler_interval_endpoint(self):
        response = self.app.post('/api/scheduler/interval',
                                 data=json.dumps({"minutes": 45}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("scheduler", {}).get("interval_minutes"), 45)
        # Reset back to 30
        self.app.post('/api/scheduler/interval',
                      data=json.dumps({"minutes": 30}),
                      content_type='application/json')

    def test_export_csv_endpoint(self):
        response = self.app.get('/api/export/csv')
        self.assertEqual(response.status_code, 200)
        self.assertIn("AmazonWebScraperDataset.csv", response.headers.get("Content-Disposition", ""))
        self.assertIn(b"Title", response.data)

    def test_api_competitors_endpoint(self):
        # Fetch existing products first
        prods_res = self.app.get('/api/products')
        self.assertEqual(prods_res.status_code, 200)
        prods = json.loads(prods_res.data).get("products", [])
        if prods:
            pid = prods[0]["id"]
            res = self.app.get(f'/api/products/{pid}/competitors')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data.get("status"), "success")
            comp = data.get("comparison", {})
            self.assertIn("indian_stores", comp)
            self.assertIn("global_stores", comp)
            self.assertIn("summary", comp)
            self.assertEqual(len(comp["indian_stores"]), 13)
            self.assertEqual(len(comp["global_stores"]), 5)


class TestCompetitorComparisonEngine(unittest.TestCase):
    """Test competitor pricing generator, Indian/Global store configs, fashion/quick commerce, and search links."""

    def test_competitor_indian_stores_all_channels(self):
        from competitor import get_competitor_prices
        product = {
            "id": 101,
            "asin": "B0BY8MCQ9S",
            "title": "boAt Rockerz 450 Bluetooth On Ear Headphones with Mic",
            "current_price": 1499.0,
            "region": "IN"
        }
        res = get_competitor_prices(product)
        self.assertEqual(res["default_market"], "indian")
        self.assertEqual(len(res["indian_stores"]), 13)
        store_names = [s["name"] for s in res["indian_stores"]]
        
        # Mega / Electronics
        self.assertIn("Flipkart", store_names)
        self.assertIn("Croma (Tata Group)", store_names)
        self.assertIn("Reliance Digital", store_names)
        self.assertIn("Tata CLiQ", store_names)
        self.assertIn("JioMart", store_names)

        # Fashion & Beauty
        self.assertIn("Myntra", store_names)
        self.assertIn("AJIO (Reliance)", store_names)
        self.assertIn("Nykaa", store_names)
        self.assertIn("Meesho", store_names)

        # Quick Commerce (10-Min Delivery)
        self.assertIn("Blinkit", store_names)
        self.assertIn("Zepto", store_names)
        self.assertIn("Swiggy Instamart", store_names)
        self.assertIn("BigBasket (Tata)", store_names)

        # Verify search URLs
        myntra = next(s for s in res["indian_stores"] if s["id"] == "myntra")
        self.assertIn("myntra.com/", myntra["search_url"])
        blinkit = next(s for s in res["indian_stores"] if s["id"] == "blinkit")
        self.assertIn("blinkit.com/s/?q=", blinkit["search_url"])

    def test_fashion_and_quick_commerce_channel_detection(self):
        from competitor import detect_product_channel
        fashion_prod = {"title": "Levi's Men Slim Fit Denim Jeans & T-Shirt", "category": "Fashion"}
        self.assertEqual(detect_product_channel(fashion_prod), "fashion")

        quick_prod = {"title": "Tata Tea Gold Leaf Tea & Maggi Instant Noodles", "category": "Grocery"}
        self.assertEqual(detect_product_channel(quick_prod), "quick_commerce")

        tech_prod = {"title": "Apple iPhone 15 Pro Max 256GB Natural Titanium", "category": "Electronics"}
        self.assertEqual(detect_product_channel(tech_prod), "mega")

    def test_competitor_global_stores(self):
        from competitor import get_competitor_prices
        product = {
            "id": 102,
            "asin": "B09B8V1LZ3",
            "title": "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones",
            "current_price": 348.0,
            "region": "US"
        }
        res = get_competitor_prices(product)
        self.assertEqual(res["default_market"], "global")
        self.assertEqual(len(res["global_stores"]), 5)
        store_names = [s["name"] for s in res["global_stores"]]
        self.assertIn("Walmart", store_names)
        self.assertIn("Best Buy", store_names)
        self.assertIn("eBay", store_names)
        self.assertIn("Target", store_names)
        self.assertIn("B&H Photo Video", store_names)

    def test_oneplus_buds_availability_nykaa_not_carried(self):
        """Verify user requirement: Nykaa does not sell OnePlus buds, so it is marked unavailable and not winner."""
        from competitor import classify_product_vertical, is_store_carrying_product, get_competitor_prices

        buds_prod = {
            "id": 201,
            "asin": "B0BY8MCQ9S",
            "title": "OnePlus Buds Pro 2 Bluetooth Truly Wireless in Ear Earbuds with Mic",
            "current_price": 119.99,
            "region": "IN"
        }
        # 1. Vertical classification
        vertical = classify_product_vertical(buds_prod)
        self.assertEqual(vertical, "audio")

        # 2. Store capability check
        # Pure fashion & beauty stores completely do NOT sell audio/buds
        self.assertFalse(is_store_carrying_product("nykaa", "audio"), "Nykaa completely does not sell audio/buds")
        self.assertFalse(is_store_carrying_product("myntra", "audio"), "Myntra completely does not sell audio/buds")
        self.assertFalse(is_store_carrying_product("ajio", "audio"), "AJIO completely does not sell audio/buds")

        # Quick commerce (Blinkit, Zepto, Instamart) and tech/mega stores DO sell audio/buds
        self.assertTrue(is_store_carrying_product("blinkit", "audio"), "Blinkit sells audio/buds in quick commerce")
        self.assertTrue(is_store_carrying_product("zepto", "audio"), "Zepto sells audio/buds in quick commerce")
        self.assertTrue(is_store_carrying_product("instamart", "audio"), "Instamart sells audio/buds in quick commerce")
        self.assertTrue(is_store_carrying_product("croma", "audio"), "Croma should carry audio/buds")
        self.assertTrue(is_store_carrying_product("flipkart", "audio"), "Flipkart should carry audio/buds")

        # 3. get_competitor_prices API output
        res = get_competitor_prices(buds_prod)
        self.assertEqual(res["product_vertical"], "audio")

        nykaa_store = next(s for s in res["indian_stores"] if s["id"] == "nykaa")
        self.assertFalse(nykaa_store["is_available"], "Nykaa must have is_available=False for OnePlus Buds")
        self.assertEqual(nykaa_store["availability_status"], "not_carried")
        self.assertIn("Not Carried", nykaa_store["availability"])

        # Zepto & Blinkit must be available
        zepto_store = next(s for s in res["indian_stores"] if s["id"] == "zepto")
        self.assertTrue(zepto_store["is_available"], "Zepto must have is_available=True for OnePlus Buds")
        blinkit_store = next(s for s in res["indian_stores"] if s["id"] == "blinkit")
        self.assertTrue(blinkit_store["is_available"], "Blinkit must have is_available=True for OnePlus Buds")

        croma_store = next(s for s in res["indian_stores"] if s["id"] == "croma")
        self.assertTrue(croma_store["is_available"], "Croma must have is_available=True for OnePlus Buds")

        # Winner must never be an uncarried store like Nykaa
        self.assertNotEqual(res["summary"]["winner_name"], "Nykaa")


if __name__ == '__main__':
    unittest.main()


