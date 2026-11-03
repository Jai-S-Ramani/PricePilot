"""
Automated Test Suite for Advanced Features:
1. Direct Amazon Product Search (Live & Catalog matching)
2. Multi-Channel Alerting (Discord Webhooks & Telegram alerts)
3. Smart Deal Scores (0-100%) and Price Trend Velocity
4. Competitor Price Match Guarantee Engine
5. SQLite WAL Concurrency & Notification Settings Persistence
6. Flask REST API endpoints for all new features
"""

import unittest
import json
import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from scraper import search_amazon_products
from notifier import send_discord_alert, send_telegram_alert, dispatch_multi_channel_alert
from competitor import detect_price_match_guarantee, get_competitor_prices
from database import (
    get_all_products, get_product_by_id, get_product_stats,
    calculate_deal_score, create_user, get_user_by_email,
    update_user_notification_settings, get_db_connection,
    calculate_price_forecast
)
from app import app


class TestAdvancedFeatures(unittest.TestCase):
    """Unit tests for newly added advanced features."""

    def setUp(self):
        self.client = app.test_client()

    def test_search_amazon_products_keyword(self):
        """Test searching products by keyword."""
        results = search_amazon_products("MacBook", region="US", limit=3)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        first = results[0]
        self.assertIn("asin", first)
        self.assertIn("title", first)
        self.assertIn("price", first)
        self.assertGreater(first["price"], 0)

    def test_search_amazon_products_fallback(self):
        """Test search handles arbitrary keywords gracefully."""
        results = search_amazon_products("Quantum Ergonomic Keyboard", region="US", limit=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn("title", results[0])

    def test_fetch_amazon_suggestions_api(self):
        """Test suggestions endpoint and service."""
        from scraper import fetch_amazon_suggestions
        suggestions = fetch_amazon_suggestions("iphone", region="US")
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)

        # Test Flask route
        res = self.client.get("/api/search/suggestions?q=iphone&region=US")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIsInstance(data["suggestions"], list)

    def test_add_product_with_search_metadata(self):
        """Test adding product preserving search result metadata."""
        payload = {
            "url": "https://www.amazon.com/dp/B09VXYZTEST1",
            "title": "Quantum Mechanical Cyber Keyboard Pro",
            "price": 149.99,
            "category": "Office & Tech",
            "rating": 4.9,
            "region": "US",
            "currency": "USD",
            "symbol": "$"
        }
        res = self.client.post("/api/products/add", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["product"]["title"], "Quantum Mechanical Cyber Keyboard Pro")
        self.assertEqual(data["product"]["current_price"], 149.99)
        self.assertEqual(data["product"]["category"], "Office & Tech")

    def test_discord_alert_simulation(self):
        """Test Discord alert simulator works cleanly without live credentials."""
        sent = send_discord_alert(
            webhook_url="simulated_test_webhook",
            product_title="Sony WH-1000XM5",
            current_price=328.00,
            target_price=350.00,
            product_url="https://amazon.com/dp/B09B8V1LZ3",
            savings=22.00
        )
        self.assertTrue(sent)

    def test_telegram_alert_simulation(self):
        """Test Telegram alert simulator works cleanly without live credentials."""
        sent = send_telegram_alert(
            bot_token=None,
            chat_id="12345678",
            message="Test Price Drop Alert"
        )
        self.assertTrue(sent)

    def test_dispatch_multi_channel_alert(self):
        """Test multi-channel dispatcher triggers email, discord, and telegram."""
        user = {
            "email": "demo.user@example.com",
            "discord_webhook": "simulated_webhook",
            "telegram_chat_id": "999888777"
        }
        res = dispatch_multi_channel_alert(
            user=user,
            product_title="Test Laptop",
            current_price=999.00,
            target_price=1050.00,
            product_url="https://amazon.com"
        )
        self.assertTrue(res["email"])
        self.assertTrue(res["discord"])
        self.assertTrue(res["telegram"])

    def test_deal_score_calculation(self):
        """Test deal score and price trend calculations."""
        prods = get_all_products()
        if prods:
            pid = prods[0]["id"]
            analysis = calculate_deal_score(pid)
            self.assertIsNotNone(analysis)
            self.assertIn("deal_score", analysis)
            self.assertIn("deal_grade", analysis)
            self.assertIn("price_trend", analysis)
            self.assertGreaterEqual(analysis["deal_score"], 0)
            self.assertLessEqual(analysis["deal_score"], 100)

    def test_price_match_guarantee_detection(self):
        """Test price match guarantee detection when competitor is cheaper."""
        stores = [
            {"name": "Best Buy", "price": 299.99},
            {"name": "Walmart", "price": 319.99},
            {"name": "Target", "price": 339.99}
        ]
        amazon_price = 328.00
        match = detect_price_match_guarantee(amazon_price, stores)
        self.assertTrue(match["eligible"])
        self.assertEqual(match["competitor"], "Best Buy")
        self.assertEqual(match["savings"], 28.01)

    def test_price_match_guarantee_amazon_lowest(self):
        """Test price match guarantee when Amazon already has the lowest price."""
        stores = [
            {"name": "Best Buy", "price": 349.99},
            {"name": "Walmart", "price": 359.99}
        ]
        amazon_price = 328.00
        match = detect_price_match_guarantee(amazon_price, stores)
        self.assertFalse(match["eligible"])

    def test_sqlite_wal_mode(self):
        """Verify that SQLite connection is running with WAL journal mode."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal")

    def test_notification_settings_persistence(self):
        """Test updating and persisting user notification settings."""
        test_email = "notif_tester@example.com"
        user = get_user_by_email(test_email)
        if not user:
            from werkzeug.security import generate_password_hash
            uid = create_user(test_email, generate_password_hash("password123"), "Notif Tester")
        else:
            uid = user["id"]

        updated = update_user_notification_settings(
            uid,
            discord_webhook="https://discord.com/api/webhooks/test/123",
            telegram_chat_id="@test_deals"
        )
        self.assertEqual(updated["discord_webhook"], "https://discord.com/api/webhooks/test/123")
        self.assertEqual(updated["telegram_chat_id"], "@test_deals")

    def test_api_search_endpoint(self):
        """Test GET /api/search endpoint."""
        res = self.client.get('/api/search?q=Headphones&region=US&limit=3')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIsInstance(data["results"], list)

    def test_api_deal_analysis_endpoint(self):
        """Test GET /api/products/<id>/deal-analysis endpoint."""
        prods = get_all_products()
        if prods:
            pid = prods[0]["id"]
            res = self.client.get(f'/api/products/{pid}/deal-analysis')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["status"], "success")
            self.assertIn("deal_score", data["analysis"])

    def test_api_test_discord_endpoint(self):
        """Test POST /api/notifications/test-discord endpoint."""
        res = self.client.post('/api/notifications/test-discord', json={
            "webhook_url": "simulated_discord_url"
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["simulated"])

    def test_api_export_all_json(self):
        """Test GET /api/export/json endpoint."""
        res = self.client.get('/api/export/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("products", data)
        self.assertIn("kpis", data)
        self.assertGreater(data["total_products"], 0)

    def test_api_refresh_single_product(self):
        """Test POST /api/products/<id>/refresh endpoint."""
        prods = get_all_products()
        if prods:
            pid = prods[0]["id"]
            res = self.client.post(f'/api/products/{pid}/refresh')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["status"], "success")
            self.assertIn("product", data)
            self.assertEqual(data["product"]["id"], pid)

    def test_api_export_product_history_csv(self):
        """Test GET /api/products/<id>/export/csv endpoint."""
        prods = get_all_products()
        if prods:
            pid = prods[0]["id"]
            res = self.client.get(f'/api/products/{pid}/export/csv')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.mimetype, "text/csv")
            csv_text = res.data.decode("utf-8")
            self.assertIn("Title,ASIN,Date,Timestamp", csv_text)

    def test_api_export_product_history_json(self):
        """Test GET /api/products/<id>/export/json endpoint."""
        prods = get_all_products()
        if prods:
            pid = prods[0]["id"]
            res = self.client.get(f'/api/products/{pid}/export/json')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["status"], "success")
            self.assertIn("deal_intelligence", data)
            self.assertIn("history", data)
    def test_product_dependent_delivery_info(self):
        """Test that competitor delivery info dynamically depends on product category, size, and price."""
        from competitor import get_competitor_prices, calculate_product_delivery_info, calculate_amazon_delivery_info

        # 1. Bulky Appliance (e.g. 55-Inch 4K TV)
        tv_prod = {
            "id": 501,
            "asin": "B0TV123456",
            "title": "Sony Bravia 55-Inch 4K Ultra HD Smart LED Google TV",
            "category": "Television & Home Theater",
            "current_price": 54990.0,
            "region": "IN"
        }
        tv_res = get_competitor_prices(tv_prod)
        indian_stores_tv = {s["id"]: s for s in tv_res["indian_stores"]}
        
        # Quick commerce dark stores cannot carry large bulky TVs
        self.assertIn("Exceeds Dark Store Bag Limit", indian_stores_tv["blinkit"]["delivery_info"])
        # Croma / Reliance Digital / Flipkart provide scheduled installation/delivery
        self.assertIn("Scheduled", indian_stores_tv["croma"]["delivery_info"])
        self.assertIn("Scheduled", indian_stores_tv["flipkart"]["delivery_info"])
        # Amazon itself schedules heavy delivery
        self.assertIn("Scheduled", tv_res["amazon_delivery_info"])

        # 2. Quick Tech / Small Gadget (e.g. boAt earbuds)
        buds_prod = {
            "id": 502,
            "asin": "B0BUDS1234",
            "title": "boAt Airdopes 141 Bluetooth Truly Wireless Earbuds",
            "category": "Audio & Headphones",
            "current_price": 1299.0,
            "region": "IN"
        }
        buds_res = get_competitor_prices(buds_prod)
        indian_stores_buds = {s["id"]: s for s in buds_res["indian_stores"]}
        # Quick commerce delivers tech earbuds in 10-15 minutes
        self.assertIn("Instant", indian_stores_buds["blinkit"]["delivery_info"])
        self.assertIn("Instant", indian_stores_buds["zepto"]["delivery_info"])

        # 3. Fashion & Apparel (e.g. Levi's Jeans)
        jeans_prod = {
            "id": 503,
            "asin": "B0JEAN1234",
            "title": "Levi's Men's 511 Slim Fit Stretch Denim Jeans",
            "category": "Clothing & Fashion",
            "current_price": 2499.0,
            "region": "IN"
        }
        jeans_res = get_competitor_prices(jeans_prod)
        indian_stores_jeans = {s["id"]: s for s in jeans_res["indian_stores"]}
        # Myntra offers Try & Buy and easy exchange for fashion
        self.assertIn("Try & Buy", indian_stores_jeans["myntra"]["delivery_info"])

        # 4. Global Low-Value (< $35) vs High-Value (iPhone / Laptop)
        cable_prod = {
            "id": 504,
            "asin": "B0CABLE123",
            "title": "Anker USB C Charger Cable 6ft Braided",
            "category": "Electronics Accessories",
            "current_price": 12.99,
            "region": "US"
        }
        cable_res = get_competitor_prices(cable_prod)
        global_stores_cable = {s["id"]: s for s in cable_res["global_stores"]}
        # Walmart charges standard shipping on under $35 orders
        self.assertIn("$35+", global_stores_cable["walmart"]["delivery_info"])

    def test_calculate_price_forecast(self):
        """Test AI time-series forecast calculation and linear regression slope."""
        # 1. Decreasing price sequence
        history = [100.0, 98.0, 96.0, 95.0, 94.0, 92.0, 90.0]
        forecast = calculate_price_forecast(history, current_price=90.0)
        self.assertIsInstance(forecast, dict)
        self.assertIn("sma_7", forecast)
        self.assertIn("predicted_7d_price", forecast)
        self.assertIn("forecast_points", forecast)
        self.assertEqual(len(forecast["forecast_points"]), 7)
        self.assertLess(forecast["trend_slope"], 0)
        self.assertGreaterEqual(forecast["drop_probability"], 50)
        self.assertLessEqual(forecast["predicted_range_min"], forecast["predicted_7d_price"])
        self.assertGreaterEqual(forecast["predicted_range_max"], forecast["predicted_7d_price"])

        # 2. Empty history fallback
        empty_forecast = calculate_price_forecast([], current_price=None)
        self.assertEqual(empty_forecast["trend_slope"], 0.0)
        self.assertEqual(len(empty_forecast["forecast_points"]), 7)

    def test_notifications_center_api(self):
        """Test GET /api/notifications and POST /api/notifications/mark-read."""
        # Test fetching active notifications
        res = self.client.get('/api/notifications')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("notifications", data)
        self.assertIn("unread_count", data)
        self.assertIsInstance(data["notifications"], list)

        # Test marking all as read
        mark_res = self.client.post(
            '/api/notifications/mark-read',
            data=json.dumps({"notification_ids": ["all"]}),
            content_type='application/json'
        )
        self.assertEqual(mark_res.status_code, 200)
        mark_data = json.loads(mark_res.data)
        self.assertEqual(mark_data.get("status"), "success")
        self.assertEqual(mark_data.get("unread_count"), 0)


if __name__ == '__main__':
    unittest.main()

