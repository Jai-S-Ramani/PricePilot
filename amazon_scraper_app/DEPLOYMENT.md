# 🚀 PricePilot — Production Deployment & Cloud Hosting Guide

This guide details how to run PricePilot in production using **Docker** locally or deploy it live on the cloud for **free** on **Render**, **Railway**, or **Fly.io** to showcase on your portfolio/resume.

---

## 1. Quickstart: 1-Command Local Docker Execution

Prerequisites: [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

```bash
# Clone and launch in container
docker compose up --build
```
Navigate to **`http://localhost:5000`** in your browser. All tracking data is automatically persisted to `amazon_tracker.db`.

---

## 2. Deploy Live Online (100% Free on Render.com)

Render provides free hosting with automatic HTTPS and continuous deployment directly from your GitHub repository.

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Add Docker and production configurations"
   git push origin main
   ```
2. **Log into [Render.com](https://render.com)** and click **New +** $\to$ **Web Service**.
3. **Connect your GitHub repository**.
4. Configure settings:
   - **Environment**: `Docker` (or `Python 3`)
   - **Root Directory**: `amazon_scraper_app`
   - **Build Command**: `pip install -r requirements.txt` (if using Python env)
   - **Start Command**: `gunicorn --workers=4 --bind=0.0.0.0:$PORT app:app`
   - **Health Check Path**: `/api/health`
5. Click **Deploy Web Service**.
6. In ~2 minutes, Render will assign you a live URL:
   **`https://pricepilot-yourname.onrender.com`**!

---

## 3. Production Health Check & Monitoring

PricePilot exposes automated health metrics for uptime monitoring tools (e.g. UptimeRobot, BetterUptime):

```bash
curl http://localhost:5000/api/health
```

**Response Example:**
```json
{
  "status": "healthy",
  "service": "PricePilot Analytics Server",
  "version": "2.4.0",
  "database": {
    "connected": true,
    "tracked_products": 10
  },
  "scheduler": {
    "running": true,
    "interval_minutes": 15,
    "last_run": "2026-10-22 18:40:00",
    "next_run": "2026-10-22 18:55:00"
  }
}
```
