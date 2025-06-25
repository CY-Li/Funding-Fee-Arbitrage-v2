#!/usr/bin/env python3
"""
部署檢查腳本 - 驗證專案是否準備好部署到 Zeabur
"""

import os
import sys
import importlib
import json

def check_file_exists(filepath, description):
    """檢查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - 文件不存在")
        return False

def check_import(module_name, description):
    """檢查模組是否可以導入"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - 導入失敗: {e}")
        return False

def check_config():
    """檢查配置是否正確"""
    print("\n🔧 檢查配置...")
    
    # 檢查 config.py 是否可以導入
    if not check_import('config', 'config.py 模組'):
        return False
    
    # 檢查 config.json 是否存在
    if not check_file_exists('config.json', 'config.json 配置文件'):
        return False
    
    # 檢查 API 密鑰環境變數
    required_env_vars = [
        'GATEIO_API_KEY',
        'GATEIO_SECRET_KEY', 
        'BITGET_API_KEY',
        'BITGET_SECRET_KEY',
        'BITGET_API_PASSPHRASE'
    ]
    
    print("\n🔑 檢查環境變數...")
    for var in required_env_vars:
        if os.environ.get(var):
            print(f"✅ 環境變數: {var}")
        else:
            print(f"⚠️  環境變數: {var} - 未設置 (部署時需要在 Zeabur 設置)")
    
    return True

def check_dependencies():
    """檢查依賴項"""
    print("\n📦 檢查依賴項...")
    
    required_packages = [
        'flask',
        'ccxt', 
        'pandas',
        'numpy',
        'requests',
        'gunicorn',
        'gevent'
    ]
    
    all_good = True
    for package in required_packages:
        if not check_import(package, f'Python 包: {package}'):
            all_good = False
    
    return all_good

def check_project_structure():
    """檢查專案結構"""
    print("\n📁 檢查專案結構...")
    
    required_files = [
        ('main.py', '主入口文件'),
        ('web_server.py', 'Web 服務器'),
        ('trading_bot.py', '交易機器人'),
        ('config.py', '配置模組'),
        ('requirements.txt', '依賴列表'),
        ('Dockerfile', 'Docker 配置'),
        ('.dockerignore', 'Docker 忽略文件'),
        ('config.json', '配置文件'),
        ('all_funding_rates.csv', '資金費率數據'),
        ('analysis_summary.json', '分析摘要')
    ]
    
    required_dirs = [
        ('templates', 'HTML 模板目錄'),
        ('utils', '工具模組目錄'),
        ('exchanges', '交易所 API 目錄')
    ]
    
    all_good = True
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    for dirpath, description in required_dirs:
        if os.path.isdir(dirpath):
            print(f"✅ {description}: {dirpath}/")
        else:
            print(f"❌ {description}: {dirpath}/ - 目錄不存在")
            all_good = False
    
    return all_good

def check_templates():
    """檢查模板文件"""
    print("\n🎨 檢查模板文件...")
    
    template_files = [
        'templates/index.html',
        'templates/funding_rates.html', 
        'templates/config.html'
    ]
    
    all_good = True
    for template in template_files:
        if not check_file_exists(template, f'模板文件: {os.path.basename(template)}'):
            all_good = False
    
    return all_good

def check_data_files():
    """檢查數據文件"""
    print("\n📊 檢查數據文件...")
    
    data_files = [
        ('all_funding_rates.csv', '資金費率原始數據'),
        ('analysis_summary.json', '資金費率分析摘要')
    ]
    
    all_good = True
    for filepath, description in data_files:
        if check_file_exists(filepath, description):
            # 檢查文件大小
            size = os.path.getsize(filepath)
            if size > 0:
                print(f"   📏 文件大小: {size:,} bytes")
            else:
                print(f"   ⚠️  文件大小: 0 bytes (空文件)")
                all_good = False
        else:
            all_good = False
    
    return all_good

def check_docker_config():
    """檢查 Docker 配置"""
    print("\n🐳 檢查 Docker 配置...")
    
    # 檢查 Dockerfile
    if not check_file_exists('Dockerfile', 'Dockerfile'):
        return False
    
    # 檢查 .dockerignore
    if not check_file_exists('.dockerignore', '.dockerignore'):
        return False
    
    # 檢查 .dockerignore 內容
    with open('.dockerignore', 'r') as f:
        content = f.read()
        if 'all_funding_rates.csv' in content or 'analysis_summary.json' in content:
            print("⚠️  .dockerignore 排除了重要數據文件，這可能導致部署問題")
            return False
    
    print("✅ Docker 配置檢查通過")
    return True

def main():
    """主檢查函數"""
    print("🚀 Zeabur 部署檢查開始...\n")
    
    checks = [
        ("專案結構", check_project_structure),
        ("Docker 配置", check_docker_config),
        ("依賴項", check_dependencies),
        ("配置", check_config),
        ("模板文件", check_templates),
        ("數據文件", check_data_files)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} 檢查失敗: {e}")
            results.append((check_name, False))
    
    print("\n" + "="*50)
    print("📋 檢查結果摘要:")
    print("="*50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 所有檢查通過！專案已準備好部署到 Zeabur")
        print("\n📝 部署步驟:")
        print("1. 將代碼推送到 Git 倉庫")
        print("2. 在 Zeabur 創建新服務，選擇 Docker 部署")
        print("3. 連接 Git 倉庫")
        print("4. 設置環境變數 (API 密鑰等)")
        print("5. 設置啟動命令: python main.py")
        print("6. 部署服務")
    else:
        print("⚠️  發現問題，請修復後再部署")
        print("\n💡 常見問題:")
        print("- 確保所有必要的文件都存在")
        print("- 檢查 .dockerignore 是否排除了重要文件")
        print("- 確保 requirements.txt 包含所有依賴")
        print("- 檢查 API 密鑰環境變數設置")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 