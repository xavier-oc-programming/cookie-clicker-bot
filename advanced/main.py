import sys
import time
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from clicker import CookieClicker


def main():
    print("Starting Cookie Clicker bot...")
    bot = CookieClicker()
    print("Bot ready. Type 'pause', 'play', or 'stop' at any time.\n")

    running: list[bool] = [True]
    clicking: list[bool] = [True]
    buff_until: list[float] = [0.0]     # timestamp when the current buff expires
    click_allowed = threading.Event()   # cleared during store checks to pause clicking
    click_allowed.set()

    def click_forever():
        while running[0]:
            click_allowed.wait()        # blocks while store check is running
            if clicking[0]:
                buff = bot.click_golden_cookies()
                if buff:
                    buff_until[0] = time.time() + buff
                    print(f"\nGolden cookie! Buff active for ~{buff:.0f}s.")
                bot.click()
            time.sleep(config.CLICK_SLEEP)

    def command_listener():
        while running[0]:
            cmd = input().strip().lower()
            if cmd == "pause":
                clicking[0] = False
                print("Paused clicking.")
            elif cmd == "play":
                clicking[0] = True
                print("Resumed clicking.")
            elif cmd == "stop":
                running[0] = False
                print("Stopping bot...")
            else:
                print("Commands: pause | play | stop")

    threading.Thread(target=click_forever, daemon=True).start()
    threading.Thread(target=command_listener, daemon=True).start()

    next_check = time.time() + config.CHECK_INTERVAL

    while running[0]:
        if time.time() >= next_check:
            next_check = time.time() + config.CHECK_INTERVAL

            remaining_buff = buff_until[0] - time.time()
            if remaining_buff > 0:
                print(f"\nBuff active ({remaining_buff:.0f}s left) — skipping store check.")
            else:
                # pause clicking so hovers aren't interrupted by the click thread
                click_allowed.clear()
                time.sleep(0.05)        # let the click thread finish its current iteration
                try:
                    cookies = bot.get_cookie_count()
                    print(f"\n=== Store check === ({cookies:,.0f} cookies)")
                    bot.check_store()
                except Exception as e:
                    print(f"Store check error (skipping): {e}")
                finally:
                    click_allowed.set() # always resume, even if check_store raised

        time.sleep(config.MAIN_POLL)

    cps = bot.get_cps()
    print(f"\nFinished. Cookies per second: {cps}" if cps else "\nFinished.")


if __name__ == "__main__":
    main()
