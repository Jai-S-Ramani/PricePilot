import unittest
import os
import sys
import json

# Ensure amazon_scraper_app is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from intelligence import (
    detect_deceptive_pricing,
    calculate_review_intelligence,
    calculate_net_price_with_offers,
    predict_price_drop_probability,
    optimize_basket_arbitrage,
    compute_buying_verdict
)
from app import app
import database as db

class TestIntelligenceSuite(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_deceptive_pricing_authentic_deal(self):
        # Current price 300, MRP 350, 30-day history hovering around 340
        history = [340, 345, 338, 342, 350]
        res = detect_deceptive_pricing(300.0, 350.0, history)
        self.assertFalse(res["is_deceptive"])
        self.assertEqual(res["effective_deal_quality"], "GENUINE_DEAL")

    def test_deceptive_pricing_fake_sale(self):
        # Current price 340, claimed MRP inflated to 450 while past 30-day base was 300
        history = [300, 300, 305, 298, 300]
        res = detect_deceptive_pricing(340.0, 450.0, history)
        self.assertTrue(res["is_deceptive"])
        self.assertGreater(res["inflation_pct"], 10.0)
        self.assertIn("inflated", res["summary"].lower())

    def test_review_intelligence_scoring(self):
        res = calculate_review_intelligence(
            product_title="Sony WH-1000XM5 Wireless Headphones",
            category="Electronics",
            rating=4.7,
            reviews_count=2400
        )
        self.assertIn(res["trust_grade"], ["A", "B", "C", "D"])
        self.assertGreaterEqual(res["authenticity_score"], 50)
        self.assertIn("positive", res["sentiment_breakdown"])
        self.assertGreater(len(res["key_pros"]), 0)
        self.assertGreater(len(res["key_cons"]), 0)
        self.assertTrue(len(res["consensus_summary"]) > 10)

    def test_review_intelligence_deceptive_sale_penalty(self):
        # Deceptive fake sales must be penalized and cannot achieve Grade A or B
        res = calculate_review_intelligence(
            product_title="Sony WH-1000XM5 Wireless Headphones",
            category="Electronics",
            rating=4.7,
            reviews_count=2400,
            is_deceptive=True,
            inflation_pct=21.0
        )
        self.assertIn(res["trust_grade"], ["C", "D"])
        self.assertLessEqual(res["authenticity_score"], 74)
        self.assertIn("deceptive", res["consensus_summary"].lower())
        self.assertTrue(any("deceptive" in c.lower() or "inflated" in c.lower() for c in res["key_cons"]))

    def test_net_price_with_offers(self):
        res = calculate_net_price_with_offers(100.0, "USD")
        self.assertLessEqual(res["net_effective_price"], 100.0)
        self.assertGreaterEqual(res["total_extra_savings"], 0.0)
        self.assertTrue("coupon_text" in res)
        self.assertTrue("bank_name" in res)

    def test_price_drop_predictor(self):
        # Downward trending history
        history = [120, 115, 112, 110, 108, 105, 102]
        res = predict_price_drop_probability(100.0, history, volatility=1.5)
        self.assertGreaterEqual(res["probability_pct"], 0)
        self.assertLessEqual(res["probability_pct"], 100)
        self.assertIn(res["likelihood_tier"], ["HIGH", "MODERATE", "LOW"])
        self.assertLessEqual(res["predicted_channel_low"], res["predicted_channel_high"])

    def test_basket_arbitrage_logic(self):
        sample_items = [
            {"id": 1, "title": "Sony Headphones", "price": 328.0, "category": "Electronics"},
            {"id": 2, "title": "Anker Dock", "price": 45.0, "category": "Accessories"}
        ]
        result = optimize_basket_arbitrage(sample_items)
        self.assertEqual(result["item_count"], 2)
        self.assertGreater(result["optimal_total_cost"], 0)
        self.assertGreater(len(result["optimal_split"]), 0)
        self.assertGreater(len(result["single_store_totals"]), 0)

    def test_api_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("active_products", data)

    def test_api_basket_optimize(self):
        prods = db.get_all_products()
        if len(prods) >= 2:
            ids = [prods[0]["id"], prods[1]["id"]]
            res = self.client.post(
                "/api/basket/optimize",
                data=json.dumps({"product_ids": ids}),
                content_type="application/json"
            )
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["status"], "success")
            self.assertIn("result", data)
            self.assertEqual(data["result"]["item_count"], 2)

    def test_api_simulate_and_reset_price_drop(self):
        prods = db.get_all_products()
        if len(prods) > 0:
            target_id = prods[0]["id"]
            original_price = prods[0]["current_price"]

            # 1. Simulate Drop
            sim_res = self.client.post(f"/api/products/{target_id}/simulate-drop")
            self.assertEqual(sim_res.status_code, 200)
            sim_data = sim_res.get_json()
            self.assertEqual(sim_data["status"], "success")
            self.assertEqual(sim_data["drop_pct"], 30.0)
            self.assertLess(sim_data["new_price"], original_price)

            # 2. Reset Price
            reset_res = self.client.post(f"/api/products/{target_id}/reset-price")
            self.assertEqual(reset_res.status_code, 200)
            reset_data = reset_res.get_json()
            self.assertEqual(reset_data["status"], "success")
            self.assertGreater(reset_data["current_price"], sim_data["new_price"])

    def test_buying_verdict_buy_now(self):
        deceptive = {"is_deceptive": False, "status": "ALL_TIME_LOW", "real_discount_pct": 12.0, "baseline_price": 100.0}
        drop_pred = {"probability_pct": 15, "likelihood_tier": "LOW", "predicted_channel_low": 85.0}
        net_pricing = {"total_extra_savings": 10.0, "net_effective_price": 78.0}
        res = compute_buying_verdict(88.0, 100.0, deceptive, drop_pred, net_pricing, lowest_price=88.0, median_price=100.0)
        self.assertEqual(res["verdict"], "BUY_NOW")
        self.assertEqual(res["verdict_label"], "Buy Now")
        self.assertIn("all-time low", res["rationale"].lower())

    def test_buying_verdict_wait_and_save(self):
        # Fake sale scenario
        deceptive = {"is_deceptive": True, "status": "INFLATED_BASELINE", "inflation_pct": 25.0, "baseline_price": 100.0}
        drop_pred = {"probability_pct": 85, "likelihood_tier": "HIGH", "predicted_channel_low": 95.0}
        res = compute_buying_verdict(125.0, 150.0, deceptive, drop_pred, lowest_price=90.0, median_price=100.0)
        self.assertEqual(res["verdict"], "WAIT_AND_SAVE")
        self.assertEqual(res["verdict_label"], "Wait & Save")
        self.assertGreater(res["projected_savings"], 0.0)

    def test_aspect_sentiment_and_bot_risk(self):
        res = calculate_review_intelligence(
            product_title="Sony WH-1000XM5 Wireless Headphones",
            category="Electronics",
            rating=4.7,
            reviews_count=5000
        )
        self.assertIn("aspect_sentiment", res)
        self.assertGreater(len(res["aspect_sentiment"]), 0)
        self.assertIn("bot_risk", res)
        self.assertIn("tier", res["bot_risk"])
        self.assertEqual(res["bot_risk"]["tier"], "LOW")

    def test_api_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["database"]["connected"])
        self.assertGreaterEqual(data["database"]["tracked_products"], 1)


if __name__ == "__main__":
    unittest.main()
