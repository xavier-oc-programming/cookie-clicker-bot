"""
cookie_clicker_bot_v7.py

Features:
- Infinite runtime until user types "stop"
- Console commands:
    • 'pause' → pause clicking
    • 'play'  → resume clicking
    • 'stop'  → exit gracefully
- Keeps upgrade/product logic unchanged
"""

import time
import re
import threading
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================================================
# CONFIG
# =========================================================
URL = "https://orteil.dashnet.org/cookieclicker/"
CHECK_INTERVAL = 5
HOVER_PAUSE = 0.2

# =========================================================
# SETUP
# =========================================================
options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=146)
driver.get(URL)

# ---------------------------------------------------------
# Handle GDPR consent popup
# ---------------------------------------------------------
try:
    consent_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".fc-button.fc-cta-consent"))
    )
    consent_btn.click()
    print("Consent dialog accepted.")
except Exception:
    print("No consent popup appeared or already handled.")

wait = WebDriverWait(driver, 30)
actions = ActionChains(driver)

# ---------------------------------------------------------
# Choose English language
# ---------------------------------------------------------
try:
    english_btn = wait.until(EC.element_to_be_clickable((By.ID, "langSelect-EN")))
    english_btn.click()
    print("Language chosen. Waiting for game UI...")
    time.sleep(8)
except Exception:
    print("Could not select English language (maybe already selected).")

# ---------------------------------------------------------
# Locate main cookie
# ---------------------------------------------------------
big_cookie = wait.until(EC.presence_of_element_located((By.ID, "bigCookie")))
print("Bot started. Type 'pause', 'play', or 'stop' in the console at any time.")

# =========================================================
# GLOBAL CONTROL FLAGS
# =========================================================
running = True     # Controls entire program (False = stop)
clicking = True    # Controls clicking state (pause/play)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def parse_number(text: str):
    if not text:
        return None
    text = text.lower().replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*(thousand|million|billion|trillion)?", text)
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2)
    if unit == "thousand":
        num *= 1_000
    elif unit == "million":
        num *= 1_000_000
    elif unit == "billion":
        num *= 1_000_000_000
    elif unit == "trillion":
        num *= 1_000_000_000_000
    return num


def get_current_cookies():
    try:
        el = driver.find_element(By.ID, "cookies")
        first_line = el.text.split("\n")[0]
        val = parse_number(first_line)
        return val or 0
    except Exception:
        return 0


def show_tooltip(el):
    try:
        actions.move_to_element(el).perform()
        time.sleep(HOVER_PAUSE)
    except Exception:
        pass


def get_product_cps_from_tooltip():
    try:
        desc = driver.find_element(By.CSS_SELECTOR, "#tooltipBuilding .descriptionBlock")
        text = desc.text
        m = re.search(r"([\d.,]+)\s+cookies per second", text)
        if m:
            return float(m.group(1).replace(",", ""))
    except Exception:
        return None
    return None

# =========================================================
# UPGRADE LOGIC
# =========================================================
def buy_most_expensive_enabled_upgrade():
    upgrades = driver.find_elements(By.CSS_SELECTOR, "#upgrades .crate.upgrade.enabled")
    if not upgrades:
        return False

    def price_from_upgrade_tooltip(up_el):
        show_tooltip(up_el)
        try:
            tooltip = driver.find_element(By.ID, "tooltip")
            for line in tooltip.text.splitlines():
                if "cookies" in line.lower():
                    return parse_number(line)
        except Exception:
            return None
        return None

    best_el = None
    best_price = -1
    for up in upgrades:
        price = price_from_upgrade_tooltip(up)
        if price is not None and price > best_price:
            best_price = price
            best_el = up

    if best_el is not None:
        try:
            best_el.click()
            print(f"Bought upgrade for {best_price:,.0f}")
            return True
        except Exception:
            pass

    try:
        upgrades[-1].click()
        print("Bought upgrade (fallback rightmost).")
        return True
    except Exception:
        return False

# =========================================================
# PRODUCT LOGIC
# =========================================================
def buy_any_unowned_affordable_product():
    cookies = get_current_cookies()
    products = driver.find_elements(By.CSS_SELECTOR, "#products .product.unlocked")

    cheapest_el = None
    cheapest_price = float("inf")

    for prod in products:
        try:
            owned_el = prod.find_element(By.CSS_SELECTOR, ".content .title.owned")
            owned_text = owned_el.text.strip()
            owned_num = int(re.sub(r"\D", "", owned_text)) if owned_text else 0
        except Exception:
            owned_num = 0

        if owned_num != 0:
            continue

        try:
            price_el = prod.find_element(By.CSS_SELECTOR, ".content .price")
            price = parse_number(price_el.text)
        except Exception:
            price = None

        if price is None:
            continue

        if price <= cookies and price < cheapest_price:
            cheapest_price = price
            cheapest_el = prod

    if cheapest_el is not None:
        try:
            cheapest_el.click()
            print(f"Discovery buy: bought new product for {cheapest_price:,.0f}")
            return True
        except Exception:
            pass

    return False


def collect_product_candidates():
    candidates = []
    products = driver.find_elements(By.CSS_SELECTOR, "#products .product.unlocked")
    for prod in products:
        try:
            price_el = prod.find_element(By.CSS_SELECTOR, ".content .price")
            price = parse_number(price_el.text)
        except Exception:
            price = None
        if price is None:
            continue

        show_tooltip(prod)
        cps = get_product_cps_from_tooltip()
        if cps is None or cps <= 0:
            continue

        payback = price / cps
        candidates.append({"el": prod, "price": price, "cps": cps, "payback": payback})

    return candidates

# =========================================================
# CLICKING THREAD
# =========================================================
def click_forever():
    """Continuously click the big cookie until 'running' is False."""
    while running:
        if clicking:  # Only click if not paused
            try:
                big_cookie.click()
            except Exception:
                pass
        # Prevent CPU overload
        time.sleep(0.0005)

# =========================================================
# COMMAND LISTENER THREAD
# =========================================================
def command_listener():
    """Listens for console commands: pause, play, stop."""
    global running, clicking
    while running:
        cmd = input().strip().lower()
        if cmd == "pause":
            clicking = False
            print("🟡 Paused clicking.")
        elif cmd == "play":
            clicking = True
            print("🟢 Resumed clicking.")
        elif cmd == "stop":
            running = False
            print("🔴 Stopping bot...")
        else:
            print("Commands: pause | play | stop")

# =========================================================
# MAIN LOOP
# =========================================================
# Start threads
threading.Thread(target=click_forever, daemon=True).start()
threading.Thread(target=command_listener, daemon=True).start()

print("\nBot is running indefinitely. Type 'pause', 'play', or 'stop' anytime.\n")

next_check = time.time() + CHECK_INTERVAL

while running:
    now = time.time()
    if now >= next_check:
        next_check = now + CHECK_INTERVAL
        print("\n=== Store check ===")

        _ = buy_most_expensive_enabled_upgrade()
        bought_new = buy_any_unowned_affordable_product()

        if not bought_new:
            products = collect_product_candidates()
            if products:
                products.sort(key=lambda x: x["payback"])
                best = products[0]
                try:
                    best["el"].click()
                    print(
                        f"Bought product: price={best['price']:,.0f}, "
                        f"CPS={best['cps']:.2f}, payback={best['payback']:.2f}s"
                    )
                except Exception:
                    print("Could not click best product.")
            else:
                print("No quantifiable products this round.")

    time.sleep(0.05)

# =========================================================
# CLEANUP
# =========================================================
try:
    cps_el = driver.find_element(By.ID, "cookiesPerSecond")
    print("\nFinished. Cookies per second:", cps_el.text)
except Exception:
    print("\nFinished.")
