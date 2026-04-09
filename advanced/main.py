import re
import sys
import time
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from clicker import CookieClicker


def parse_duration_to_seconds(value: str) -> float:
    """
    Convert human-friendly time strings into seconds.

        "30"     -> 30.0
        "30s"    -> 30.0
        "2m"     -> 120.0
        "1h"     -> 3600.0
        "2m30s"  -> 150.0

    Raises ValueError for malformed input.
    """
    text = str(value).strip().lower().replace(" ", "")
    if not text:
        raise ValueError("empty duration")

    # bare number — treat as seconds
    try:
        result = float(text)
        if result <= 0:
            raise ValueError("duration must be greater than zero")
        return result
    except ValueError as e:
        if "greater than zero" in str(e):
            raise
        pass  # not a bare number, continue

    pattern = re.compile(r"(\d+(?:\.\d+)?)([hms])")
    units = {"h": 3600, "m": 60, "s": 1}
    pos, total = 0, 0.0

    for m in pattern.finditer(text):
        if m.start() != pos:
            raise ValueError(f"unexpected characters before '{text[pos:]}'")
        total += float(m.group(1)) * units[m.group(2)]
        pos = m.end()

    if pos != len(text):
        raise ValueError("unparsed trailing characters")
    if total <= 0:
        raise ValueError("duration must be greater than zero")
    return total


def main():
    print("Starting Cookie Clicker bot...")
    bot = CookieClicker()
    print("Bot ready. Type 'pause', 'play', 'interval <time>', or 'stop' at any time.\n")

    running: list[bool] = [True]
    clicking: list[bool] = [True]
    buff_until: list[float] = [0.0]
    check_interval: list[float] = [float(config.CHECK_INTERVAL)]
    click_allowed = threading.Event()
    click_allowed.set()

    def click_forever():
        while running[0]:
            click_allowed.wait()
            if clicking[0]:
                buff = bot.click_golden_cookies()
                if buff:
                    buff_until[0] = time.time() + buff
                    print(f"\nGolden cookie! Buff active for ~{buff:.0f}s.")
                bot.click()
            time.sleep(config.CLICK_SLEEP)

    def command_listener():
        while running[0]:
            raw = input().strip().lower()
            parts = raw.split()
            if not parts:
                continue
            cmd = parts[0]

            if cmd == "pause":
                clicking[0] = False
                print("Paused.")
            elif cmd in ("play", "resume"):
                clicking[0] = True
                print("Resumed.")
            elif cmd == "stop":
                running[0] = False
                print("Stopping bot...")
            elif cmd == "interval":
                if len(parts) == 1:
                    print(f"Store check interval: {check_interval[0]:.1f}s")
                else:
                    try:
                        secs = parse_duration_to_seconds(parts[1])
                        check_interval[0] = secs
                        print(f"Store check interval set to {secs:.1f}s.")
                    except ValueError as e:
                        print(f"Invalid interval: {e}. Examples: 30  30s  2m  1h  2m30s")
            else:
                print("Commands: pause | play | interval <time> | stop")

    threading.Thread(target=click_forever, daemon=True).start()
    threading.Thread(target=command_listener, daemon=True).start()

    next_check = time.time() + check_interval[0]

    while running[0]:
        if time.time() >= next_check:
            next_check = time.time() + check_interval[0]

            if not clicking[0]:
                pass  # paused — skip store check
            elif (remaining_buff := buff_until[0] - time.time()) > 0:
                print(f"\nBuff active ({remaining_buff:.0f}s left) — skipping store check.")
            else:
                click_allowed.clear()
                time.sleep(0.05)
                try:
                    cookies = bot.get_cookie_count()
                    print(f"\n=== Store check === ({cookies:,.0f} cookies)")
                    bot.check_store()
                except Exception as e:
                    print(f"Store check error (skipping): {e}")
                finally:
                    click_allowed.set()

        time.sleep(config.MAIN_POLL)

    cps = bot.get_cps()
    print(f"\nFinished. Cookies per second: {cps}" if cps else "\nFinished.")


if __name__ == "__main__":
    main()
