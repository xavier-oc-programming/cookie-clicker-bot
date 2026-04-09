# Browser
CHROME_VERSION = 146    # must match your installed Chrome major version

# API / URLs
URL = "https://orteil.dashnet.org/cookieclicker/"

# CSS Selectors / Element IDs
COOKIE_ID = "bigCookie"
COOKIES_DISPLAY_ID = "cookies"
CPS_DISPLAY_ID = "cookiesPerSecond"
LANGUAGE_BTN_ID = "langSelect-EN"
CONSENT_BTN_CSS = ".fc-button.fc-cta-consent"
UPGRADES_CSS = "#upgrades .crate.upgrade.enabled"
PRODUCTS_CSS = "#products .product.unlocked"
TOOLTIP_ID = "tooltip"
TOOLTIP_BUILDING_DESC_CSS = "#tooltipBuilding .descriptionBlock"
PRODUCT_PRICE_CSS = ".content .price"
PRODUCT_OWNED_CSS = ".content .title.owned"

# Timing / rate limits
CHECK_INTERVAL = 5      # seconds between store checks
HOVER_PAUSE = 0.2       # seconds to wait after hovering for tooltip to render
CLICK_SLEEP = 0.0005    # seconds between cookie clicks (limits CPU load)
MAIN_POLL = 0.05        # seconds between main-loop iterations
CONSENT_WAIT = 10       # max seconds to wait for GDPR consent popup
DRIVER_WAIT = 30        # max seconds for WebDriverWait on game elements
LANGUAGE_SLEEP = 8      # seconds to wait for game UI after language selection
