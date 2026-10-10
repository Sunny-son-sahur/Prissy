# this launcher.py restarts the bot if it crashes.

import subprocess
import time
import os

while True:
    os.system("color a")
    os.system("title Prissy Server")
    print("Starting Prissy...")

    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    subprocess.run(["python", "bot.py"])

    print("Bot stopped. Restarting in 5 seconds...")
    time.sleep(5)
