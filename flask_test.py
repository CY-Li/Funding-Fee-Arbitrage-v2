#!/usr/bin/env python3
"""
Flask 測試腳本
"""

try:
    print("Testing Flask import...")
    from flask import Flask
    print("✓ Flask imported successfully")
    
    app = Flask(__name__)
    print("✓ Flask app created successfully")
    
    @app.route('/')
    def hello():
        return "Hello from Flask!"
    
    print("✓ Route defined successfully")
    
    import os
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Flask server on port {port}...")
    
    app.run(host='0.0.0.0', port=port, debug=False)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1) 