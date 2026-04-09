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

    def click_forever():
        while running[0]:
            if clicking[0]:
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
            print("\n=== Store check ===")
            try:
                bot.check_store()
            except Exception as e:
                print(f"Store check error (skipping): {e}")

        time.sleep(config.MAIN_POLL)

    cps = bot.get_cps()
    print(f"\nFinished. Cookies per second: {cps}" if cps else "\nFinished.")


if __name__ == "__main__":
    main()
