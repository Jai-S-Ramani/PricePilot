# ⚡ Amazon Price Intelligence & Multi-Store Arbitrage Command Center

> An enterprise-grade, full-stack Data Analytics Web Application, Competitor Arbitrage Engine, Live Amazon Catalog Search, and Multi-Channel Notification Platform built with Python, Flask, BeautifulSoup4, SQLite3, Chart.js, and GSAP. A real-time price monitoring, predictive intelligence, and multi-channel alerting ecosystem.
>
> **Architect & Lead Engineer**: **Jai S Ramani**  
> 📧 **Email**: [jaisramani05@gmail.com](mailto:jaisramani05@gmail.com) | 💼 **LinkedIn**: [jai-s-ramani-2948532bb](https://www.linkedin.com/in/jai-s-ramani-2948532bb) | 🐙 **GitHub**: [Jai-S-Ramani](https://github.com/Jai-S-Ramani)

---

## 🌟 Project Highlights

- 🔎 **Real-Time Amazon Live Search & Autocomplete**: Search products directly across Amazon's catalog with instant debounced suggestions, regional selection (defaulting to 🇮🇳 India `IN`), and 1-click tracking.
- 🏪 **18-Store Competitor Arbitrage Engine**: Benchmarks Amazon against **13 Indian marketplaces** (Flipkart, Croma, Reliance Digital, Tata CLiQ, JioMart, Meesho, Blinkit, Zepto, Swiggy Instamart, BigBasket, Myntra, AJIO, Nykaa) and **5 Global retailers** (Walmart, Best Buy, eBay, Target, B&H Photo).
- 🏷️ **Intelligent Catalog Availability Filter**: Real-world vertical filtering that excludes stores that do not sell a specific product category (e.g., Nykaa does not sell OnePlus Buds; Croma does not sell fashion apparel).
- 🔔 **Multi-Channel Alert Dispatcher**: Pushes instant price-drop alerts across **Discord Webhooks** (rich emerald embeds), **Telegram Bots** (Markdown push notifications), and **HTML Emails**.
- 💱 **Multi-Currency FX Engine (7 Currencies)**: Full support for `INR (₹)`, `USD ($)`, `EUR (€)`, `GBP (£)`, `CAD (CA$)`, `AUD (A$)`, and `JPY (¥)` with exact native price preservation and zero rounding discrepancies.
- ⏱️ **Autonomous Background Scheduler**: Isolated thread daemon continuously sweeping tracked items, calculating volatility, and syncing time-series records to SQLite and CSV.
- 📈 **Predictive Analytics & AI Decision Signals**: Real-time signals (`BUY_NOW`, `FAIR_PRICE`, `WAIT`), standard-deviation volatility scoring, deal scores, and 30-day interactive SVG sparklines.
- 🎨 **Obsidian Briar & Warm Biscuit Luxe UI**: Premium dark glassmorphic design featuring rolling GSAP numeric roll-ups, spring pop-up physics, and interactive Chart.js analytics.
- 📊 **Multi-Format Data Exports**: Export time-series records to CSV and comprehensive portfolio intelligence to JSON, with per-product historical downloads directly from the analytics modal.
- 🔄 **Instant 1-Click Price Re-Scraper**: Refresh live Amazon prices for any individual product on demand with animated spring feedback.
- 🧪 **43 Automated Tests**: Comprehensive test suite covering scrapers, competitor comparison, availability filters, scheduler lifecycle, export pipelines, and REST APIs.

---

## 📁 Repository Structure

```
PortfolioProjects/
├── AmazonWebScraperDataset.csv       # Live synchronized CSV dataset export
├── run_original_scraper.py          # Standalone runner for single-item command-line scraper
├── architecture.html                # Interactive system architecture diagram
├── pricepilot.architecture.json     # Architecture specification model
├── README.md                        # Portfolio overview and repository documentation
└── amazon_scraper_app/              # Production Web Application & Intelligence Center
    ├── app.py                       # REST API controllers & web routes
    ├── scheduler.py                 # Thread-safe BackgroundPriceScheduler daemon
    ├── scraper.py                   # Multi-region BS4 scraper, live search & suggestion engine
    ├── competitor.py                # 18-store competitor comparison & catalog availability engine
    ├── database.py                  # SQLite database manager, analytics & seed pipelines
    ├── notifier.py                  # Email, Discord webhook & Telegram notification engine
    ├── amazon_tracker.db            # Production SQLite3 database
    ├── README.md                    # Detailed application documentation
    ├── tests/
    │   ├── test_all_features.py     # Base test suite (24 tests)
    │   └── test_advanced_features.py# Search, notification & export tests (19 tests)
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

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Install Dependencies
```bash
python -m pip install flask beautifulsoup4 requests pandas
```

### 3. Launch the Web Application
```bash
python amazon_scraper_app/app.py
```
Open **[`http://127.0.0.1:5000/dashboard`](http://127.0.0.1:5000/dashboard)** in your browser.
*(Or visit [`http://127.0.0.1:5000/`](http://127.0.0.1:5000/) for the High-Conversion Landing Page & 1-Click Guest Demo)*.

### 4. Run Automated Tests
```bash
python -m unittest discover -s amazon_scraper_app/tests -p "test_*.py"
```
*(All 43 tests passing 100% across both test modules)*.

### 5. Run the Original Tutorial Scraper
```bash
python run_original_scraper.py
```
This logs scraped product entries directly into [`AmazonWebScraperDataset.csv`](file:///e:/DATA%20ANALYTICS/PortfolioProjects/AmazonWebScraperDataset.csv).

---

## 📜 Attribution & Credits

- **Architect & Lead Developer**: **Jai S Ramani**
  - 📧 **Email**: [jaisramani05@gmail.com](mailto:jaisramani05@gmail.com)
  - 💼 **LinkedIn**: [https://www.linkedin.com/in/jai-s-ramani-2948532bb](https://www.linkedin.com/in/jai-s-ramani-2948532bb)
  - 🐙 **GitHub**: [https://github.com/Jai-S-Ramani](https://github.com/Jai-S-Ramani)
- **Key Capabilities**: Production-grade application featuring real-time Amazon catalog search, multi-store competitor arbitrage, catalog availability filtering, multi-channel alerting, predictive analytics, custom dark mode branding, and modern architecture.
- **Tech Stack**: Python 3, Flask, BeautifulSoup4, SQLite3, Chart.js, GSAP 3, FontAwesome 6, Google Fonts.
