# Cookie Clicker Bot

A Selenium bot that automates Cookie Clicker: clicks the cookie, buys upgrades and buildings by CPS payback ratio, and accepts console commands to pause, play, or stop.

Cookie Clicker is a browser-based idle game created by Julien "Orteil" Thiennot in 2013. The entire premise is deceptively simple: there is a large cookie on the left side of the screen — you click it, you get cookies. Cookies are the game's single currency, used to buy buildings (Cursors, Grandmas, Farms, Mines, Factories, and so on) that produce more cookies automatically every second. Each building has a cookies-per-second (CPS) rate, and as your CPS climbs, an upgrade shop on the left unlocks one-time power-ups that multiply the output of specific buildings. The loop is: click → earn cookies → buy buildings → earn cookies faster → buy upgrades → earn cookies much faster → repeat, scaling from tens of cookies per second to trillions. The game never ends; the goal is simply to push your CPS as high as possible.

Launch the bot and watch it open Chrome, accept the GDPR consent dialog, select English, and start hammering the big cookie in a background thread. Every 5 seconds it pauses to scan the shop: it first snaps up the most expensive available upgrade, then either buys the cheapest unowned building to unlock its CPS bonus (discovery rule), or — when all buildings are already owned — picks the one with the lowest price-to-CPS payback ratio. Type `pause` in the terminal to suspend clicking, `play` to resume, and `stop` to exit cleanly and print your final cookies-per-second score.

There are two builds. The **original** build is the course script (`play_pause_cookie.py`) written as a single procedural file with all constants at the top — exactly as delivered on Day 48. The **advanced** build restructures it into an OOP `CookieClicker` class (`clicker.py`) driven by an orchestrator (`main.py`), with every magic number moved into `config.py`. Both builds implement the same game strategy; the difference is structure, testability, and maintainability.

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
| Threading | `threading.Thread` (bare) | Same, via `main.py` orchestrator |
| Console commands | `pause` / `play` / `stop` | `pause` / `play` / `stop` |
| Shop strategy | Upgrade → discovery → payback | Upgrade → discovery → payback |
| Error handling | `except Exception: pass` inline | Exceptions bubble to `main.py`; loop continues |
| Run mode | Infinite until `stop` | Infinite until `stop` |

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

Once a build is running:

```
Bot ready. Type 'pause', 'play', or 'stop' at any time.

=== Store check ===
Bought upgrade for 100
Discovery buy: bought new product for 15

pause
Paused clicking.
play
Resumed clicking.
stop
Stopping bot...

Finished. Cookies per second: 42.3
```

---

## 4. Data flow

```
Launch → Open Chrome → Navigate to URL
       → Accept GDPR consent popup
       → Select English language
       → Wait for #bigCookie element

Background thread: click #bigCookie in tight loop (every 0.5 ms)

Every 5 s (CHECK_INTERVAL):
  Read #cookies text → parse float
  Hover over each enabled upgrade → read tooltip price
    → click most expensive affordable upgrade
  Scan #products for unowned (count == 0) affordable buildings
    → click cheapest (discovery rule)
  If no discovery: hover each product → read tooltip CPS
    → sort by price / CPS → click lowest payback

On 'stop' command:
  Set running[0] = False → threads exit
  Read #cookiesPerSecond → print final CPS
```

---

## 5. Features

**Continuous cookie clicking** — A daemon thread clicks the big cookie as fast as possible (configurable `CLICK_SLEEP` to limit CPU usage). Clicking is entirely independent of the shop-check logic.

**GDPR consent handling** — On first launch, Cookie Clicker shows a consent popup. The bot waits up to 10 seconds for it and dismisses it automatically; if it is absent it continues without error.

**Language selection** — The bot explicitly clicks the English language button and waits 8 seconds for the full game UI to load before proceeding.

**Upgrade purchasing** — Every store check, the bot hovers over each enabled upgrade to read its tooltip price, then clicks the most expensive one it can find. This prioritises high-value upgrades. Falls back to the rightmost upgrade if tooltip parsing fails.

**Discovery buying (advanced-only logic, present in both builds)** — If any building has never been bought (owned count == 0) and is affordable, the bot buys the cheapest such building first. Unlocking new building types reveals new upgrade slots and multipliers.

**Payback-ratio purchasing** — When all affordable buildings are already owned, the bot hovers each product to read its per-unit CPS from the tooltip, computes `price / CPS` (seconds to recoup the cost), and buys the building with the lowest payback time.

**Interactive console commands** — A second daemon thread reads stdin continuously. Type `pause` to stop clicking (useful for manual intervention), `play` to resume, and `stop` to exit cleanly. Invalid commands print a reminder of available options.

**Per-iteration error handling (advanced build)** — `check_store()` exceptions are caught in `main.py`'s loop and logged; a single DOM glitch does not kill the bot.

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

### b) Execution flow

```
Start
  │
  ▼
Open Chrome + navigate to URL
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
  ├──[Thread 1: click_forever]──────────────────────────────────────┐
  │   while running:                                                 │
  │     if clicking: bot.click()                                     │
  │     sleep 0.0005 s                                               │
  │                                                                  │
  ├──[Thread 2: command_listener]────────────────────────────────────┤
  │   'pause' → clicking = False                                     │
  │   'play'  → clicking = True                                      │
  │   'stop'  → running = False                                      │
  │                                                                  │
  └──[Main thread: store loop]───────────────────────────────────────┘
      every CHECK_INTERVAL seconds:
        buy_best_upgrade()
          hover each enabled upgrade → parse tooltip price
          click most expensive → fallback to rightmost
        buy_discovery_product()
          find unowned affordable buildings → click cheapest
          → if purchased, skip payback step
        buy_best_payback_product()
          hover each product → parse CPS from tooltip
          compute price/CPS → click lowest payback
        on exception → log and continue

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
│   └── play_pause_cookie.py # Course script verbatim (v7)
│
└── advanced/
    ├── config.py            # All constants — URLs, selectors, timing
    ├── clicker.py           # CookieClicker class — WebDriver + game logic
    └── main.py              # Orchestrator — threads, command loop, error handling
```

---

## 8. Module reference

### `advanced/clicker.py` — class `CookieClicker`

| Method | Returns | Description |
|---|---|---|
| `__init__()` | — | Opens Chrome, accepts consent, selects English, locates `#bigCookie` |
| `click()` | `None` | Clicks the big cookie once; silently ignores stale-element errors |
| `get_cookie_count()` | `float` | Reads and parses the current cookie counter; returns `0.0` on error |
| `get_cps()` | `str` | Reads the cookies-per-second display string; returns `""` on error |
| `check_store()` | `None` | Runs one full store-check cycle: upgrade → discovery → payback |
| `_buy_best_upgrade()` | `bool` | Buys the highest-priced enabled upgrade; `True` if purchased |
| `_buy_discovery_product()` | `bool` | Buys cheapest unowned affordable building; `True` if purchased |
| `_buy_best_payback_product()` | `bool` | Buys building with lowest price/CPS ratio; `True` if purchased |
| `_upgrade_price(up_el)` | `float \| None` | Hovers an upgrade element and parses its tooltip price |
| `_owned_count(prod_el)` | `int` | Reads owned count from a product element's title |
| `_product_price(prod_el)` | `float \| None` | Reads price from a product element |
| `_tooltip_cps()` | `float \| None` | Parses "N cookies per second" from the building tooltip |
| `_parse_number(text)` | `float \| None` | Converts "65 million" or "14,970" strings to float |

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
| `CHECK_INTERVAL` | `5` | Seconds between store checks |
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

First line only is parsed. Commas are stripped; multiplier suffixes (`thousand`, `million`, `billion`, `trillion`) are expanded to full floats.

### Upgrade tooltip text (raw DOM, `#tooltip`)

```
Reinforced index finger
Costs 100 cookies
...
```

The line containing `"cookies"` is parsed for the price.

### Building tooltip text (raw DOM, `#tooltipBuilding .descriptionBlock`)

```
Each cursor produces 0.1 cookies per second
```

The pattern `([\d.,]+) cookies per second` is extracted as the per-unit CPS.

### Product candidate dict (internal, `_buy_best_payback_product`)

```python
{
    "el":      <WebElement>,   # Selenium element reference
    "price":   float,          # cost in cookies
    "cps":     float,          # cookies per second this building produces
    "payback": float,          # price / cps — seconds to recoup cost
}
```

---

## 11. Design decisions

**`config.py` — zero magic numbers.** Every URL, selector, and timing value has a name. When Cookie Clicker updates its CSS classes (it has), one-line fixes in `config.py` propagate everywhere instead of requiring a grep-and-replace across files.

**Separate `CookieClicker` class.** All DOM interaction is isolated in one place. The threading model, command listener, and loop timing in `main.py` can be changed without touching the game logic, and vice versa.

**`clicker.py` raises exceptions instead of `sys.exit()`.** The class has no opinion on how failures should be handled. `main.py` catches `check_store()` exceptions per iteration and logs them — a single stale element reference does not kill a long-running bot session.

**`sys.path.insert` in `main.py`.** Allows both `python advanced/main.py` (from the project root) and `subprocess.run` via `menu.py` to resolve sibling imports without a package install.

**`subprocess.run` + `cwd=path.parent` in `menu.py`.** Each build runs in its own directory, so relative imports and any future file-path operations resolve correctly regardless of where `menu.py` is launched from.

**`while True` in `menu.py` vs recursion.** Recursion would grow the call stack with every menu return. The loop approach is flat and runs indefinitely without risk of a stack overflow.

**Console cleared before every menu render, not after invalid input.** Invalid input prints an error message; clearing immediately would erase it before the user can read it. `clear = False` on the invalid-input path preserves the message for one cycle.

**`input("\nPress Enter to return to menu...")` after `subprocess.run`.** The bot process may print errors as it exits. The pause keeps them visible so the user can read them before the screen clears on the next menu render.

**`running` and `clicking` as one-element lists.** Both are mutated inside `command_listener`, which is a closure. Python closures can read enclosing-scope variables but cannot rebind them without `nonlocal`. A one-element list (`running: list[bool] = [True]`) gives the closure a mutable cell without requiring `nonlocal` declarations.

**`time.sleep(CLICK_SLEEP)` in the clicking thread.** Without any sleep, the clicking thread saturates one CPU core. `0.0005 s` (0.5 ms) keeps CPU usage reasonable while still clicking ~2,000 times per second — far faster than any human.

**`try/except per store-check iteration, not around the whole loop.** Wrapping the entire `while running` loop in a single try/except would silently swallow errors and make debugging impossible. Per-iteration handling logs the error and continues, keeping the bot alive through transient DOM issues.

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
- Mutable closure cells as an alternative to `nonlocal`

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for full concept breakdown.

---

## 13. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `selenium` | both builds | WebDriver, element location, `ActionChains`, `WebDriverWait` |
| `threading` | both builds | Background clicking thread and command-listener thread |
| `re` | both builds | Parse human-readable cookie counts and CPS values from DOM text |
| `time` | both builds | `sleep` for rate-limiting, tooltip waits, and language-load wait |
| `subprocess` | `menu.py` | Launch each build as a child process |
| `sys` | `menu.py`, `advanced/main.py` | `sys.executable` for correct Python path; `sys.path.insert` for imports |
| `pathlib` | `menu.py`, `advanced/main.py` | `Path(__file__).parent` for portable file paths |
| `os` | `menu.py` | `os.system("clear")` / `os.system("cls")` for console clearing |
