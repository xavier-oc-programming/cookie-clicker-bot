# Cookie Clicker Bot

A Selenium bot that automates Cookie Clicker: clicks the cookie, hunts golden cookies, buys upgrades and buildings by CPS payback ratio, and accepts console commands to pause, change the store-check interval, or stop.

Cookie Clicker is a browser-based idle game created by Julien "Orteil" Thiennot in 2013. The entire premise is deceptively simple: there is a large cookie on the left side of the screen — you click it, you get cookies. Cookies are the game's single currency, used to buy buildings (Cursors, Grandmas, Farms, Mines, Factories, and so on) that produce more cookies automatically every second. Each building has a cookies-per-second (CPS) rate, and as your CPS climbs, an upgrade shop on the left unlocks one-time power-ups that multiply the output of specific buildings. Golden cookies occasionally float across the screen; clicking one triggers a timed buff — Frenzy, Click Frenzy, or Lucky — that can multiply your CPS or grant a large cookie bonus for a short window. The loop is: click → earn cookies → buy buildings → earn cookies faster → buy upgrades → earn cookies much faster → catch golden cookie buffs → repeat, scaling from tens of cookies per second to trillions. The game never ends; the goal is simply to push your CPS as high as possible.

Launch the bot and watch it open Chrome, accept the GDPR consent dialog, select English, and start hammering the big cookie in a background thread. Every 5 seconds it pauses to scan the shop: it first snaps up the most expensive available upgrade, then either buys the cheapest unowned building to unlock its CPS bonus (discovery rule), or — when all buildings are already owned — picks the one with the lowest price-to-CPS payback ratio. Golden cookies are clicked automatically; if a buff is active the store check is skipped so no cookies are wasted buying buildings during a multiplier. Type `pause` to suspend all activity, `play` to resume, `interval <time>` to change how often the store is checked, and `stop` to exit cleanly.

There are two builds. The **original** build is the course script (`play_pause_cookie.py`) written as a single procedural file with all constants at the top — exactly as delivered on Day 48. The **advanced** build restructures it into an OOP `CookieClicker` class (`clicker.py`) driven by an orchestrator (`main.py`), with every magic number moved into `config.py`. Both builds implement the same game strategy and the same anti-bot-detection protocol; the difference is structure, testability, and the extra features available in the advanced build.

```
                COOKIE CLICKER BOT
               ~~~~~~~~~~~~~~~~~~~~
            Day 48  |  100 Days of Code
            Selenium Browser Automation

⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠋⠉⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡻⠋⠁⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣻⠋⠀⠀⠀⠠⠖⠋⠉⠀⠀⠀⠀⣾⠉⢳⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡿⡱⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠉⠀⠀⠀⠐⠲⠦⣄⠉⠉⠻⣿⣿⣿⡿⠟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⢱⠁⠀⠀⠀⠀⣠⢤⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡇⡆⠀⠀⠀⠀⠠⠷⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⡿⠿⠿⠻⣿⣿⣿
⣿⣿⣿⣿⣿⠃⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡞⠳⣆⠈⣿⡀⠀⣠⠄⠀⢸⣿⣿
⣿⣿⣿⣿⣿⢰⠁⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⠀⠀⠘⢧⣠⠟⠀⢹⣧⠈⠀⠀⣀⣾⣿⣿
⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⢀⣶⠿⠛⠛⢿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⠟⠛⠻⢷⣄⠀⠀⠀⠀⠀⠀⢸⣷⣶⣶⣿⣿⣿⣿⣿
⣿⣿⣿⣿⡏⠀⠀⠀⠀⢸⠀⠀⠛⠁⠀⠀⠀⠀⠈⠃⠀⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣧⢰⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠛⠛⠛⠉⠉⠉⠉⠙⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡄⡆⠀⠀⠈⠂⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⠀⠀⠀⠀⠀⢠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣸⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⡴⠶⣶⣶⣀⣠⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡤⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡿⠀⠀⠈⢧⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⠙⠻⢥⡤⠞⠉⠀⠀⠀⠀⠀⠀⠀⠀⠐⠚⠉⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣇⡄⠀⡠⠈⢧⣺⣍⠉⣻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠤⢄⡀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⢣⠘⠁⠀⠀⢳⣍⠉⠁⠀⠀⠀⠀⠐⠢⣤⣀⡀⠀⠀⠀⠛⠦⠤⠞⠁⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣯⣢⣄⣀⣀⣼⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⣀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠳⠶⠤⣤⣤⣤⣤⣤⣤⠴⠶⠞⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⢸⣿⣿⣿⣿⡇⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⠀⠔⠒⠚⣿⣿⣿⣿⣴⠀⠠⠔⠚⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣣⣀⡀⢀⣹⣿⣿⣿⣯⣆⡀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
```

---

## Table of Contents

1. [Quick start](#1-quick-start)
2. [Builds comparison](#2-builds-comparison)
3. [Usage](#3-usage)
4. [Data flow](#4-data-flow)
5. [Features](#5-features)
6. [Navigation flow](#6-navigation-flow)
7. [Architecture](#7-architecture)
8. [Module reference](#8-module-reference)
9. [Configuration reference](#9-configuration-reference)
10. [Data schema](#10-data-schema)
11. [Design decisions](#11-design-decisions)
12. [Course context](#12-course-context)
13. [Dependencies](#13-dependencies)

---

## 1. Quick start

```bash
pip install -r requirements.txt
python menu.py       # select 1 (original) or 2 (advanced)

# or run a build directly:
python original/play_pause_cookie.py
python advanced/main.py
```

Chrome must be installed. Selenium 4.6+ downloads ChromeDriver automatically via Selenium Manager.

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| Structure | Single procedural file | OOP — `CookieClicker` class + orchestrator |
| Constants | Inline at top of file | Centralised in `config.py` |
| Anti-bot protocol | CDP `navigator.webdriver` override + 3 ChromeOptions flags | Same |
| Golden cookies | Not handled | Clicked automatically; store check skipped during buff |
| Click interception | `except Exception: pass` | JS fallback on `ElementClickInterceptedException` |
| Click/store race | Can conflict | `threading.Event` pauses click thread during store check |
| Console commands | `pause` / `play` / `stop` | `pause` / `play` / `interval <time>` / `stop` |
| Store-check interval | Fixed (`CHECK_INTERVAL = 5`) | Changeable at runtime with `interval` command |
| Shop strategy | Upgrade → discovery → payback | Same |
| Number parsing | Basic (thousand–trillion) | Extended (thin-space normalisation, quadrillion) |
| Error handling | `except Exception: pass` inline | Exceptions bubble to `main.py`; loop continues |

---

## 3. Usage

Both builds open Chrome, navigate to Cookie Clicker, and start clicking immediately.

```
$ python menu.py

      .::::.
    .:::::::::.
   ::::::::::::      COOKIE CLICKER BOT
  ...

Select a build to run:

  1. Original  — play_pause_cookie.py (course version)
  2. Advanced  — advanced/main.py (OOP, config module)
  q. Quit
```

Once the advanced build is running:

```
Bot ready. Commands:
  pause              pause clicking and store checks
  play               resume
  interval           show current store-check interval
  interval <time>    change it  e.g. 30  30s  2m  1h  2m30s
  stop               exit

=== Store check === (14,970 cookies)
Bought upgrade for 100
Discovery buy: Grandma for 100

Golden cookie! Buff active for ~77s.
Buff active (74s left) — skipping store check.

interval 2m
Store check interval set to 120.0s.

pause
Paused.
play
Resumed.
stop
Stopping bot...

Finished. Cookies per second: 42.3
```

The original build supports `pause` / `play` / `stop` only.

---

## 4. Data flow

```
Launch → Open Chrome → Navigate to URL
       → CDP: hide navigator.webdriver before page script runs
       → Accept GDPR consent popup
       → Select English language
       → Wait for #bigCookie element

Background thread 1 — click_forever:
  wait for click_allowed event (cleared during store checks)
  if not paused:
    click_golden_cookies() → if buff acquired, record buff_until timestamp
    click #bigCookie
  sleep CLICK_SLEEP

Background thread 2 — command_listener:
  'pause'           → clicking = False  (halts clicking and store checks)
  'play'            → clicking = True
  'interval <time>' → check_interval = parse_duration_to_seconds(time)
  'stop'            → running = False

Main thread — store loop (every check_interval seconds):
  if paused → skip
  if buff active → skip (print remaining time)
  else:
    clear click_allowed  (pause click thread)
    sleep 0.05           (let click thread finish current iteration)
    read #cookies text → parse float
    hover each enabled upgrade → read tooltip price
      → click most expensive affordable upgrade
    scan #products for unowned (count == 0) affordable buildings
      → click cheapest (discovery rule)
    if no discovery: hover each product → read tooltip CPS
      → sort by price / CPS → click lowest payback
    set click_allowed    (resume click thread)

On 'stop' command:
  running = False → all threads exit
  read #cookiesPerSecond → print final CPS
```

---

## 5. Features

**Continuous cookie clicking** — A daemon thread clicks the big cookie as fast as possible (`CLICK_SLEEP = 0.0005 s` to limit CPU usage). Clicking is entirely independent of the shop-check logic.

**Anti-bot detection** — Both builds use three `ChromeOptions` flags (`--disable-blink-features=AutomationControlled`, `excludeSwitches: ["enable-automation"]`, `useAutomationExtension: False`) plus a CDP `Page.addScriptToEvaluateOnNewDocument` command that hides `navigator.webdriver` before the page's own JavaScript runs. This bypasses Cloudflare's bot-detection check on the Cookie Clicker site.

**GDPR consent handling** — On first launch, Cookie Clicker shows a consent popup. The bot waits up to 10 seconds for it and dismisses it automatically; if it is absent it continues without error.

**Language selection** — The bot explicitly clicks the English language button and waits 8 seconds for the full game UI to load before proceeding.

**Golden cookie clicking (advanced)** — Before each cookie click, the bot scans for `.shimmer` elements (golden and wrath cookies). If any are found, they are clicked first. A JS fallback is used if the normal click is intercepted. The longest active buff duration is read back from `#buffs .buff` elements.

**Buff-aware store skipping (advanced)** — If a golden cookie buff is active (Frenzy, Click Frenzy, Lucky), the store check is skipped for the duration of the buff so no cookies are spent buying buildings during a multiplier window.

**Click thread pausing during store checks (advanced)** — A `threading.Event` (`click_allowed`) is cleared before each store check and set in the `finally` block after. This prevents the click thread from moving the mouse mid-hover and breaking tooltip reads.

**Upgrade purchasing** — Every store check, the bot hovers over each enabled upgrade to read its tooltip price, then clicks the most expensive one it can find. This prioritises high-value upgrades. Falls back to the rightmost upgrade if tooltip parsing fails.

**Discovery buying** — If any building has never been bought (owned count == 0) and is affordable, the bot buys the cheapest such building first. Unlocking new building types reveals new upgrade slots and multipliers.

**Payback-ratio purchasing** — When all affordable buildings are already owned, the bot hovers each product to read its per-unit CPS from the tooltip, computes `price / CPS` (seconds to recoup the cost), and buys the building with the lowest payback time.

**Runtime interval command (advanced)** — Type `interval <time>` to change how often the store is checked without restarting. Accepts bare seconds (`30`), seconds with unit (`30s`), minutes (`2m`), hours (`1h`), or compound (`2m30s`). Type `interval` alone to print the current value.

**Interactive console commands** — A second daemon thread reads stdin continuously. `pause` suspends both clicking and store checks; `play` resumes; `stop` exits cleanly and prints the final CPS.

**Per-iteration error handling (advanced)** — `check_store()` exceptions are caught in `main.py`'s loop and logged; a single stale element reference does not kill a long-running bot session.

---

## 6. Navigation flow

### a) Terminal menu tree

```
python menu.py
│
├── 1 → original/play_pause_cookie.py
│         └── runs until 'stop' → Press Enter to return to menu
│
├── 2 → advanced/main.py
│         └── runs until 'stop' → Press Enter to return to menu
│
└── q → exit
```

### b) Execution flow (advanced build)

```
Start
  │
  ▼
Open Chrome + navigate to URL
CDP: navigator.webdriver = undefined
  │
  ▼
GDPR popup present?
  ├── Yes → click consent button
  └── No  → continue
  │
  ▼
Language select present?
  ├── Yes → click EN, sleep 8 s
  └── No  → continue
  │
  ▼
Wait for #bigCookie
  │
  ├──[Thread 1: click_forever]──────────────────────────────────────────┐
  │   wait click_allowed event                                           │
  │   if clicking:                                                       │
  │     click_golden_cookies() → record buff_until if buff found        │
  │     bot.click()                                                      │
  │   sleep CLICK_SLEEP                                                  │
  │                                                                      │
  ├──[Thread 2: command_listener]─────────────────────────────────────── ┤
  │   'pause'           → clicking = False                               │
  │   'play'            → clicking = True                                │
  │   'interval <time>' → check_interval = parse_duration_to_seconds()  │
  │   'stop'            → running = False                                │
  │                                                                      │
  └──[Main thread: store loop]────────────────────────────────────────── ┘
      every check_interval seconds:
        if paused → skip
        if buff active → skip (print remaining time)
        else:
          click_allowed.clear()
          sleep 0.05
          buy_best_upgrade()
          buy_discovery_product()  → if bought, skip payback
          buy_best_payback_product()
          click_allowed.set()

      running = False → exit loop
      print final CPS
      End
```

---

## 7. Architecture

```
cookie-clicker-bot/
├── menu.py                  # Entry point: build selector menu
├── art.py                   # LOGO ASCII art
├── requirements.txt         # pip dependencies + Python version note
├── .gitignore
├── README.md
│
├── docs/
│   └── COURSE_NOTES.md      # Original exercise description + concept list
│
├── original/
│   └── play_pause_cookie.py # Course script (procedural, single file)
│
└── advanced/
    ├── config.py            # All constants — URLs, selectors, timing
    ├── clicker.py           # CookieClicker class — WebDriver + game logic
    └── main.py              # Orchestrator — threads, interval command, error handling
```

---

## 8. Module reference

### `advanced/clicker.py` — class `CookieClicker`

| Method | Returns | Description |
|---|---|---|
| `__init__()` | — | Opens Chrome, hides `navigator.webdriver`, accepts consent, selects English, locates `#bigCookie` |
| `click()` | `None` | Clicks the big cookie; JS fallback on `ElementClickInterceptedException` |
| `click_golden_cookies()` | `float \| None` | Clicks all `.shimmer` elements; returns longest buff duration or `None` |
| `_get_buff_duration()` | `float \| None` | Reads longest active buff time from `#buffs .buff` elements |
| `get_cookie_count()` | `float` | Reads and parses the current cookie counter; returns `0.0` on error |
| `get_cps()` | `str` | Reads the cookies-per-second display string; returns `""` on error |
| `check_store()` | `None` | Runs one full store-check cycle: upgrade → discovery → payback |
| `_buy_best_upgrade()` | `bool` | Buys the highest-priced enabled upgrade; `True` if purchased |
| `_upgrade_price(up_el)` | `float \| None` | Hovers an upgrade element and parses its tooltip price |
| `_buy_discovery_product()` | `bool` | Buys cheapest unowned affordable building; `True` if purchased |
| `_buy_best_payback_product()` | `bool` | Buys building with lowest price/CPS ratio; `True` if purchased |
| `_owned_count(prod_el)` | `int` | Reads owned count from a product element's title |
| `_product_name(prod_el)` | `str` | Reads product name for console logging |
| `_product_price(prod_el)` | `float \| None` | Reads price from a product element |
| `_tooltip_cps()` | `float \| None` | Parses "N cookies per second" from the building tooltip |
| `_parse_number(text)` | `float \| None` | Converts "65 million", "2.5 quadrillion", "14,970" strings to float |

### `advanced/main.py`

| Function | Description |
|---|---|
| `main()` | Entry point — creates bot, starts threads, runs store loop |
| `parse_duration_to_seconds(value)` | Converts `"30"`, `"30s"`, `"2m"`, `"1h"`, `"2m30s"` to a float in seconds |

---

## 9. Configuration reference

All constants live in [advanced/config.py](advanced/config.py).

| Constant | Default | Description |
|---|---|---|
| `URL` | `https://orteil.dashnet.org/cookieclicker/` | Game URL |
| `COOKIE_ID` | `"bigCookie"` | Element ID of the main cookie |
| `COOKIES_DISPLAY_ID` | `"cookies"` | Element ID of the cookie counter |
| `CPS_DISPLAY_ID` | `"cookiesPerSecond"` | Element ID of the CPS display |
| `LANGUAGE_BTN_ID` | `"langSelect-EN"` | Element ID of the English language button |
| `CONSENT_BTN_CSS` | `".fc-button.fc-cta-consent"` | CSS selector for the GDPR consent button |
| `UPGRADES_CSS` | `"#upgrades .crate.upgrade.enabled"` | CSS selector for available upgrades |
| `PRODUCTS_CSS` | `"#products .product.unlocked"` | CSS selector for unlocked buildings |
| `TOOLTIP_ID` | `"tooltip"` | Element ID of the upgrade tooltip |
| `TOOLTIP_BUILDING_DESC_CSS` | `"#tooltipBuilding .descriptionBlock"` | CSS selector for building tooltip description |
| `PRODUCT_PRICE_CSS` | `".content .price"` | CSS selector for product price within a product element |
| `PRODUCT_OWNED_CSS` | `".content .title.owned"` | CSS selector for owned count within a product element |
| `PRODUCT_NAME_CSS` | `".content .title.productName"` | CSS selector for product name within a product element |
| `GOLDEN_COOKIE_CSS` | `".shimmer"` | CSS selector for golden/wrath cookies |
| `BUFFS_CSS` | `"#buffs .buff"` | CSS selector for active buff elements |
| `CHECK_INTERVAL` | `5` | Default seconds between store checks (changeable at runtime) |
| `HOVER_PAUSE` | `0.2` | Seconds to wait after hovering for tooltip to render |
| `CLICK_SLEEP` | `0.0005` | Seconds between cookie clicks (limits CPU load) |
| `MAIN_POLL` | `0.05` | Seconds between main-loop iterations |
| `CONSENT_WAIT` | `10` | Max seconds to wait for the GDPR popup |
| `DRIVER_WAIT` | `30` | Max seconds for `WebDriverWait` on game elements |
| `LANGUAGE_SLEEP` | `8` | Seconds to wait for game UI after language selection |

---

## 10. Data schema

### Cookie counter text (raw DOM, `#cookies`)

```
14,970 cookies
per second : 42.3
```

First line only is parsed. Commas are stripped; thin spaces are normalised; multiplier suffixes (`thousand`, `million`, `billion`, `trillion`, `quadrillion`) are expanded to full floats.

### Upgrade tooltip text (raw DOM, `#tooltip`)

```
Reinforced index finger
Costs 100 cookies
...
```

The line containing `"cookies"` is parsed for the price.

### Building tooltip text (raw DOM, `#tooltipBuilding .descriptionBlock`)

```
Each grandma produces 4 cookies per second
```

Two patterns are tried in order:
1. `each .* produces N cookies per second` — specific per-unit CPS
2. `N cookies per second` — fallback for any match in the description

### Buff element (raw DOM, `#buffs .buff`)

Buff duration is read from `data-timer` attribute first (raw seconds as a float string), then falls back to parsing `"for N seconds"` from `data-tooltip`.

### Product candidate dict (internal, `_buy_best_payback_product`)

```python
{
    "el":      <WebElement>,   # Selenium element reference
    "name":    str,            # product name for console logging
    "price":   float,          # cost in cookies
    "cps":     float,          # cookies per second this building produces
    "payback": float,          # price / cps — seconds to recoup cost
}
```

---

## 11. Design decisions

**CDP `navigator.webdriver` override before `driver.get()`.** `Page.addScriptToEvaluateOnNewDocument` registers a script that runs on every new document load before the page's own JavaScript. Calling it after `driver.get()` would be too late — the page script would have already read `navigator.webdriver = true`. Both builds register it immediately after `webdriver.Chrome()`.

**`config.py` — zero magic numbers.** Every URL, selector, and timing value has a name. When Cookie Clicker updates its CSS classes, one-line fixes in `config.py` propagate everywhere instead of requiring a grep-and-replace across files.

**Separate `CookieClicker` class.** All DOM interaction is isolated in one place. The threading model, command listener, and loop timing in `main.py` can be changed without touching the game logic, and vice versa.

**`threading.Event` instead of a bare flag for click pausing.** Using a boolean flag to pause the click thread during store checks would require the click thread to poll it in a tight loop. `click_allowed.wait()` blocks with zero CPU until the event is set, and `click_allowed.clear()` + `time.sleep(0.05)` guarantees the click thread has finished its current iteration before hovering begins.

**`check_interval` as a one-element list.** The interval is mutated by `command_listener`, which is a closure. A one-element list gives the closure a mutable cell without `nonlocal`. The main loop always reads `check_interval[0]` so changes take effect on the next cycle.

**Buff skipping over store checks.** During a Frenzy or Click Frenzy buff, every cookie click is worth several times its normal value. Running a store check (which pauses clicking for several seconds of hovering) during a buff would waste the multiplier window. The bot reads the buff expiry time and skips store checks until it passes.

**`clicker.py` raises exceptions instead of `sys.exit()`.** The class has no opinion on how failures should be handled. `main.py` catches `check_store()` exceptions per iteration and logs them — a single stale element reference does not kill a long-running session.

**`sys.path.insert` in `main.py`.** Allows both `python advanced/main.py` (from the project root) and `subprocess.run` via `menu.py` to resolve sibling imports without a package install.

**`subprocess.run` + `cwd=path.parent` in `menu.py`.** Each build runs in its own directory so relative imports and any future file-path operations resolve correctly regardless of where `menu.py` is launched from.

**`running` and `clicking` as one-element lists.** Both are mutated inside `command_listener`, which is a closure. Python closures can read enclosing-scope variables but cannot rebind them without `nonlocal`. A one-element list (`running: list[bool] = [True]`) gives the closure a mutable cell without requiring `nonlocal` declarations.

---

## 12. Course context

Built as Day 48 of 100 Days of Code by Dr. Angela Yu.

**Concepts covered in the original build:**
- Selenium `webdriver.Chrome`, `ChromeOptions`
- `WebDriverWait` + `expected_conditions` for reliable element detection
- `By.CSS_SELECTOR`, `By.ID` element location
- `ActionChains.move_to_element` for tooltip triggering
- `threading.Thread` for concurrent clicking and store-check loops
- `re.search` for parsing game text into numbers
- `time.sleep` for rate-limiting and UI synchronisation

**The advanced build extends into:**
- OOP encapsulation — `CookieClicker` class with clear public/private boundary
- Configuration module pattern — all constants in one place
- Exception propagation — modules raise, orchestrator handles
- `threading.Event` for fine-grained thread coordination
- Mutable closure cells as an alternative to `nonlocal`
- Runtime-configurable parameters via console commands
- Human-friendly duration parsing (`parse_duration_to_seconds`)

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for full concept breakdown.

---

## 13. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `selenium` | both builds | WebDriver, element location, `ActionChains`, `WebDriverWait`, CDP commands |
| `threading` | both builds | Background clicking thread, command-listener thread, `Event` for click pausing |
| `re` | both builds | Parse human-readable cookie counts, CPS values, and duration strings from text |
| `time` | both builds | `sleep` for rate-limiting, tooltip waits, and language-load wait |
| `subprocess` | `menu.py` | Launch each build as a child process |
| `sys` | `menu.py`, `advanced/main.py` | `sys.executable` for correct Python path; `sys.path.insert` for imports |
| `pathlib` | `menu.py`, `advanced/main.py` | `Path(__file__).parent` for portable file paths |
| `os` | `menu.py` | `os.system("clear")` / `os.system("cls")` for console clearing |
