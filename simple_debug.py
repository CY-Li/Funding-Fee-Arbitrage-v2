import os
import sys

print("Debug script starting")
print("Python version:", sys.version)
print("Current directory:", os.getcwd())

try:
    files = os.listdir('.')
    print("Files found:", len(files))
    for f in files[:10]:  # Show first 10 files
        print("  ", f)
except Exception as e:
    print("Error listing files:", e)

print("Debug script completed") 