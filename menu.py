import os
import sys
import subprocess
from pathlib import Path
from art import LOGO


def main():
    clear = True
    while True:
        if clear:
            os.system("cls" if os.name == "nt" else "clear")
        clear = True

        print(LOGO)
        print("Select a build to run:\n")
        print("  1. Original  — play_pause_cookie.py (course version)")
        print("  2. Advanced  — advanced/main.py (OOP, config module)")
        print("  q. Quit\n")

        choice = input("Enter choice: ").strip().lower()

        if choice == "1":
            path = Path(__file__).parent / "original" / "play_pause_cookie.py"
            subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
            input("\nPress Enter to return to menu...")
        elif choice == "2":
            path = Path(__file__).parent / "advanced" / "main.py"
            subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
            input("\nPress Enter to return to menu...")
        elif choice == "q":
            break
        else:
            print("Invalid choice. Try again.")
            clear = False


if __name__ == "__main__":
    main()
