# Course Notes — Day 48

**Course:** 100 Days of Code: The Complete Python Pro Bootcamp  
**Instructor:** Dr. Angela Yu  
**Topic:** Selenium Browser Automation — Game Bot (Part 2)

## Exercise description

Use Selenium to automate the browser game Cookie Clicker
(https://orteil.dashnet.org/cookieclicker/).

The bot must:
- Click the big cookie as fast as possible
- Periodically check the shop for upgrades and buildings
- Decide what to buy to maximise cookies per second (CPS)
- Run for a fixed time window (original task: 5 minutes) then report final CPS

## Concepts covered

- `selenium.webdriver` — launching Chrome, navigating to a URL
- `WebDriverWait` + `expected_conditions` — waiting for elements to appear
- `By.CSS_SELECTOR`, `By.ID` — locating elements
- `ActionChains` — hovering over elements to trigger tooltips
- `threading.Thread` — running the cookie click loop in the background
  while the main thread handles the store-check logic
- `time.sleep` — rate-limiting loops to avoid CPU saturation
- Regex (`re.search`) — parsing human-readable number strings like
  "14,970 cookies" or "65 million" into floats

## Files in this project

| File | Version | Notes |
|---|---|---|
| `play_pause_cookie.py` | v7 | **Selected for `original/`** — infinite runtime, pause/play/stop console commands |
| `multi_thread_cookie.py` | v6 | Timed 5-minute run; moved to `old_files/` (local only, gitignored) |

v6 (`multi_thread_cookie.py`) is the closer match to the stated course exercise (timed run).
v7 was selected for `original/` because it is the final, more complete implementation
with interactive console control and no timeout.
