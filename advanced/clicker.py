import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config


class CookieClicker:
    """
    Manages the Selenium WebDriver and all in-game actions.

    Handles browser setup, GDPR consent, language selection, cookie
    clicking, and shop decisions. Pure logic — no print() calls,
    no threading, no I/O. Raises exceptions on unrecoverable errors;
    main.py decides how to handle them.
    """

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=options)
        self.actions = ActionChains(self.driver)
        self._setup()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup(self):
        """Open the game, accept consent, select English, locate cookie."""
        self.driver.get(config.URL)

        try:
            consent_btn = WebDriverWait(self.driver, config.CONSENT_WAIT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, config.CONSENT_BTN_CSS))
            )
            consent_btn.click()
        except Exception:
            pass  # popup absent or already dismissed

        wait = WebDriverWait(self.driver, config.DRIVER_WAIT)

        try:
            lang_btn = wait.until(
                EC.element_to_be_clickable((By.ID, config.LANGUAGE_BTN_ID))
            )
            lang_btn.click()
            time.sleep(config.LANGUAGE_SLEEP)
        except Exception:
            pass  # already set to English

        self.big_cookie = wait.until(
            EC.presence_of_element_located((By.ID, config.COOKIE_ID))
        )

    # ------------------------------------------------------------------
    # Clicking
    # ------------------------------------------------------------------

    def click(self):
        """Click the big cookie once. Silently ignores stale-element errors."""
        try:
            self.big_cookie.click()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # State reading
    # ------------------------------------------------------------------

    def get_cookie_count(self) -> float:
        """Return current cookie count as a float (0.0 on error)."""
        try:
            el = self.driver.find_element(By.ID, config.COOKIES_DISPLAY_ID)
            first_line = el.text.split("\n")[0]
            return self._parse_number(first_line) or 0.0
        except Exception:
            return 0.0

    def get_cps(self) -> str:
        """Return the cookies-per-second display string (empty string on error)."""
        try:
            return self.driver.find_element(By.ID, config.CPS_DISPLAY_ID).text
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Shop
    # ------------------------------------------------------------------

    def check_store(self) -> None:
        """
        Run one store-check cycle:
          1. Buy the most expensive enabled upgrade.
          2. Buy the cheapest unowned affordable product (discovery rule).
          3. If no discovery buy, buy the product with the best CPS payback ratio.
        """
        self._buy_best_upgrade()
        if not self._buy_discovery_product():
            self._buy_best_payback_product()

    def _buy_best_upgrade(self) -> bool:
        """Buy the highest-priced enabled upgrade. Returns True if purchased."""
        upgrades = self.driver.find_elements(By.CSS_SELECTOR, config.UPGRADES_CSS)
        if not upgrades:
            return False

        best_el, best_price = None, -1
        for up in upgrades:
            price = self._upgrade_price(up)
            if price is not None and price > best_price:
                best_price, best_el = price, up

        target = best_el if best_el is not None else upgrades[-1]
        try:
            target.click()
            return True
        except Exception:
            return False

    def _upgrade_price(self, up_el) -> float | None:
        """Hover over an upgrade element and parse its price from the tooltip."""
        try:
            self.actions.move_to_element(up_el).perform()
            time.sleep(config.HOVER_PAUSE)
            tooltip = self.driver.find_element(By.ID, config.TOOLTIP_ID)
            for line in tooltip.text.splitlines():
                if "cookies" in line.lower():
                    return self._parse_number(line)
        except Exception:
            pass
        return None

    def _buy_discovery_product(self) -> bool:
        """
        Buy the cheapest unowned (count == 0) affordable product.
        Returns True if a product was purchased.
        """
        cookies = self.get_cookie_count()
        products = self.driver.find_elements(By.CSS_SELECTOR, config.PRODUCTS_CSS)
        cheapest_el, cheapest_price = None, float("inf")

        for prod in products:
            if self._owned_count(prod) != 0:
                continue
            price = self._product_price(prod)
            if price is None:
                continue
            if price <= cookies and price < cheapest_price:
                cheapest_price, cheapest_el = price, prod

        if cheapest_el is not None:
            try:
                cheapest_el.click()
                return True
            except Exception:
                pass
        return False

    def _buy_best_payback_product(self) -> bool:
        """
        Buy the unlocked product with the lowest price/CPS payback ratio.
        Returns True if a product was purchased.
        """
        candidates = []
        for prod in self.driver.find_elements(By.CSS_SELECTOR, config.PRODUCTS_CSS):
            price = self._product_price(prod)
            if price is None:
                continue
            self.actions.move_to_element(prod).perform()
            time.sleep(config.HOVER_PAUSE)
            cps = self._tooltip_cps()
            if cps is None or cps <= 0:
                continue
            candidates.append({"el": prod, "price": price, "cps": cps,
                                "payback": price / cps})

        if not candidates:
            return False

        best = min(candidates, key=lambda x: x["payback"])
        try:
            best["el"].click()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # DOM helpers
    # ------------------------------------------------------------------

    def _owned_count(self, prod_el) -> int:
        try:
            text = prod_el.find_element(
                By.CSS_SELECTOR, config.PRODUCT_OWNED_CSS
            ).text.strip()
            return int(re.sub(r"\D", "", text)) if text else 0
        except Exception:
            return 0

    def _product_price(self, prod_el) -> float | None:
        try:
            return self._parse_number(
                prod_el.find_element(By.CSS_SELECTOR, config.PRODUCT_PRICE_CSS).text
            )
        except Exception:
            return None

    def _tooltip_cps(self) -> float | None:
        try:
            desc = self.driver.find_element(
                By.CSS_SELECTOR, config.TOOLTIP_BUILDING_DESC_CSS
            )
            m = re.search(r"([\d.,]+)\s+cookies per second", desc.text)
            if m:
                return float(m.group(1).replace(",", ""))
        except Exception:
            pass
        return None

    @staticmethod
    def _parse_number(text: str) -> float | None:
        """Convert '14,970 cookies' or '65 million' into a float."""
        if not text:
            return None
        text = text.lower().replace(",", "").strip()
        m = re.search(r"([\d.]+)\s*(thousand|million|billion|trillion)?", text)
        if not m:
            return None
        num = float(m.group(1))
        multipliers = {
            "thousand": 1_000,
            "million": 1_000_000,
            "billion": 1_000_000_000,
            "trillion": 1_000_000_000_000,
        }
        num *= multipliers.get(m.group(2), 1)
        return num
