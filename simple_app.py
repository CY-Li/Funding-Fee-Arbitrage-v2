#!/usr/bin/env python3
"""
最簡單的 Flask 應用程式 - 用於測試基本功能
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': 'Hello from Zeabur!', 'status': 'running'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'port': os.environ.get('PORT', 8080)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 