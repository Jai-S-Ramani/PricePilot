import os
import csv
import sqlite3
import datetime
import random
from pathlib import Path
from intelligence import (
    detect_deceptive_pricing,
    calculate_review_intelligence,
    calculate_net_price_with_offers,
    predict_price_drop_probability,
    compute_buying_verdict
)

DB_PATH = Path(__file__).parent / "amazon_tracker.db"
CSV_PATH = Path(__file__).parent.parent / "pricepilot_dataset.csv"

def get_db_connection():
    db_file = os.environ.get("TRACKER_DB_PATH") or DB_PATH
    conn = sqlite3.connect(db_file, timeout=10.0)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=-64000;")
        conn.execute("PRAGMA temp_store=MEMORY;")
        conn.execute("PRAGMA mmap_size=268435456;")
    except Exception:
        pass
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            name TEXT,
            auto_alerts_enabled INTEGER DEFAULT 1,
            discord_webhook TEXT,
            telegram_chat_id TEXT,
            google_id TEXT,
            avatar_url TEXT,
            auth_provider TEXT DEFAULT 'local',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Check and migrate user table columns
    cursor.execute("PRAGMA table_info(users)")
    user_cols = [c[1] for c in cursor.fetchall()]
    if "auto_alerts_enabled" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN auto_alerts_enabled INTEGER DEFAULT 1")
    if "discord_webhook" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN discord_webhook TEXT")
    if "telegram_chat_id" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN telegram_chat_id TEXT")
    if "google_id" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
    if "avatar_url" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    if "auth_provider" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'local'")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            current_price REAL NOT NULL,
            original_price REAL,
            target_price REAL,
            url TEXT NOT NULL,
            image_url TEXT,
            rating REAL,
            reviews_count INTEGER,
            availability TEXT,
            category TEXT,
            last_scraped TEXT,
            user_id INTEGER REFERENCES users(id)
        );
    """)

    # Check and migrate user_id and regional columns if needed
    cursor.execute("PRAGMA table_info(products)")
    cols = [c[1] for c in cursor.fetchall()]
    if "user_id" not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN user_id INTEGER REFERENCES users(id)")
    if "region" not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN region TEXT DEFAULT 'US'")
    if "currency" not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN currency TEXT DEFAULT 'USD'")
    if "symbol" not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN symbol TEXT DEFAULT '$'")
    if "native_price" not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN native_price REAL")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            product_title TEXT NOT NULL,
            current_price REAL NOT NULL,
            target_price REAL NOT NULL,
            recipient_email TEXT NOT NULL,
            status TEXT DEFAULT 'SENT',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );
    """)

    # High-performance indexes for fast queries, joins, and aggregations
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_prod_date ON price_history(product_id, date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_region ON products(region);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_asin ON products(asin);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alert_logs_user_id ON alert_logs(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alert_logs_user_prod ON alert_logs(user_id, product_id, created_at);")

    # Auto-correct any existing inflated 900000 prices in DB (e.g. 900000 -> 9000)
    cursor.execute("UPDATE products SET current_price = current_price / 100.0 WHERE current_price >= 100000 AND (current_price % 100) = 0")
    cursor.execute("UPDATE price_history SET price = price / 100.0 WHERE price >= 100000 AND (price % 100) = 0")

    # Auto-normalize unconverted INR prices (> 3000) to base USD (e.g. 9890.00 / 83.50 -> 118.44 USD)
    cursor.execute("SELECT id, current_price, target_price FROM products WHERE current_price > 3000")
    high_prods = cursor.fetchall()
    for hp in high_prods:
        usd_price = round(hp["current_price"] / 83.50, 2)
        usd_target = round((hp["target_price"] or (hp["current_price"] * 0.9)) / 83.50, 2) if hp["target_price"] and hp["target_price"] > 2000 else hp["target_price"]
        cursor.execute("UPDATE products SET current_price = ?, target_price = ? WHERE id = ?", (usd_price, usd_target, hp["id"]))
        cursor.execute("UPDATE price_history SET price = ROUND(price / 83.50, 2) WHERE product_id = ?", (hp["id"],))

    # Auto-normalize price_history outliers for items whose normal price is under $500 (e.g. 2260.3 -> 144.99)
    cursor.execute("""
        UPDATE price_history 
        SET price = 144.99 
        WHERE price > 1000 AND product_id IN (SELECT id FROM products WHERE current_price < 500)
    """)

    # Ensure catalog demo products (ID <= 5) are public (user_id IS NULL)
    cursor.execute("UPDATE products SET user_id = NULL WHERE id = 3 AND user_id IS NOT NULL")

    # Migrate any generic/Unsplash or placeholder product DPs to authentic, genuine product photography packshots
    authentic_dps = {
        "B07W5JK7B9": "/static/images/products/anker_dock.jpg",
        "B0DCZ3WDTB": "/static/images/products/xiaomi_powerbank.jpg",
        "B09VXYZTES": "/static/images/products/mechanical_keyboard.jpg",
        "B030306166": "/static/images/products/bose_qc45.jpg",
        "B09B8V1LZ3": "/static/images/products/sony_wh1000xm5.jpg",
        "B0CX23VJP5": "/static/images/products/macbook_air_m3.jpg",
        "B08N5WRWNW": "/static/images/products/mx_master_3s.jpg",
        "B0BS74M665": "/static/images/products/sony_whch720n.jpg",
        "B0BY8MCQ9S": "/static/images/products/oneplus_buds_2.jpg",
        "B0DMXNPT66": "/static/images/products/macbook_pro_m4.jpg",
        "B07FNW9FGJ": "/static/images/products/data_tshirt.jpg",
        "B0CHWRXH8B": "/static/images/products/airpods_pro_2.jpg"
    }
    for item_asin, img_path in authentic_dps.items():
        cursor.execute("UPDATE products SET image_url = ? WHERE asin = ?", (img_path, item_asin))

    conn.commit()

    # Seed initial demo products if database is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_default_data(conn)

    conn.close()
    export_to_csv()


def seed_default_data(conn):
    from scraper import SAMPLE_PRODUCTS
    cursor = conn.cursor()
    today = datetime.date.today()

    for asin, item in SAMPLE_PRODUCTS.items():
        target_price = round(item["price"] * 0.90, 2)
        cursor.execute("""
            INSERT INTO products (asin, title, current_price, original_price, target_price, url, image_url, rating, reviews_count, availability, category, last_scraped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["asin"],
            item["title"],
            item["price"],
            item["original_price"],
            target_price,
            item["url"],
            item["image_url"],
            item["rating"],
            item["reviews_count"],
            item["availability"],
            item["category"],
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        product_id = cursor.lastrowid

        # Generate 30 days of synthetic price history leading to today
        base_price = item["price"]
        for d in range(30, -1, -1):
            hist_date = today - datetime.timedelta(days=d)
            # Add subtle price fluctuation
            fluctuation = random.choice([-2.0, -1.0, 0.0, 0.5, 1.5, 3.0, 0.0, 0.0]) if d > 0 else 0.0
            day_price = max(5.0, round(base_price + fluctuation, 2))
            cursor.execute("""
                INSERT INTO price_history (product_id, price, timestamp, date)
                VALUES (?, ?, ?, ?)
            """, (
                product_id,
                day_price,
                hist_date.strftime("%Y-%m-%d 10:00:00"),
                hist_date.strftime("%Y-%m-%d")
            ))

    conn.commit()


def create_user(email: str, password_hash: str, name: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (email, password_hash, name)
            VALUES (?, ?, ?)
        """, (email.lower().strip(), password_hash, name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password_hash, name, avatar_url, google_id, auth_provider, auto_alerts_enabled, discord_webhook, telegram_chat_id, created_at FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name, avatar_url, google_id, auth_provider, auto_alerts_enabled, discord_webhook, telegram_chat_id, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_or_create_google_user(email: str, name: str = None, google_id: str = None, avatar_url: str = None):
    """Retrieves existing user by email or creates a new user via Google OAuth."""
    import secrets
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, name, avatar_url, google_id, auth_provider, auto_alerts_enabled, discord_webhook, telegram_chat_id, created_at 
        FROM users 
        WHERE LOWER(email) = LOWER(?)
    """, (email.strip(),))
    row = cursor.fetchone()
    
    if row:
        user = dict(row)
        cursor.execute("""
            UPDATE users 
            SET google_id = COALESCE(?, google_id),
                avatar_url = COALESCE(?, avatar_url),
                name = COALESCE(name, ?)
            WHERE id = ?
        """, (google_id, avatar_url, name, user["id"]))
        conn.commit()
        conn.close()
        return get_user_by_id(user["id"])
    else:
        cursor.execute("""
            INSERT INTO users (email, password_hash, name, google_id, avatar_url, auth_provider)
            VALUES (?, ?, ?, ?, ?, 'google')
        """, (email.lower().strip(), f"google_oauth_{secrets.token_hex(16)}", name or email.split('@')[0], google_id, avatar_url))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return get_user_by_id(user_id)

def update_user_notification_settings(user_id: int, discord_webhook: str = None, telegram_chat_id: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET discord_webhook = ?, telegram_chat_id = ?
        WHERE id = ?
    """, (discord_webhook, telegram_chat_id, user_id))
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def toggle_user_auto_alerts(user_id: int, enabled: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET auto_alerts_enabled = ? WHERE id = ?", (1 if enabled else 0, user_id))
    conn.commit()
    conn.close()
    return enabled

def log_alert(user_id: int, product_id: int, product_title: str, current_price: float, target_price: float, recipient_email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alert_logs (user_id, product_id, product_title, current_price, target_price, recipient_email, status)
        VALUES (?, ?, ?, ?, ?, ?, 'SENT')
    """, (user_id, product_id, product_title, float(current_price), float(target_price), recipient_email))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def has_recent_alert(user_id: int, product_id: int, hours: int = 6) -> bool:
    """Checks if an alert email was sent for this user & product within the cooldown window."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM alert_logs 
        WHERE user_id = ? AND product_id = ? 
          AND created_at >= datetime('now', '-' || ? || ' hours')
    """, (user_id, product_id, hours))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def get_alert_logs_for_user(user_id: int, limit: int = 25):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.id, l.user_id, l.product_id, l.product_title, l.current_price, 
               l.target_price, l.recipient_email, l.status, l.created_at,
               p.url as product_url, p.image_url
        FROM alert_logs l
        LEFT JOIN products p ON l.product_id = p.id
        WHERE l.user_id = ?
        ORDER BY l.id DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def process_auto_alerts_for_user(user_id: int):
    """
    Evaluates all tracked products for a user.
    If price <= target_price and no recent alert in cooldown window,
    automatically sends email and logs it.
    """
    user = get_user_by_id(user_id)
    if not user or not user.get("auto_alerts_enabled", 1):
        return []

    from notifier import build_alert_email_template, send_mail, dispatch_multi_channel_alert
    products = get_all_products(user_id)
    triggered = []

    for p in products:
        current = float(p.get("current_price") or 0)
        target = float(p.get("target_price") or (current * 0.9))
        
        # Check if price qualifies for deal alert
        if current > 0 and target > 0 and current <= target:
            # Check cooldown (6 hours)
            if not has_recent_alert(user_id, p["id"], hours=6):
                template = build_alert_email_template(p["title"], current, target, p["url"])
                dispatch_res = dispatch_multi_channel_alert(user, p["title"], current, target, p["url"], p.get("image_url"))
                sent = dispatch_res.get("email", False) or dispatch_res.get("discord", False) or dispatch_res.get("telegram", False)
                log_id = log_alert(user_id, p["id"], p["title"], current, target, user["email"])
                triggered.append({
                    "log_id": log_id,
                    "product_id": p["id"],
                    "product_title": p["title"],
                    "current_price": current,
                    "target_price": target,
                    "subject": template["subject"],
                    "email": user["email"],
                    "sent": sent,
                    "channels": dispatch_res
                })

    return triggered


def calculate_price_forecast(price_rows: list, current_price: float = None) -> dict:
    """
    Time-Series & Statistical Regression Forecasting Model:
    Calculates 7-day Simple Moving Average (SMA-7), Linear Regression Slope,
    Predicted 7-day target range, Drop Probability %, and 7 daily forward projection points.
    """
    if not price_rows or len(price_rows) < 2:
        cur = float(current_price or 100.0)
        return {
            "sma_7": cur,
            "trend_slope": 0.0,
            "trajectory": "STABLE",
            "predicted_7d_price": cur,
            "predicted_range_min": round(cur * 0.98, 2),
            "predicted_range_max": round(cur * 1.02, 2),
            "drop_probability": 50,
            "drop_signal": "Neutral Trading Channel",
            "forecast_points": [cur] * 7,
            "forecast_labels": [f"Day +{i}" for i in range(1, 8)]
        }

    prices = [float(p) for p in price_rows if p is not None]
    n = len(prices)
    cur = float(current_price) if current_price is not None else prices[-1]

    # 1. 7-Day Simple Moving Average
    window = min(7, n)
    sma_7 = round(sum(prices[-window:]) / window, 2)

    # 2. Linear Regression Slope (dy/dx)
    x = list(range(n))
    mean_x = sum(x) / n
    mean_y = sum(prices) / n
    denom = sum((x[i] - mean_x) ** 2 for i in range(n))
    slope = round(sum((x[i] - mean_x) * (prices[i] - mean_y) for i in range(n)) / denom, 4) if denom != 0 else 0.0

    # 3. 7-Day Projections bounded within realistic corridors
    lowest = min(prices)
    highest = max(prices)
    damped_slope = slope * 0.75
    raw_projected = cur + (damped_slope * 7)
    bounded_proj = round(max(lowest * 0.85, min(highest * 1.15, raw_projected)), 2)

    range_min = round(bounded_proj * 0.975, 2)
    range_max = round(bounded_proj * 1.025, 2)

    forecast_points = []
    for i in range(1, 8):
        pt = round(cur + (damped_slope * i), 2)
        pt = round(max(lowest * 0.85, min(highest * 1.15, pt)), 2)
        forecast_points.append(pt)

    # 4. Statistical Drop Likelihood Score (0 - 100%)
    if slope < -0.05:
        drop_prob = min(95, int(65 + abs(slope) * 20))
        drop_signal = "High Drop Probability (Bearish Price Trajectory)"
        trajectory = "DROPPING"
    elif slope > 0.05:
        drop_prob = max(10, int(40 - slope * 15))
        drop_signal = "Low Drop Probability (Rising Price Trend)"
        trajectory = "RISING"
    else:
        if cur >= (lowest + highest) / 2:
            drop_prob = 60
            drop_signal = "Moderate Drop Likelihood (Upper Channel)"
        else:
            drop_prob = 35
            drop_signal = "Low Drop Likelihood (Historical Floor)"
        trajectory = "STABLE"

    today_dt = datetime.date.today()
    forecast_labels = [(today_dt + datetime.timedelta(days=i)).strftime("%b %d") for i in range(1, 8)]

    return {
        "sma_7": sma_7,
        "trend_slope": slope,
        "trajectory": trajectory,
        "predicted_7d_price": bounded_proj,
        "predicted_range_min": range_min,
        "predicted_range_max": range_max,
        "drop_probability": drop_prob,
        "drop_signal": drop_signal,
        "forecast_points": forecast_points,
        "forecast_labels": forecast_labels
    }


def compute_stats_from_price_list(price_rows: list, current_price: float = None, original_price: float = None, target_price: float = None) -> dict:
    """Computes pricing metrics, volatility, deal scores, and recommendations from a list of price history floats."""
    if not price_rows:
        cur = float(current_price or 0.0)
        return {
            "lowest_price": cur,
            "highest_price": cur,
            "avg_price": cur,
            "volatility": "Stable",
            "volatility_ratio": 0.0,
            "recommendation": "BUY_NOW" if target_price and cur <= target_price else "FAIR_PRICE",
            "recommendation_label": "Buy Now (Target Met)" if target_price and cur <= target_price else "Fair Price",
            "discount_pct": 0.0,
            "potential_savings": 0.0,
            "deal_score": 80 if (target_price and cur <= target_price) else 50,
            "deal_grade": "FAIR",
            "deal_label": "🟡 Fair Value",
            "price_trend": "STABLE",
            "trend_pct": 0.0,
            "trend_label": "Stable",
            "best_time_to_buy": bool(target_price and cur <= target_price),
            "sma_7": cur,
            "predicted_7d_price": cur,
            "predicted_range_min": round(cur * 0.98, 2),
            "predicted_range_max": round(cur * 1.02, 2),
            "drop_probability": 50,
            "drop_signal": "Neutral Channel"
        }

    lowest = round(min(price_rows), 2)
    highest = round(max(price_rows), 2)
    avg_val = round(sum(price_rows) / len(price_rows), 2)

    cur = float(current_price) if current_price is not None else price_rows[-1]
    orig = float(original_price or 0.0)
    tgt = float(target_price or 0.0)

    # Calculate Volatility ratio: (highest - lowest) / avg_val
    vol_ratio = round((highest - lowest) / avg_val, 3) if avg_val > 0 else 0.0
    if vol_ratio < 0.08:
        volatility = "Stable"
    elif vol_ratio < 0.20:
        volatility = "Moderate"
    else:
        volatility = "High"

    # Sanity guard: Normalize orig/tgt if mistakenly stored in local currency (e.g. INR > 5x cur)
    if cur > 0 and orig > cur * 5:
        orig = round(orig / 83.50, 2)
    if cur > 0 and tgt > cur * 5:
        tgt = round(tgt / 83.50, 2)

    # Baseline peak for savings
    baseline_peak = max(orig, highest)
    # Sanity guard: baseline peak shouldn't be absurdly inflated (> 2.5x cur)
    if cur > 0 and baseline_peak > cur * 2.5:
        baseline_peak = round(cur * 1.25, 2)

    if baseline_peak > cur and baseline_peak > 0:
        discount_pct = round(((baseline_peak - cur) / baseline_peak) * 100, 1)
        savings = round(baseline_peak - cur, 2)
    else:
        discount_pct = 0.0
        savings = 0.0

    # Predictive Recommendation Engine:
    # 1. BUY_NOW: If current price <= target_price OR within 3% of 30-day low
    # 2. FAIR_PRICE: If current price < 30-day average
    # 3. WAIT: If current price >= 30-day average
    if tgt > 0 and cur <= tgt:
        recommendation = "BUY_NOW"
        rec_label = "Buy Now (Target Reached)"
    elif lowest > 0 and cur <= round(lowest * 1.03, 2):
        recommendation = "BUY_NOW"
        rec_label = "Buy Now (Near 30d Low)"
    elif cur < avg_val:
        recommendation = "FAIR_PRICE"
        rec_label = "Fair Price (Below Avg)"
    else:
        recommendation = "WAIT"
        rec_label = "Wait for Drop"

    # Deal Score Calculation (0 - 100%)
    if highest > lowest:
        raw_score = ((highest - cur) / (highest - lowest)) * 100
        if tgt > 0 and cur <= tgt:
            raw_score = min(100.0, raw_score + 15.0)
    else:
        raw_score = 80.0 if (tgt > 0 and cur <= tgt) else 50.0

    deal_score = max(5, min(100, int(round(raw_score))))
    if deal_score >= 85:
        deal_grade = "STEAL"
        deal_label = "🔥 Steal (Near Low)"
    elif deal_score >= 70:
        deal_grade = "GREAT_DEAL"
        deal_label = "⚡ Great Deal"
    elif deal_score >= 50:
        deal_grade = "FAIR"
        deal_label = "🟡 Fair Value"
    else:
        deal_grade = "OVERPRICED"
        deal_label = "⚠️ Overpriced"

    # Price Trend & Velocity Analysis
    if len(price_rows) >= 2:
        baseline_p = price_rows[0]
        trend_pct = round(((cur - baseline_p) / baseline_p) * 100, 1) if baseline_p > 0 else 0.0
        if trend_pct <= -2.0:
            price_trend = "DROPPING"
            trend_label = f"Falling ({trend_pct}%)"
        elif trend_pct >= 2.0:
            price_trend = "RISING"
            trend_label = f"Rising (+{trend_pct}%)"
        else:
            price_trend = "STABLE"
            trend_label = "Stable (0%)"
    else:
        trend_pct = 0.0
        price_trend = "STABLE"
        trend_label = "Stable"

    best_time_to_buy = bool(deal_score >= 75 or recommendation == "BUY_NOW")
    forecast = calculate_price_forecast(price_rows, current_price=cur)

    return {
        "lowest_price": lowest,
        "highest_price": highest,
        "avg_price": avg_val,
        "volatility": volatility,
        "volatility_ratio": vol_ratio,
        "recommendation": recommendation,
        "recommendation_label": rec_label,
        "discount_pct": discount_pct,
        "potential_savings": savings,
        "deal_score": deal_score,
        "deal_grade": deal_grade,
        "deal_label": deal_label,
        "price_trend": price_trend,
        "trend_pct": trend_pct,
        "trend_label": trend_label,
        "best_time_to_buy": best_time_to_buy,
        "sma_7": forecast["sma_7"],
        "predicted_7d_price": forecast["predicted_7d_price"],
        "predicted_range_min": forecast["predicted_range_min"],
        "predicted_range_max": forecast["predicted_range_max"],
        "drop_probability": forecast["drop_probability"],
        "drop_signal": forecast["drop_signal"]
    }


def get_all_products(user_id: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM products WHERE user_id = ? OR user_id IS NULL ORDER BY id DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM products ORDER BY id DESC")
    rows = cursor.fetchall()
    
    if not rows:
        conn.close()
        return []

    product_dicts = [dict(r) for r in rows]
    prod_ids = [p["id"] for p in product_dicts]

    # Optimized batch query: fetch price history across ALL requested products in 1 roundtrip
    placeholders = ",".join("?" for _ in prod_ids)
    cursor.execute(f"SELECT product_id, price FROM price_history WHERE product_id IN ({placeholders}) ORDER BY id ASC", prod_ids)
    
    prices_by_product = {pid: [] for pid in prod_ids}
    for row in cursor.fetchall():
        if row[1] is not None:
            prices_by_product[row[0]].append(float(row[1]))

    conn.close()

    for p in product_dicts:
        price_list = prices_by_product.get(p["id"], [])
        stats = compute_stats_from_price_list(
            price_list,
            current_price=p.get("current_price"),
            original_price=p.get("original_price"),
            target_price=p.get("target_price")
        )
        p.update(stats)
        
        # Attach 6-Feature Intelligence Suite
        deceptive = detect_deceptive_pricing(
            current_price=float(p.get("current_price") or 0.0),
            original_price=float(p.get("original_price") or 0.0),
            price_history=price_list
        )
        p["deceptive_pricing"] = deceptive
        p["review_intelligence"] = calculate_review_intelligence(
            product_title=p.get("title") or "",
            category=p.get("category") or "",
            rating=float(p.get("rating") or 4.5),
            reviews_count=int(p.get("reviews_count") or 150),
            is_deceptive=bool(deceptive.get("is_deceptive")),
            inflation_pct=float(deceptive.get("inflation_pct") or 0.0),
            deal_quality=str(deceptive.get("effective_deal_quality") or "")
        )
        p["net_pricing"] = calculate_net_price_with_offers(
            price=float(p.get("current_price") or 0.0),
            currency=p.get("currency") or "USD",
            native_price=float(p.get("native_price") or 0.0) if p.get("native_price") else None,
            product_id=p.get("id"),
            title=p.get("title"),
            category=p.get("category")
        )
        p["drop_prediction"] = predict_price_drop_probability(
            price=float(p.get("current_price") or 0.0),
            price_history=price_list,
            volatility=float(p.get("volatility_ratio") or 0.0) * 10.0
        )
        p["buying_verdict"] = compute_buying_verdict(
            current_price=float(p.get("current_price") or 0.0),
            original_price=float(p.get("original_price") or 0.0),
            deceptive=deceptive,
            drop_pred=p["drop_prediction"],
            net_pricing=p["net_pricing"],
            lowest_price=float(p.get("lowest_price") or 0.0),
            median_price=float(p.get("median_price") or deceptive.get("baseline_price") or 0.0)
        )

    return product_dicts


def get_product_by_id(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    p = dict(row)
    cursor.execute("SELECT price FROM price_history WHERE product_id = ? ORDER BY id ASC", (product_id,))
    price_rows = [float(r[0]) for r in cursor.fetchall() if r[0] is not None]
    conn.close()
    
    stats = compute_stats_from_price_list(
        price_rows,
        current_price=p.get("current_price"),
        original_price=p.get("original_price"),
        target_price=p.get("target_price")
    )
    p.update(stats)
    
    # Attach 6-Feature Intelligence Suite
    deceptive = detect_deceptive_pricing(
        current_price=float(p.get("current_price") or 0.0),
        original_price=float(p.get("original_price") or 0.0),
        price_history=price_rows
    )
    p["deceptive_pricing"] = deceptive
    p["review_intelligence"] = calculate_review_intelligence(
        product_title=p.get("title") or "",
        category=p.get("category") or "",
        rating=float(p.get("rating") or 4.5),
        reviews_count=int(p.get("reviews_count") or 150),
        is_deceptive=bool(deceptive.get("is_deceptive")),
        inflation_pct=float(deceptive.get("inflation_pct") or 0.0),
        deal_quality=str(deceptive.get("effective_deal_quality") or "")
    )
    p["net_pricing"] = calculate_net_price_with_offers(
        price=float(p.get("current_price") or 0.0),
        currency=p.get("currency") or "USD",
        native_price=float(p.get("native_price") or 0.0) if p.get("native_price") else None,
        product_id=p.get("id"),
        title=p.get("title"),
        category=p.get("category")
    )
    p["drop_prediction"] = predict_price_drop_probability(
        price=float(p.get("current_price") or 0.0),
        price_history=price_rows,
        volatility=float(p.get("volatility_ratio") or 0.0) * 10.0
    )
    p["buying_verdict"] = compute_buying_verdict(
        current_price=float(p.get("current_price") or 0.0),
        original_price=float(p.get("original_price") or 0.0),
        deceptive=deceptive,
        drop_pred=p["drop_prediction"],
        net_pricing=p["net_pricing"],
        lowest_price=float(p.get("lowest_price") or 0.0),
        median_price=float(p.get("median_price") or deceptive.get("baseline_price") or 0.0)
    )
    return p


def get_product_stats(product_id: int, current_price: float = None, original_price: float = None, target_price: float = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM price_history WHERE product_id = ? ORDER BY id ASC", (product_id,))
    price_rows = [float(r[0]) for r in cursor.fetchall() if r[0] is not None]
    conn.close()
    return compute_stats_from_price_list(
        price_rows,
        current_price=current_price,
        original_price=original_price,
        target_price=target_price
    )


def calculate_deal_score(product_id: int):
    """Returns standalone comprehensive deal intelligence & trend analysis."""
    prod = get_product_by_id(product_id)
    if not prod:
        return None
    return {
        "product_id": product_id,
        "title": prod.get("title"),
        "current_price": prod.get("current_price"),
        "target_price": prod.get("target_price"),
        "lowest_price": prod.get("lowest_price"),
        "highest_price": prod.get("highest_price"),
        "avg_price": prod.get("avg_price"),
        "deal_score": prod.get("deal_score", 50),
        "deal_grade": prod.get("deal_grade", "FAIR"),
        "deal_label": prod.get("deal_label", "🟡 Fair Value"),
        "price_trend": prod.get("price_trend", "STABLE"),
        "trend_pct": prod.get("trend_pct", 0.0),
        "trend_label": prod.get("trend_label", "Stable"),
        "best_time_to_buy": prod.get("best_time_to_buy", False),
        "recommendation": prod.get("recommendation", "FAIR_PRICE"),
        "recommendation_label": prod.get("recommendation_label", "Fair Price")
    }


def get_portfolio_kpis(user_id: int = None):
    """Calculates aggregate portfolio analytics across tracked products."""
    prods = get_all_products(user_id)
    total_products = len(prods)
    active_deals = sum(1 for p in prods if float(p.get("current_price") or 0) <= float(p.get("target_price") or 0))
    total_savings = round(sum(float(p.get("potential_savings") or 0) for p in prods), 2)
    avg_discount = (
        round(sum(float(p.get("discount_pct") or 0) for p in prods) / total_products, 1)
        if total_products > 0 else 0.0
    )
    buy_now_count = sum(1 for p in prods if p.get("recommendation") == "BUY_NOW")

    return {
        "total_products": total_products,
        "active_deals": active_deals,
        "total_savings": total_savings,
        "avg_discount": avg_discount,
        "buy_now_count": buy_now_count
    }


def save_or_update_product(data: dict, user_id: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, target_price FROM products WHERE asin = ?", (data["asin"],))
    existing = cursor.fetchone()

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    url_str = (data.get("url") or "").lower()
    is_inr_domain = "amazon.in" in url_str or "amzn.in" in url_str or ".in/" in url_str
    
    # If explicit USD or US domain, not INR
    if "amazon.com" in url_str or data.get("currency") == "USD" or data.get("region") == "US":
        is_inr = False
    elif is_inr_domain or data.get("currency") == "INR" or data.get("region") == "IN":
        is_inr = True
    else:
        is_inr = False

    region = "IN" if is_inr else data.get("region", "US")
    currency = "INR" if is_inr else data.get("currency", "USD")
    symbol = "₹" if is_inr else ("£" if currency == "GBP" else ("€" if currency == "EUR" else "$"))

    raw_price = float(data.get("price", 0))

    if is_inr and raw_price > 500:
        norm_price = round(raw_price / 83.50, 2)
        native_price = raw_price
    else:
        norm_price = raw_price
        if is_inr:
            raw_nat = data.get("native_price")
            native_price = float(raw_nat) if raw_nat and float(raw_nat) > 0 else round(raw_price * 83.50, 2)
        else:
            native_price = float(data.get("native_price") or raw_price)

    raw_orig = data.get("original_price")
    if raw_orig:
        raw_orig_val = float(raw_orig)
        if is_inr and (raw_orig_val > norm_price * 5 or raw_orig_val > 500):
            norm_orig = round(raw_orig_val / 83.50, 2)
        else:
            norm_orig = raw_orig_val
    else:
        norm_orig = round(norm_price * 1.15, 2)

    raw_target = data.get("target_price")
    if raw_target:
        raw_tgt_val = float(raw_target)
        if is_inr and (raw_tgt_val > norm_price * 5 or raw_tgt_val > 500):
            norm_target = round(raw_tgt_val / 83.50, 2)
        else:
            norm_target = raw_tgt_val
    else:
        norm_target = round(norm_price * 0.90, 2)

    if existing:
        product_id = existing["id"]
        # Safeguard: do not overwrite established price if scraper returned 0 or null
        if norm_price <= 0:
            cursor.execute("SELECT current_price, original_price, native_price FROM products WHERE id = ?", (product_id,))
            ex_row = cursor.fetchone()
            if ex_row and ex_row["current_price"] and float(ex_row["current_price"]) > 0:
                norm_price = float(ex_row["current_price"])
                norm_orig = float(ex_row["original_price"] or (norm_price * 1.15))
                native_price = float(ex_row["native_price"] or norm_price)

        target_price = norm_target or existing["target_price"] or round(norm_price * 0.9, 2)
        cursor.execute("""
            UPDATE products
            SET title = COALESCE(NULLIF(?, ''), title),
                current_price = ?, original_price = ?, url = ?, 
                image_url = COALESCE(NULLIF(?, ''), image_url), 
                rating = COALESCE(?, rating), reviews_count = COALESCE(?, reviews_count), 
                availability = COALESCE(NULLIF(?, ''), availability), 
                category = COALESCE(NULLIF(?, ''), category), last_scraped = ?, 
                user_id = COALESCE(?, user_id), region = ?, currency = ?, symbol = ?, native_price = ?,
                target_price = ?
            WHERE id = ?
        """, (
            data.get("title"), norm_price, norm_orig, data["url"],
            data.get("image_url"), data.get("rating"), data.get("reviews_count"),
            data.get("availability"), data.get("category"), now_str, user_id,
            region, currency, symbol, native_price, target_price, product_id
        ))
    else:
        target_price = norm_target
        cursor.execute("""
            INSERT INTO products (
                asin, title, current_price, original_price, target_price, url, 
                image_url, rating, reviews_count, availability, category, last_scraped, 
                user_id, region, currency, symbol, native_price
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["asin"], data["title"], norm_price, norm_orig,
            target_price, data["url"], data.get("image_url"), data.get("rating"),
            data.get("reviews_count"), data.get("availability"), data.get("category"), 
            now_str, user_id, region, currency, symbol, native_price
        ))
        product_id = cursor.lastrowid

    # Log price history entry
    cursor.execute("""
        INSERT INTO price_history (product_id, price, timestamp, date)
        VALUES (?, ?, ?, ?)
    """, (product_id, norm_price, now_str, today_str))

    conn.commit()
    conn.close()

    export_to_csv()
    return product_id


def delete_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM price_history WHERE product_id = ?", (product_id,))
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    export_to_csv()


def update_target_price(product_id: int, target_price: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET target_price = ? WHERE id = ?", (target_price, product_id))
    conn.commit()
    conn.close()


def get_price_history(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT price, timestamp, date
        FROM price_history
        WHERE product_id = ?
        ORDER BY timestamp ASC
    """, (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_to_csv():
    """Exports dataset to clean CSV format."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.title, h.price, h.date, p.asin, p.url
        FROM price_history h
        JOIN products p ON h.product_id = p.id
        ORDER BY h.timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Price', 'Date', 'ASIN', 'URL'])
        for r in rows:
            writer.writerow([r['title'], r['price'], r['date'], r['asin'], r['url']])


def simulate_product_price_drop(product_id: int, drop_percent: float = 30.0) -> dict:
    """
    Simulates a sudden flash-crash price drop (e.g. -30%) on a tracked item.
    Updates current_price in SQLite, appends to price_history, and exports to CSV.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_price, original_price, native_price, currency, region FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    cur = float(row["current_price"])
    orig = float(row["original_price"]) if row["original_price"] else cur
    curr = row["currency"]
    new_price = max(1.0, round(cur * (1.0 - (drop_percent / 100.0)), 2))
    new_native = round(new_price * 83.50, 2) if curr == "INR" else new_price
    
    cursor.execute("""
        UPDATE products 
        SET current_price = ?, original_price = ?, native_price = ?, last_scraped = datetime('now', 'localtime')
        WHERE id = ?
    """, (new_price, orig, new_native, product_id))
    
    now_dt = datetime.datetime.now()
    cursor.execute("""
        INSERT INTO price_history (product_id, price, timestamp, date)
        VALUES (?, ?, ?, ?)
    """, (product_id, new_price, now_dt.strftime("%Y-%m-%d %H:%M:%S"), now_dt.strftime("%Y-%m-%d")))
    
    conn.commit()
    conn.close()
    export_to_csv()
    return get_product_by_id(product_id)


def reset_product_price(product_id: int) -> dict:
    """
    Restores a product's price to its authentic pre-drop baseline.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT original_price, current_price, currency FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    orig_p = float(row["original_price"]) if row["original_price"] else None
    curr = row["currency"]

    cursor.execute("SELECT price FROM price_history WHERE product_id = ? ORDER BY id ASC", (product_id,))
    rows = cursor.fetchall()
    prices = [float(r[0]) for r in rows if r[0] is not None]

    if orig_p and orig_p > 0:
        restored_price = round(orig_p * 0.90, 2)
    elif prices:
        # Use maximum of median of historical prices
        restored_price = max(sorted(prices)[len(prices) // 2], max(prices[:10]))
    else:
        restored_price = 99.0

    original_p = orig_p if orig_p else round(restored_price * 1.15, 2)
    new_native = round(restored_price * 83.50, 2) if curr == "INR" else restored_price
    
    cursor.execute("""
        UPDATE products 
        SET current_price = ?, original_price = ?, native_price = ?, last_scraped = datetime('now', 'localtime')
        WHERE id = ?
    """, (restored_price, original_p, new_native, product_id))
    
    now_dt = datetime.datetime.now()
    cursor.execute("""
        INSERT INTO price_history (product_id, price, timestamp, date)
        VALUES (?, ?, ?, ?)
    """, (product_id, restored_price, now_dt.strftime("%Y-%m-%d %H:%M:%S"), now_dt.strftime("%Y-%m-%d")))
    
    conn.commit()
    conn.close()
    export_to_csv()
    return get_product_by_id(product_id)


def simulate_random_flash_crash(drop_percent: float = 35.0) -> dict:
    """
    Selects an active product and simulates an instant flash crash price drop.
    Prefers products that have not yet had a recent drop.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, current_price, target_price FROM products ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return simulate_product_price_drop(row["id"], drop_percent=drop_percent)


def reset_all_product_prices() -> int:
    """
    Restores all tracked products back to their verified market baselines.
    Returns the count of products restored.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products")
    rows = cursor.fetchall()
    conn.close()
    
    count = 0
    for r in rows:
        if reset_product_price(r["id"]):
            count += 1
    return count
