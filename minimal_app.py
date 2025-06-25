#!/usr/bin/env python3
"""
最簡單的 Flask 應用程式 - 直接使用內建服務器
"""

from flask import Flask, jsonify
import os
import sys

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'message': 'Hello from Zeabur!', 
        'status': 'running',
        'python_version': sys.version,
        'port': os.environ.get('PORT', 8080)
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 