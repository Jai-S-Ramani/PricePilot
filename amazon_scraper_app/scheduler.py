import time
import threading
import datetime
import logging
from typing import Dict, Any

# Configure logger
logger = logging.getLogger("PriceScheduler")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class BackgroundPriceScheduler:
    """
    Thread-safe background daemon that periodically checks all tracked Amazon products,
    updates prices, logs historical data points, and triggers automated email alerts.
    """

    def __init__(self, interval_minutes: int = 30):
        self.interval_seconds = max(60, interval_minutes * 60)
        self.interval_minutes = interval_minutes
        self._stop_event = threading.Event()
        self._thread = None
        self._lock = threading.Lock()
        
        # State tracking
        self.is_running = False
        self.last_run_time = None
        self.next_run_time = None
        self.total_runs_completed = 0
        self.last_items_checked = 0
        self.last_status_message = "Initialized. Ready to start."

    def start(self):
        """Starts the background scheduler thread."""
        with self._lock:
            if self.is_running:
                logger.info("Scheduler already running.")
                return

            self._stop_event.clear()
            self.is_running = True
            self.next_run_time = (
                datetime.datetime.now() + datetime.timedelta(seconds=self.interval_seconds)
            ).strftime("%Y-%m-%d %H:%M:%S")
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="PriceSchedulerThread")
            self._thread.start()
            self.last_status_message = f"Scheduler active. Monitoring every {self.interval_minutes} minutes."
            logger.info("BackgroundPriceScheduler started.")

    def stop(self):
        """Signals the background thread to stop cleanly."""
        with self._lock:
            if not self.is_running:
                return
            self.is_running = False
            self._stop_event.set()
            self.next_run_time = None
            self.last_status_message = "Scheduler stopped."
            logger.info("BackgroundPriceScheduler stopped.")

    def set_interval(self, minutes: int):
        """Updates the check frequency in minutes."""
        with self._lock:
            self.interval_minutes = max(1, int(minutes))
            self.interval_seconds = self.interval_minutes * 60
            if self.is_running:
                self.next_run_time = (
                    datetime.datetime.now() + datetime.timedelta(seconds=self.interval_seconds)
                ).strftime("%Y-%m-%d %H:%M:%S")
            self.last_status_message = f"Interval updated to {self.interval_minutes} minutes."
            logger.info(f"Scheduler interval updated to {self.interval_minutes}m.")

    def trigger_now(self) -> Dict[str, Any]:
        """Runs an immediate background check without waiting for the timer."""
        def _manual_worker():
            self._execute_check_cycle(source="Manual Trigger")

        t = threading.Thread(target=_manual_worker, daemon=True, name="ManualScrapeTrigger")
        t.start()
        return {"status": "success", "message": "Manual check initiated in background"}

    def get_status(self) -> Dict[str, Any]:
        """Returns the current operational status of the scheduler."""
        with self._lock:
            return {
                "running": self.is_running,
                "interval_minutes": self.interval_minutes,
                "last_run": self.last_run_time or "Never",
                "next_run": self.next_run_time or "Paused",
                "total_runs": self.total_runs_completed,
                "last_items_checked": self.last_items_checked,
                "status_message": self.last_status_message
            }

    def _run_loop(self):
        """Internal daemon loop that waits for interval and executes cycles."""
        logger.info("Background scheduler loop entered.")
        while not self._stop_event.is_set():
            # Wait for either timeout or stop signal
            interrupted = self._stop_event.wait(timeout=self.interval_seconds)
            if interrupted or not self.is_running:
                break

            self._execute_check_cycle(source="Automated Timer")

            with self._lock:
                self.next_run_time = (
                    datetime.datetime.now() + datetime.timedelta(seconds=self.interval_seconds)
                ).strftime("%Y-%m-%d %H:%M:%S")

    def _execute_check_cycle(self, source: str = "Automated"):
        """Performs scraping across all products and fires user alerts."""
        start_time = datetime.datetime.now()
        logger.info(f"[{source}] Starting price check sweep...")

        try:
            # Delayed imports to avoid circular dependencies
            from database import (
                get_all_products, save_or_update_product,
                get_db_connection, process_auto_alerts_for_user
            )
            from scraper import scrape_amazon_product

            products = get_all_products()
            checked_count = 0
            updated_count = 0

            from concurrent.futures import ThreadPoolExecutor, as_completed

            def _check_single(prod):
                try:
                    url = prod.get("url")
                    if not url:
                        return False
                    # Scrape updated product info
                    scraped = scrape_amazon_product(url)
                    scraped["target_price"] = prod.get("target_price")
                    scraped["user_id"] = prod.get("user_id")

                    # Persist updated prices and append to price_history
                    save_or_update_product(scraped, user_id=prod.get("user_id"))
                    return True
                except Exception as item_err:
                    logger.warning(f"Error checking product {prod.get('id')}: {item_err}")
                    return False

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(_check_single, p) for p in products]
                for f in as_completed(futures):
                    if f.result():
                        checked_count += 1
                        updated_count += 1

            # Now evaluate auto alerts across all registered users
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE auto_alerts_enabled = 1")
            user_rows = cursor.fetchall()
            conn.close()

            total_alerts_fired = 0
            for u in user_rows:
                try:
                    alerts = process_auto_alerts_for_user(u["id"])
                    total_alerts_fired += len(alerts)
                except Exception as alert_err:
                    logger.warning(f"Error checking alerts for user {u['id']}: {alert_err}")

            finish_time = datetime.datetime.now()
            duration = (finish_time - start_time).total_seconds()

            with self._lock:
                self.last_run_time = finish_time.strftime("%Y-%m-%d %H:%M:%S")
                self.last_items_checked = checked_count
                self.total_runs_completed += 1
                self.last_status_message = (
                    f"Last sweep completed in {duration:.1f}s ({checked_count} items checked, {total_alerts_fired} alerts dispatched)."
                )

            logger.info(f"[{source}] Sweep finished. {checked_count} checked, {total_alerts_fired} alerts fired in {duration:.1f}s.")

        except Exception as e:
            logger.error(f"[{source}] Scheduler sweep encountered an error: {e}", exc_info=True)
            with self._lock:
                self.last_status_message = f"Last sweep encountered error: {str(e)[:80]}"


# Global singleton instance
price_scheduler = BackgroundPriceScheduler(interval_minutes=30)
