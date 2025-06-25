#!/usr/bin/env python3
import os
import sys

print("=== Environment Diagnosis ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

print("\n=== Environment Variables ===")
for key, value in os.environ.items():
    if key in ['PORT', 'PATH', 'PYTHONPATH', 'HOME']:
        print(f"{key}: {value}")

print("\n=== Testing Flask ===")
try:
    from flask import Flask
    print("✓ Flask imported successfully")
    
    app = Flask(__name__)
    print("✓ Flask app created")
    
    @app.route('/')
    def hello():
        return "Hello from Zeabur!"
    
    print("✓ Route defined")
    
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 