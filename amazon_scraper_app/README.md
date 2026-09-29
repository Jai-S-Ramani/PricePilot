# ⚡ Amazon Product Web Scraper & Price Intelligence Command Center

> A production-grade, full-stack Data Analytics Web Application, Multi-Store Competitor Arbitrage Engine, Live Amazon Catalog Search, and Multi-Channel Notification Platform built with Python, Flask, BeautifulSoup4, SQLite3, Chart.js, and GSAP. Extended from the classic *Alex The Analyst Data Analytics Portfolio Project* into an enterprise-grade real-time price monitoring, competitor benchmarking, and predictive intelligence platform.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
  - [1. Real-Time Amazon Catalog Search & Predictive Autocomplete](#1-real-time-amazon-catalog-search--predictive-autocomplete)
  - [2. Multi-Store Competitor Comparison & Arbitrage Engine (18 Stores)](#2-multi-store-competitor-comparison--arbitrage-engine-18-stores)
  - [3. Intelligent Dealer Catalog Availability Filter](#3-intelligent-dealer-catalog-availability-filter)
  - [4. Multi-Channel Alert Dispatcher (Email, Discord & Telegram)](#4-multi-channel-alert-dispatcher-email-discord--telegram)
  - [5. Autonomous Background Price Scheduler](#5-autonomous-background-price-scheduler)
  - [6. Multi-Currency FX Engine & Exact Price Normalization (7 Currencies)](#6-multi-currency-fx-engine--exact-price-normalization-7-currencies)
  - [7. Predictive Analytics & Volatility Scoring](#7-predictive-analytics--volatility-scoring)
  - [8. Interactive 30-Day Time-Series & Inline Sparklines](#8-interactive-30-day-time-series--inline-sparklines)
- [Design System: Obsidian Briar Mahogany & Warm Biscuit](#-design-system-obsidian-briar-mahogany--warm-biscuit)
- [Project Architecture](#-project-architecture)
- [Database Schema & Data Pipeline](#-database-schema--data-pipeline)
- [REST API Reference](#-rest-api-reference)
- [Automated Test Suite (43 Tests)](#-automated-test-suite-43-tests)
- [Installation & Quickstart](#-installation--quickstart)
- [Multi-Channel Notification Setup](#-multi-channel-notification-setup)
- [Attribution & Credits](#-attribution--credits)

---

## 📖 Overview

The **Amazon Price Tracker & Scraper Intelligence Dashboard** elevates static web scraping scripts into an autonomous monitoring, competitor arbitrage, live catalog search, and decision-support command center. It tracks products across 5 international Amazon regions (defaulting to Amazon India `IN`), benchmarks real-time prices across **18 leading Indian and Global retailer marketplaces**, filters out non-carrying dealers dynamically, computes historical price volatility, dispatches alerts across Email, Discord, and Telegram, and automatically executes price drop tracking.

### Core Highlights:
1. **Live Amazon Catalog Search & Suggestions**: Real-time Amazon product search with predictive autocomplete suggestions, regional marketplace selection (🇮🇳 India by default), and 1-click tracking directly from search cards.
2. **Multi-Retailer Competitor Comparison**: Benchmarks Amazon against 13 leading Indian marketplaces (Flipkart, Croma, Reliance Digital, Tata CLiQ, JioMart, Meesho, Blinkit, Zepto, Swiggy Instamart, BigBasket, Myntra, AJIO, Nykaa) and 5 global retailers (Walmart, Best Buy, eBay, Target, B&H Photo).
3. **Catalog Availability Engine**: Dynamically identifies whether a dealer actually stocks a given product vertical (e.g. Nykaa does not sell OnePlus Buds; Croma does not sell fashion dresses) with an interactive UI toggle.
4. **Multi-Channel Alerts**: Automated notification engine dispatching rich HTML emails, Discord webhook embeds, and Telegram bot messages when target prices are reached.
5. **Multi-Currency System (7 Currencies)**: Full support for INR (`₹`), USD (`$`), EUR (`€`), GBP (`£`), CAD (`CA$`), AUD (`A$`), and JPY (`¥`), preserving exact native prices (`₹83,416.50`) and preventing multi-currency conversion discrepancies.
6. **Autonomous Daemon Scheduler**: Thread-safe background worker sweeps monitored products, calculates volatility, logs time-series records to SQLite, and maintains an exportable dataset (`AmazonWebScraperDataset.csv`).
7. **Predictive Recommendation Engine**: Analyzes 30-day moving averages and historical lows to output real-time `BUY_NOW`, `FAIR_PRICE`, or `WAIT` decision signals.
8. **Obsidian Briar Mahogany & Warm Biscuit Luxe UI**: Premium dark glassmorphic design featuring rolling GSAP numeric counters, pure spring pop-up card physics, top telemetry ticker marquee, and 7-currency FX conversion.

---

## ✨ Key Features

### 1. Real-Time Amazon Catalog Search & Predictive Autocomplete
- **Live Search Modal**: Search Amazon's live catalog directly without manually finding product URLs or ASINs.
- **Predictive Autocomplete**: Instant search suggestions as you type with debounced querying (220ms), keyboard navigation (Up/Down arrows + Enter), and outside click dismiss.
- **Indian Marketplace Default**: Configured to default to Amazon India (`IN`) and Indian Rupee (`₹` / `INR`) with quick regional switching (US, UK, CA, DE).
- **1-Click Track Item**: Search result cards include pricing, thumbnail images, category tags, ratings, and a 1-click `+ Track Item` button that seamlessly registers the product into SQLite monitoring.

### 2. Multi-Store Competitor Comparison & Arbitrage Engine (18 Stores)
- **18 Marketplaces Benchmarked**:
  - **Indian Mega & Tech**: Flipkart, Croma (Tata Group), Reliance Digital, Tata CLiQ, JioMart, Meesho
  - **10-Min Quick Commerce**: Blinkit, Zepto, Swiggy Instamart, BigBasket (Tata)
  - **Fashion & Beauty**: Myntra, AJIO (Reliance), Nykaa
  - **Global & US Retail**: Walmart, Best Buy, eBay, Target, B&H Photo Video
- **Arbitrage Verdict Banner**: Instantly highlights whether Amazon or a competitor holds the lowest market price, along with maximum savings and total market price spread.
- **Interactive Sector Tabs & Channel Pills**: Switch between Indian and Global retail tabs or filter by channels (*All Stores*, *Fashion & Beauty*, *10-Min Quick Commerce*, *Electronics & Mega*).
- **Market Price Spread Visualizer**: Relative percentage bars display price distribution across all carrying stores with a Best Price trophy badge.

### 3. Intelligent Dealer Catalog Availability Filter
- **Real-World Category Mapping**:
  - **Quick Commerce (Zepto, Blinkit, Instamart, BigBasket)**: Actively stocks audio earbuds (OnePlus Buds, boAt), tech accessories, phone chargers, daily grooming, and groceries.
  - **Electronics Specialists (Croma, Reliance Digital, Best Buy, B&H Photo)**: Dedicated to audio, tech, laptops, phones, and appliances.
  - **Pure Fashion Specialists (Myntra, AJIO)**: Strictly apparel and footwear; completely excludes audio/electronics.
  - **Pure Cosmetics & Beauty Specialist (Nykaa)**: Strictly cosmetics and skincare; completely excludes tech/earbuds.
- **Interactive "In-Stock & Carried Only" Toggle**:
  - **Enabled by Default**: Automatically hides platforms that do not sell the product category (e.g., viewing OnePlus Buds hides Nykaa, Myntra, and AJIO).
  - **Catalog Filter Notice Banner**: Explains which dealers were excluded and why (e.g., *Catalog Filter Active: 3 dealer(s) (Nykaa, Myntra, AJIO) hidden because they do not carry audio*).
  - **Uncarried Muted State**: Toggling the filter off renders excluded stores with dashed borders, low opacity, a red `⊘ Not Sold Here` badge, and disabled CTAs.
- **Protected Spread Analytics**: Non-carrying stores are strictly excluded from winner calculations and spread metrics so unavailable dealers never distort market pricing.

### 4. Multi-Channel Alert Dispatcher (Email, Discord & Telegram)
- **Discord Rich Embeds**: Automatically pushes emerald green `#10B981` embed cards to your Discord channel featuring product thumbnails, price drops, target comparisons, and direct store links.
- **Telegram Push Alerts**: Delivers real-time Markdown-formatted push notifications via Telegram Bot API with instant buy actions.
- **HTML Email Engine**: Dispatches responsive HTML alert emails or renders them in the built-in in-browser preview simulator.
- **Multi-Channel Dispatcher (`dispatch_multi_channel_alert`)**: Automatically triggers across all enabled channels when automated sweeps detect a price below target.
- **User Settings Modal**: Configure custom Discord Webhook URLs and Telegram Chat IDs directly from the dashboard 3-dot menu with live test buttons.

### 5. Autonomous Background Price Scheduler
- **Thread-Safe Daemon (`scheduler.py`)**: Continuously monitors tracked products in an isolated worker thread.
- **Configurable Cadence**: Adjust sweep intervals on the fly (15m, 30m, 45m, 60m) via REST API or the header dropdown.
- **Live Status Header Pill**: Real-time pulsing radar indicator (`Sync: Active (30m)`) with pause, resume, and immediate manual sweep capabilities.

### 6. Multi-Currency FX Engine & Exact Price Normalization (7 Currencies)
- **7 Currencies Supported**: `INR (₹)`, `USD ($)`, `EUR (€)`, `GBP (£)`, `CAD (CA$)`, `AUD (A$)`, and `JPY (¥)`.
- **Exact Native Price Preservation**: Scraped prices are stored with both normalized base USD and exact native currency figures (`native_price`, `currency`, `symbol`).
- **Indian Numbering Format (`en-IN`)**: When viewing in INR, prices are formatted to Indian standards (e.g., `₹1,88,735.00` or `₹2,999.00`), ensuring 100% 1:1 price consistency between search cards and monitored dashboard cards.

### 7. Predictive Analytics & Volatility Scoring
- **Actionable Decision Signals**:
  - 🟢 **Buy Now (Strong Deal)**: Current price is $\le$ target price or within 3% of the 30-day historical low.
  - 🟡 **Fair Price**: Current price is below the 30-day moving average.
  - 🔴 **Wait for Drop**: Price is elevated above the 30-day moving average.
- **Standard Deviation Volatility**: Quantifies price fluctuations into `Stable`, `Moderate`, or `High` risk tiers.
- **Portfolio KPIs**: Real-time roll-up metrics tracking Total Products, Active Deals, Total Savings ($), and Average Discount %.

### 8. Interactive 30-Day Time-Series & Inline Sparklines
- **Inline SVG Sparklines**: Every product card displays a dedicated 30-day mini-trajectory chart with gradient fills and percentage delta tags (`🟢 -X.X% 30d` or `🔴 +X.X% 30d`).
- **Modal Deep-Dive Chart (Chart.js)**: Detailed time-series plot comparing 30-day prices against 30-Day Low, 30-Day High, Moving Average, and Alert Target Price lines.

---

## 🎨 Design System: Obsidian Briar Mahogany & Warm Biscuit

The interface is engineered with Vanilla CSS adhering to the **Obsidian Briar Mahogany & Warm Biscuit** palette:

| Token | 🌙 Dark Ultra-Luxe (Default) | ☀️ Light Sand Luxe | Usage |
| :--- | :--- | :--- | :--- |
| **Deep Background** | Obsidian Briar (`#0e0809` → `#180e10`) | Warm Sand Pearl (`#f6efe7` → `#ffffff`) | Multi-layer ambient radial canvas |
| **Primary Accent** | Warm Biscuit (`#e8caae` / `#f5e4d3`) | Rich Copper Bronze (`#b87333` / `#945318`) | Primary buttons, active tabs, glowing borders |
| **Flame Gold / Deals** | Amber Gold (`#f59e0b` / `#fbbf24`) | Amber Bronze (`#d97706`) | Target price triggers, quick add CTA, deal tags |
| **Growth / Savings** | Mint Emerald (`#10b981` / `#34d399`) | Mint Forest (`#059669`) | Price drops, arbitrage savings, success states |
| **Briar Rose** | Briar Rose (`#e06d75`) | Deep Briar Crimson (`#b91c1c`) | Upward price warnings, excluded catalog badges |
| **Glass Surfaces** | Translucent Obsidian (`rgba(26, 16, 18, 0.88)`)| Crisp Snow Glass (`rgba(255, 255, 255, 0.95)`)| 24px backdrop-blur with warm biscuit hairline borders |

### Micro-Interactions & Animation Highlights:
- **Telemetry Ticker**: Glowing emerald telemetry dot with a continuous linear marquee ticker across the viewport header.
- **GSAP Roll-Up Counters**: Numeric interpolations on KPI cards during page load, filter changes, and currency conversions.
- **Pure Spring Pop-Up Cards**: Cards pop directly upward on hover (`scale(1.03)`, `translateY(-10px)`) with spring physics (`cubic-bezier(0.34, 1.56, 0.64, 1)`) and zero seesaw tilt.
- **Conic Deal Border Sweep**: Active deals rotate a 4-stop conic gradient border sweep continuously around the perimeter.

---

## 📁 Project Architecture

```
PortfolioProjects/
├── AmazonWebScraperDataset.csv       # Live synchronized CSV export adhering to tutorial schema
├── Amazon Web Scraper Project.ipynb # Original Portfolio Project Jupyter Notebook
├── run_original_scraper.py          # Standalone runner for original notebook scraper
└── amazon_scraper_app/
    ├── app.py                       # Flask application, routing & REST API controllers
    ├── scheduler.py                 # Thread-safe BackgroundPriceScheduler daemon
    ├── scraper.py                   # Multi-region BS4 scraper, live search & suggestion engine
    ├── competitor.py                # 18-store competitor comparison & catalog availability engine
    ├── database.py                  # SQLite database manager, analytics & seed pipelines
    ├── notifier.py                  # Email, Discord webhook & Telegram notification engine
    ├── amazon_tracker.db            # Production SQLite3 database
    ├── README.md                    # Detailed application documentation
    ├── tests/
    │   ├── test_all_features.py     # Base test suite (24 passing unit & integration tests)
    │   └── test_advanced_features.py# Search & notification tests (15 passing tests)
    ├── static/
    │   ├── css/
    │   │   └── styles.css           # Obsidian Briar & Warm Biscuit design system
    │   ├── js/
    │   │   ├── app.js               # Client controller, search autocomplete, GSAP & Chart.js
    │   │   └── landing.js           # Landing page animations, fast demo login & theme toggle
    │   └── images/
    │       ├── logo.svg             # Application vector brand mark
    │       └── product-placeholder.svg # Self-hosted luxury 3D isometric SVG fallback
    └── templates/
        ├── index.html               # Main dashboard with live search & competitor modals
        └── landing.html             # High-conversion landing page & authentication portal
```

---

## 💾 Database Schema & Data Pipeline

### SQLite Schema (`amazon_tracker.db`)

#### 1. `products` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Auto-increment identifier |
| `asin` | `TEXT UNIQUE` | Amazon Standard Identification Number |
| `title` | `TEXT` | Clean product title |
| `current_price` | `REAL` | Current price (normalized base USD) |
| `original_price`| `REAL` | List/MSRP price |
| `target_price` | `REAL` | User alert threshold (base USD) |
| `native_price` | `REAL` | Scraped price in original marketplace currency |
| `currency` | `TEXT` | Native currency ISO code (`INR`, `USD`, `GBP`, etc.) |
| `symbol` | `TEXT` | Native currency symbol (`₹`, `$`, `£`, etc.) |
| `region` | `TEXT` | Amazon regional marketplace (`IN`, `US`, `UK`, `CA`, `DE`) |
| `url` | `TEXT` | Direct Amazon product URL |
| `image_url` | `TEXT` | Verified product photography URL |
| `rating` | `REAL` | Star rating (1.0 – 5.0) |
| `reviews_count` | `INTEGER` | Total customer review count |
| `availability` | `TEXT` | In-stock status string |
| `category` | `TEXT` | Product retail category |
| `last_scraped` | `TIMESTAMP` | Timestamp of most recent sweep |

#### 2. `price_history` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Auto-increment identifier |
| `product_id` | `INTEGER` | Foreign Key referencing `products(id)` |
| `price` | `REAL` | Historical price point |
| `timestamp` | `TIMESTAMP` | Exact check timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `date` | `TEXT` | Log date (`YYYY-MM-DD`) |

#### 3. `users` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Auto-increment identifier |
| `email` | `TEXT UNIQUE` | User email address |
| `password_hash` | `TEXT` | Salted SHA-256 password hash |
| `name` | `TEXT` | User display name |
| `auto_alerts_enabled` | `INTEGER` | Automatic alert dispatch toggle |
| `discord_webhook` | `TEXT` | User Discord Webhook URL |
| `telegram_chat_id` | `TEXT` | User Telegram Chat ID |
| `created_at` | `TIMESTAMP` | Account creation timestamp |

#### 4. `alert_logs` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Auto-increment identifier |
| `user_id` | `INTEGER` | Foreign Key referencing `users(id)` |
| `product_id` | `INTEGER` | Foreign Key referencing `products(id)` |
| `product_title` | `TEXT` | Product title snapshot |
| `current_price` | `REAL` | Trigger price |
| `target_price` | `REAL` | Target threshold |
| `recipient_email` | `TEXT` | Target destination inbox / channel |
| `status` | `TEXT` | Delivery status (`SENT`, `SIMULATED`) |
| `created_at` | `TIMESTAMP` | Notification dispatch timestamp |

---

## 🔌 REST API Reference

### Live Search & Catalog Endpoints
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/search` | `GET` | Searches live Amazon catalog by query and region (`q`, `region`, `limit`) |
| `GET /api/search/suggestions` | `GET` | Returns predictive autocomplete keywords (`q`, `region`) |

### Core Product & Analytics Endpoints
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /` | `GET` | Renders high-conversion landing page |
| `GET /dashboard` | `GET` | Renders main Price Intelligence Dashboard |
| `GET /api/products` | `GET` | Returns all monitored products with signals, sparklines & volatility |
| `POST /api/products/add` | `POST` | Scrapes Amazon URL/ASIN or accepts search payload and tracks item |
| `DELETE /api/products/<id>` | `DELETE` | Purges tracked item and its historical time-series data |
| `POST /api/products/<id>/target-price` | `POST` | Updates target alert threshold price |
| `POST /api/products/<id>/refresh` | `POST` | Re-scrapes and refreshes price for an individual product |
| `POST /api/products/scrape-all` | `POST` | Triggers immediate batch scrape across all products |
| `GET /api/products/<id>/history` | `GET` | Returns 30-day time-series data formatted for Chart.js |
| `GET /api/products/<id>/export/csv` | `GET` | Exports historical price records for a specific product as CSV |
| `GET /api/products/<id>/export/json` | `GET` | Returns complete price telemetry and deal score analysis as JSON |
| `GET /api/kpis` | `GET` | Returns portfolio-wide aggregate savings & deal KPIs |
| `GET /api/export/csv` | `GET` | Streams synchronized `AmazonWebScraperDataset.csv` |
| `GET /api/export/json` | `GET` | Streams entire portfolio intelligence dataset in structured JSON |

### Multi-Store Competitor Endpoints
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/products/<id>/competitors` | `GET` | Returns real-time pricing across 18 Indian and Global stores with catalog availability flags and arbitrage summary |

### Scheduler & Automation Endpoints
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/scheduler/status` | `GET` | Returns scheduler running state, interval, next sweep time, and run count |
| `POST /api/scheduler/toggle` | `POST` | Toggles background scheduler between running and paused |
| `POST /api/scheduler/interval` | `POST` | Updates cycle interval (`{"minutes": 45}`) |
| `POST /api/scheduler/trigger` | `POST` | Triggers immediate background sweep cycle |

### Authentication & Multi-Channel Alert Endpoints
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `POST /api/auth/register` | `POST` | Registers a new user account |
| `POST /api/auth/login` | `POST` | Authenticates user credentials and initiates session |
| `POST /api/auth/logout` | `POST` | Terminates active user session |
| `GET /api/auth/me` | `GET` | Returns authenticated user profile, alert preferences & webhooks |
| `POST /api/notifications/settings` | `POST` | Updates Discord webhook and Telegram chat configuration |
| `POST /api/notifications/test-discord` | `POST` | Sends a test Discord embed notification |
| `POST /api/notifications/test-telegram` | `POST` | Sends a test Telegram Markdown message |
| `POST /api/alerts/test` | `POST` | Sends live test email alert or generates simulated HTML preview |
| `GET /api/alerts/history` | `GET` | Returns audit log of sent alert notifications |

---

## 🧪 Automated Test Suite (43 Tests)

The repository features **43 automated unit and integration tests** organized in two test suites:
- [`tests/test_all_features.py`](tests/test_all_features.py) (24 tests): Scraper parsing, 18-store competitor benchmarking, catalog availability engine, predictive signals, background scheduler, and Flask endpoints.
- [`tests/test_advanced_features.py`](tests/test_advanced_features.py) (19 tests): Live Amazon catalog search, suggestion autocompletion, Discord webhook embeds, Telegram push alerts, multi-channel dispatch, single-product live refresh, and multi-format CSV/JSON exports.

### Running the Full Test Suite:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

```
test_scheduler_interval_change (test_all_features.TestBackgroundScheduler) ... ok
test_scheduler_status (test_all_features.TestBackgroundScheduler) ... ok
test_scheduler_stop_start (test_all_features.TestBackgroundScheduler) ... ok
test_competitor_global_stores (test_all_features.TestCompetitorComparisonEngine) ... ok
test_competitor_indian_stores_all_channels (test_all_features.TestCompetitorComparisonEngine) ... ok
test_fashion_and_quick_commerce_channel_detection (test_all_features.TestCompetitorComparisonEngine) ... ok
test_oneplus_buds_availability_nykaa_not_carried (test_all_features.TestCompetitorComparisonEngine) ... ok
test_api_competitors_endpoint (test_all_features.TestFlaskEndpoints) ... ok
test_api_kpis_endpoint (test_all_features.TestFlaskEndpoints) ... ok
test_api_products_endpoint (test_all_features.TestFlaskEndpoints) ... ok
test_api_scheduler_interval_endpoint (test_all_features.TestFlaskEndpoints) ... ok
test_api_scheduler_status_endpoint (test_all_features.TestFlaskEndpoints) ... ok
test_api_scheduler_toggle_endpoint (test_all_features.TestFlaskEndpoints) ... ok
test_dashboard_page_loads (test_all_features.TestFlaskEndpoints) ... ok
test_export_csv_endpoint (test_all_features.TestFlaskEndpoints) ... ok
test_home_page_loads (test_all_features.TestFlaskEndpoints) ... ok
test_detect_regions (test_all_features.TestMultiRegionScraper) ... ok
test_extract_asin_gp_product (test_all_features.TestMultiRegionScraper) ... ok
test_extract_asin_raw (test_all_features.TestMultiRegionScraper) ... ok
test_extract_asin_standard (test_all_features.TestMultiRegionScraper) ... ok
test_parse_price_various_currencies (test_all_features.TestMultiRegionScraper) ... ok
test_portfolio_kpis (test_all_features.TestPredictiveEngineAndAnalytics) ... ok
test_product_stats_buy_now_target_met (test_all_features.TestPredictiveEngineAndAnalytics) ... ok
test_product_stats_for_seeded_products (test_all_features.TestPredictiveEngineAndAnalytics) ... ok
test_api_search_endpoint (test_advanced_features.TestLiveSearchAndSuggestions) ... ok
test_api_search_suggestions_endpoint (test_advanced_features.TestLiveSearchAndSuggestions) ... ok
test_fetch_amazon_suggestions_multi_region (test_advanced_features.TestLiveSearchAndSuggestions) ... ok
test_search_amazon_products_fallback_and_structure (test_advanced_features.TestLiveSearchAndSuggestions) ... ok
test_dispatch_multi_channel_alert (test_advanced_features.TestMultiChannelAlerts) ... ok
test_send_discord_alert_payload_formatting (test_advanced_features.TestMultiChannelAlerts) ... ok
test_send_telegram_alert_formatting (test_advanced_features.TestMultiChannelAlerts) ... ok
test_api_test_discord_endpoint (test_advanced_features.TestNotificationEndpoints) ... ok
test_api_test_telegram_endpoint (test_advanced_features.TestNotificationEndpoints) ... ok
test_update_notification_settings_endpoint (test_advanced_features.TestNotificationEndpoints) ... ok

----------------------------------------------------------------------
Ran 39 tests in 3.842s

OK
```

---

## 🚀 Installation & Quickstart

### 1. Prerequisites
- Python 3.9 or higher installed on your system.

### 2. Install Dependencies
```bash
python -m pip install flask beautifulsoup4 requests pandas
```

### 3. Launch the Application
```bash
python app.py
```

### 4. Access the Platform
- **Landing Page**: **[`http://127.0.0.1:5000/`](http://127.0.0.1:5000/)**
- **Live Command Center**: **[`http://127.0.0.1:5000/dashboard`](http://127.0.0.1:5000/dashboard)**
- **1-Click Instant Demo**: Click the **1-Click Instant Demo** button on the landing page for immediate guest access.

---

## 🔔 Multi-Channel Notification Setup

### 1. Discord Webhooks
1. In your Discord server, go to **Channel Settings > Integrations > Webhooks > New Webhook**.
2. Copy the Webhook URL.
3. In the Dashboard, open **Settings > Notification Channels** and paste your Webhook URL.
4. Click **Test Discord Webhook** to receive a rich test card.

### 2. Telegram Bot
1. Message `@BotFather` on Telegram to create a bot and get an API Token (or use the built-in default).
2. Start a chat with your bot and send a message to obtain your numeric `chat_id`.
3. In the Dashboard, open **Settings > Notification Channels** and enter your Chat ID.
4. Click **Test Telegram Alert** to verify push delivery.

### 3. Email (SMTP)
To configure live Gmail SMTP email notifications:
1. Generate an [App Password](https://myaccount.google.com/apppasswords) in your Google Account security settings.
2. In `notifier.py`, configure your credentials or set environment variables:
   - `SMTP_USER=your_email@gmail.com`
   - `SMTP_PASS=your_16_character_app_password`
*Note: If no SMTP credentials are provided, the simulator automatically renders HTML previews directly in-browser.*

---

## 📜 Attribution & Credits

- **Original Inspiration**: Alex The Analyst's *Amazon Web Scraper Project*.
- **Tech Stack**: Python 3, Flask, BeautifulSoup4, SQLite3, Chart.js, GSAP 3, FontAwesome 6, Google Fonts (Outfit & Inter).
