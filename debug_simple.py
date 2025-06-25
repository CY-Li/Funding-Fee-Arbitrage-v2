#!/usr/bin/env python3
import os
import sys
import time

print("=== Starting Debug Script ===")
print(f"Time: {time.ctime()}")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

try:
    print("Listing files in current directory:")
    files = os.listdir('.')
    for file in files:
        print(f"  - {file}")
except Exception as e:
    print(f"Error listing files: {e}")

try:
    print("Checking environment variables:")
    port = os.environ.get('PORT', 'NOT_SET')
    print(f"  PORT: {port}")
    print(f"  PATH: {os.environ.get('PATH', 'NOT_SET')}")
    print(f"  HOME: {os.environ.get('HOME', 'NOT_SET')}")
except Exception as e:
    print(f"Error checking environment: {e}")

print("=== Debug Script Completed ===")
print("If you see this message, Python is working correctly!")

# Keep the process running for a while to see if it gets killed
print("Keeping process alive for 30 seconds...")
time.sleep(30)
print("Process completed successfully!") 