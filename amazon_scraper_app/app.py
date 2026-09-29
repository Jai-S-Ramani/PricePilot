import os
import io
import csv
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for, Response
from werkzeug.security import generate_password_hash, check_password_hash

from database import (
    init_db, get_all_products, get_product_by_id, save_or_update_product,
    delete_product, update_target_price, get_price_history, CSV_PATH,
    create_user, get_user_by_email, get_user_by_id,
    get_alert_logs_for_user, toggle_user_auto_alerts, process_auto_alerts_for_user,
    get_portfolio_kpis, calculate_deal_score, update_user_notification_settings
)
from scraper import scrape_amazon_product, extract_asin, SAMPLE_PRODUCTS, search_amazon_products, fetch_amazon_suggestions
from notifier import build_alert_email_template, send_mail, send_discord_alert, dispatch_multi_channel_alert
from scheduler import price_scheduler
from competitor import get_competitor_prices

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "amazon_scraper_super_secret_luxe_key_2026")

# Ensure database tables exist and start background daemon scheduler
init_db()
price_scheduler.start()


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


# -----------------------------------------------------------------
# Authentication API Routes
# -----------------------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def api_auth_register():
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters"}), 400

    existing = get_user_by_email(email)
    if existing:
        return jsonify({"status": "error", "message": "An account with this email already exists"}), 400

    password_hash = generate_password_hash(password)
    user_id = create_user(email, password_hash, name)

    if not user_id:
        return jsonify({"status": "error", "message": "Could not create account"}), 500

    session["user_id"] = user_id
    session["user_email"] = email

    # Automatically process and dispatch alerts for eligible tracked products
    auto_triggered = process_auto_alerts_for_user(user_id)

    user = get_user_by_id(user_id)
    return jsonify({
        "status": "success",
        "message": "Account created successfully! Auto-alerts armed for your monitored products.",
        "user": user,
        "auto_alerts_triggered": len(auto_triggered),
        "triggered_alerts": auto_triggered
    })


@app.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    session["user_id"] = user["id"]
    session["user_email"] = user["email"]

    # Automatically check price drops and send automated alerts on sign in
    auto_triggered = process_auto_alerts_for_user(user["id"])

    user_profile = get_user_by_id(user["id"])
    return jsonify({
        "status": "success",
        "message": f"Welcome back, {user_profile.get('name') or user_profile['email']}!",
        "user": user_profile,
        "auto_alerts_triggered": len(auto_triggered),
        "triggered_alerts": auto_triggered
    })


@app.route("/api/auth/logout", methods=["POST"])
def api_auth_logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"})


@app.route("/api/auth/me", methods=["GET"])
def api_auth_me():
    user_id = session.get("user_id")
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return jsonify({"status": "success", "logged_in": True, "user": user})
    
    return jsonify({"status": "success", "logged_in": False, "user": None})


# -----------------------------------------------------------------
# Product Intelligence & Tracker API Routes
# -----------------------------------------------------------------

@app.route("/api/products", methods=["GET"])
def api_get_products():
    user_id = session.get("user_id")
    products = get_all_products(user_id)
    return jsonify({"status": "success", "products": products})


@app.route("/api/products/add", methods=["POST"])
def api_add_product():
    data = request.json or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"status": "error", "message": "Amazon URL or ASIN is required"}), 400

    scraped = scrape_amazon_product(url)

    # Preserve rich search metadata if available (from live search or fallback)
    if data.get("title") and (scraped.get("is_simulated") or str(scraped.get("title", "")).startswith("Amazon Item") or data.get("native_price")):
        scraped["title"] = data["title"]
        currency = data.get("currency", scraped.get("currency", "INR"))
        raw_price = float(data.get("price", 0))
        base_usd = float(data.get("base_usd", 0))

        if base_usd > 0:
            usd_price = base_usd
            native_p = float(data.get("native_price") or raw_price)
        elif currency == "INR":
            if raw_price > 500:
                usd_price = round(raw_price / 83.50, 2)
                native_p = raw_price
            else:
                usd_price = raw_price
                native_p = round(raw_price * 83.50, 2)
        else:
            usd_price = raw_price
            native_p = float(data.get("native_price") or raw_price)

        scraped["price"] = usd_price
        scraped["original_price"] = round(usd_price * 1.15, 2)
        scraped["native_price"] = native_p

        if data.get("image_url") and not str(data.get("image_url")).endswith("placeholder.svg"):
            scraped["image_url"] = data["image_url"]
        if data.get("category"):
            scraped["category"] = data["category"]
        if data.get("rating"):
            try:
                scraped["rating"] = float(data["rating"])
            except (ValueError, TypeError):
                pass
        scraped["region"] = data.get("region", "IN")
        scraped["currency"] = currency
        scraped["symbol"] = data.get("symbol", "₹" if currency == "INR" else "$")

    if "target_price" in data and data["target_price"]:
        try:
            raw_target = float(data["target_price"])
            p_price = scraped.get("price", 100)
            if (data.get("currency") == "INR" or scraped.get("currency") == "INR") and raw_target > (p_price * 5):
                scraped["target_price"] = round(raw_target / 83.50, 2)
            else:
                scraped["target_price"] = raw_target
        except ValueError:
            pass

    user_id = session.get("user_id")
    product_id = save_or_update_product(scraped, user_id=user_id)
    updated_product = get_product_by_id(product_id)
    return jsonify({"status": "success", "product": updated_product})


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id):
    delete_product(product_id)
    return jsonify({"status": "success", "message": "Product removed from tracking"})


@app.route("/api/products/<int:product_id>/target-price", methods=["POST"])
def api_update_target_price(product_id):
    data = request.json or {}
    target_price = data.get("target_price")
    if target_price is None:
        return jsonify({"status": "error", "message": "target_price is required"}), 400

    update_target_price(product_id, float(target_price))
    product = get_product_by_id(product_id)
    return jsonify({"status": "success", "product": product})


@app.route("/api/products/scrape-all", methods=["POST"])
def api_scrape_all():
    user_id = session.get("user_id")
    products = get_all_products(user_id)
    updated = []
    price_drops = []

    for p in products:
        scraped = scrape_amazon_product(p["url"])
        if p.get("target_price"):
            scraped["target_price"] = p["target_price"]
        
        # Check if price dropped below target
        if scraped["price"] <= p.get("target_price", 0):
            price_drops.append(scraped)

        save_or_update_product(scraped, user_id=user_id)
        updated.append(get_product_by_id(p["id"]))

    # If logged in user ran scrape-all, automatically process alerts for deals
    auto_triggered = []
    if user_id:
        auto_triggered = process_auto_alerts_for_user(user_id)

    return jsonify({
        "status": "success",
        "scraped_count": len(updated),
        "price_drops_detected": len(price_drops),
        "auto_alerts_triggered": len(auto_triggered),
        "products": updated
    })


@app.route("/api/alerts/activity", methods=["GET"])
def api_get_alert_activity():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required"}), 401
    
    logs = get_alert_logs_for_user(user_id, limit=30)
    user = get_user_by_id(user_id)
    return jsonify({
        "status": "success",
        "auto_alerts_enabled": bool(user.get("auto_alerts_enabled", 1)) if user else False,
        "logs": logs
    })


@app.route("/api/alerts/auto-toggle", methods=["POST"])
def api_toggle_auto_alerts():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required"}), 401

    data = request.json or {}
    enabled = data.get("enabled")
    if enabled is None:
        user = get_user_by_id(user_id)
        enabled = not bool(user.get("auto_alerts_enabled", 1))
    
    toggle_user_auto_alerts(user_id, bool(enabled))
    return jsonify({
        "status": "success",
        "auto_alerts_enabled": bool(enabled),
        "message": f"Automated price alerts {'activated' if enabled else 'paused'}."
    })


@app.route("/api/products/<int:product_id>/history", methods=["GET"])
def api_get_history(product_id):
    history = get_price_history(product_id)
    product = get_product_by_id(product_id)
    return jsonify({
        "status": "success",
        "product": product,
        "history": history
    })


@app.route("/api/products/<int:product_id>/competitors", methods=["GET"])
def api_get_product_competitors(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404

    comparison = get_competitor_prices(product)
    return jsonify({"status": "success", "comparison": comparison})


@app.route("/api/alerts/test", methods=["POST"])
def api_test_alert():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Authentication required. Please log in or create an account to access price drop alerts."
        }), 401

    data = request.json or {}
    user = get_user_by_id(user_id)
    default_email = user["email"] if user else (session.get("user_email") or "alex.analyst@example.com")
    email = data.get("email", default_email)
    product_id = data.get("product_id")

    if product_id:
        product = get_product_by_id(int(product_id))
    else:
        products = get_all_products(user_id)
        product = products[0] if products else None

    if not product:
        return jsonify({"status": "error", "message": "No product found for test alert"}), 400

    current_price = float(product["current_price"])
    target_price = float(product.get("target_price") or (current_price * 0.9))

    template = build_alert_email_template(
        product["title"],
        current_price,
        target_price,
        product["url"]
    )
    
    send_mail(email, template["subject"], template["body"])
    
    return jsonify({
        "status": "success",
        "email": email,
        "preview": template
    })


@app.route("/api/kpis", methods=["GET"])
def api_get_kpis():
    user_id = session.get("user_id")
    kpis = get_portfolio_kpis(user_id)
    return jsonify({"status": "success", "kpis": kpis})


@app.route("/api/scheduler/status", methods=["GET"])
def api_scheduler_status():
    status = price_scheduler.get_status()
    return jsonify({"status": "success", "scheduler": status})


@app.route("/api/scheduler/toggle", methods=["POST"])
def api_scheduler_toggle():
    status = price_scheduler.get_status()
    if status["running"]:
        price_scheduler.stop()
    else:
        price_scheduler.start()
    return jsonify({
        "status": "success",
        "message": "Scheduler toggled",
        "scheduler": price_scheduler.get_status()
    })


@app.route("/api/scheduler/interval", methods=["POST"])
def api_scheduler_interval():
    data = request.json or {}
    minutes = data.get("minutes", 30)
    try:
        minutes = int(minutes)
        price_scheduler.set_interval(minutes)
        return jsonify({
            "status": "success",
            "message": f"Interval set to {minutes} minutes",
            "scheduler": price_scheduler.get_status()
        })
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid minutes integer"}), 400


@app.route("/api/scheduler/trigger", methods=["POST"])
def api_scheduler_trigger():
    result = price_scheduler.trigger_now()
    return jsonify(result)


@app.route("/api/export/csv", methods=["GET"])
def api_export_csv():
    if CSV_PATH.exists():
        return send_file(CSV_PATH, as_attachment=True, download_name="AmazonWebScraperDataset.csv")
    return jsonify({"status": "error", "message": "CSV dataset file not found"}), 404


@app.route("/api/export/json", methods=["GET"])
def api_export_all_json():
    user_id = session.get("user_id")
    products = get_all_products(user_id)
    kpis = get_portfolio_kpis(user_id)

    export_items = []
    for p in products:
        h = get_price_history(p["id"])
        deal = calculate_deal_score(p["id"])
        export_items.append({
            "product": p,
            "deal_intelligence": deal,
            "history_count": len(h),
            "history": h
        })

    return jsonify({
        "status": "success",
        "timestamp": str(Path(CSV_PATH).stat().st_mtime) if CSV_PATH.exists() else None,
        "kpis": kpis,
        "total_products": len(products),
        "products": export_items
    })


@app.route("/api/products/<int:product_id>/refresh", methods=["POST"])
def api_refresh_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404

    scraped = scrape_amazon_product(product["url"])
    if product.get("target_price"):
        scraped["target_price"] = product["target_price"]

    user_id = session.get("user_id")
    save_or_update_product(scraped, user_id=user_id or product.get("user_id"))
    updated = get_product_by_id(product_id)
    return jsonify({
        "status": "success",
        "message": f"Successfully refreshed live price for {updated['title'][:40]}...",
        "product": updated
    })


@app.route("/api/products/<int:product_id>/export/csv", methods=["GET"])
def api_export_product_history_csv(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404

    history = get_price_history(product_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "ASIN", "Date", "Timestamp", "Price_USD", "Current_Price_USD", "Target_Price_USD", "URL"])
    for h in history:
        writer.writerow([
            product["title"],
            product["asin"],
            h.get("date"),
            h.get("timestamp"),
            h.get("price"),
            product.get("current_price"),
            product.get("target_price"),
            product.get("url")
        ])
    filename = f"PriceHistory_{product['asin']}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/api/products/<int:product_id>/export/json", methods=["GET"])
def api_export_product_history_json(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404

    history = get_price_history(product_id)
    deal = calculate_deal_score(product_id)
    return jsonify({
        "status": "success",
        "product": product,
        "deal_intelligence": deal,
        "data_points": len(history),
        "history": history
    })


@app.route("/api/search/suggestions", methods=["GET"])
def api_search_suggestions():
    query = request.args.get("q", "").strip()
    region = request.args.get("region", "IN").strip().upper()
    if not query:
        return jsonify({"status": "success", "query": "", "suggestions": []})

    suggestions = fetch_amazon_suggestions(query, region=region)
    return jsonify({
        "status": "success",
        "query": query,
        "region": region,
        "suggestions": suggestions
    })


@app.route("/api/search", methods=["GET"])
def api_search():
    query = request.args.get("q", "").strip()
    region = request.args.get("region", "IN").strip().upper()
    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        limit = 5

    if not query:
        return jsonify({"status": "error", "message": "Search query parameter 'q' is required", "results": []}), 400

    results = search_amazon_products(query, region=region, limit=limit)
    return jsonify({
        "status": "success",
        "query": query,
        "region": region,
        "count": len(results),
        "results": results
    })


@app.route("/api/products/<int:product_id>/deal-analysis", methods=["GET"])
def api_product_deal_analysis(product_id):
    analysis = calculate_deal_score(product_id)
    if not analysis:
        return jsonify({"status": "error", "message": "Product not found"}), 404
    return jsonify({"status": "success", "analysis": analysis})


@app.route("/api/notifications/settings", methods=["POST"])
def api_notification_settings():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required"}), 401

    data = request.json or {}
    discord_webhook = data.get("discord_webhook", "").strip() or None
    telegram_chat_id = data.get("telegram_chat_id", "").strip() or None

    user = update_user_notification_settings(user_id, discord_webhook, telegram_chat_id)
    return jsonify({
        "status": "success",
        "message": "Notification channels updated successfully!",
        "user": user
    })


@app.route("/api/notifications/test-discord", methods=["POST"])
def api_test_discord():
    data = request.json or {}
    webhook_url = data.get("webhook_url", "").strip()

    if not webhook_url:
        user_id = session.get("user_id")
        if user_id:
            user = get_user_by_id(user_id)
            webhook_url = user.get("discord_webhook", "") if user else ""

    if not webhook_url:
        return jsonify({"status": "error", "message": "Discord Webhook URL is required"}), 400

    sent = send_discord_alert(
        webhook_url=webhook_url,
        product_title="Test Product - Price Tracker Alert Verified",
        current_price=19.99,
        target_price=24.99,
        product_url="https://www.amazon.com",
        savings=5.00
    )
    return jsonify({
        "status": "success" if sent else "error",
        "message": "Discord test alert sent successfully!" if sent else "Failed to send Discord alert",
        "simulated": "discord.com/api/webhooks" not in webhook_url
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
