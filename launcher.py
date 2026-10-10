# this launcher.py restarts the bot if it crashes.

import subprocess
import time
import os
import sys

IS_WINDOWS = sys.platform.startswith("win")

while True:
    if IS_WINDOWS:
        os.system("color a")
        os.system("title Prissy Server")
    print("Starting Prissy...")

    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    subprocess.run([sys.executable, "bot.py"])

    print("Bot stopped. Restarting in 5 seconds...")
    time.sleep(5)
