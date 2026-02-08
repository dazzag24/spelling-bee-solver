#!/usr/bin/env python3
"""
Simple entrypoint that starts Xvfb and runs app.py directly.
Use this if your app.py already handles its own execution.
"""
import subprocess
import sys
import time


# Start Xvfb in the background
try:
    xvfb_process = subprocess.Popen(
        ["Xvfb", ":99", "-screen", "0", "1024x768x16"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)  # Give Xvfb time to start
    print("Xvfb started on display :99")
except Exception as e:
    print(f"Failed to start Xvfb: {e}", file=sys.stderr)
    sys.exit(1)

# Execute the main application
# This replaces the current process with python app.py
import os
os.execvp("python", ["python", "app.py"])