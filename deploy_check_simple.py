#!/usr/bin/env python3
"""
簡化部署檢查腳本 - 只檢查文件存在性
"""

import os

def check_file(filepath, description):
    """檢查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - 文件不存在")
        return False

def check_dir(dirpath, description):
    """檢查目錄是否存在"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}/")
        return True
    else:
        print(f"❌ {description}: {dirpath}/ - 目錄不存在")
        return False

def main():
    print("🚀 Zeabur 部署檢查開始...\n")
    
    # 檢查必要文件
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
    
    # 檢查必要目錄
    required_dirs = [
        ('templates', 'HTML 模板目錄'),
        ('utils', '工具模組目錄'),
        ('exchanges', '交易所 API 目錄')
    ]
    
    # 檢查模板文件
    template_files = [
        ('templates/index.html', '主頁模板'),
        ('templates/funding_rates.html', '資金費率頁面模板'),
        ('templates/config.html', '配置頁面模板')
    ]
    
    all_good = True
    
    print("📁 檢查專案結構...")
    for filepath, description in required_files:
        if not check_file(filepath, description):
            all_good = False
    
    for dirpath, description in required_dirs:
        if not check_dir(dirpath, description):
            all_good = False
    
    print("\n🎨 檢查模板文件...")
    for filepath, description in template_files:
        if not check_file(filepath, description):
            all_good = False
    
    print("\n📊 檢查數據文件...")
    data_files = [
        ('all_funding_rates.csv', '資金費率原始數據'),
        ('analysis_summary.json', '資金費率分析摘要')
    ]
    
    for filepath, description in data_files:
        if check_file(filepath, description):
            size = os.path.getsize(filepath)
            if size > 0:
                print(f"   📏 文件大小: {size:,} bytes")
            else:
                print(f"   ⚠️  文件大小: 0 bytes (空文件)")
                all_good = False
    
    print("\n🐳 檢查 Docker 配置...")
    if check_file('Dockerfile', 'Dockerfile'):
        with open('Dockerfile', 'r') as f:
            content = f.read()
            if 'python:3.10-slim' in content:
                print("   ✅ 使用正確的 Python 基礎映像")
            else:
                print("   ⚠️  Dockerfile 可能不是預期的內容")
    
    if check_file('.dockerignore', '.dockerignore'):
        with open('.dockerignore', 'r') as f:
            content = f.read()
            if 'all_funding_rates.csv' in content or 'analysis_summary.json' in content:
                print("   ⚠️  .dockerignore 排除了重要數據文件")
                all_good = False
            else:
                print("   ✅ .dockerignore 配置正確")
    
    print("\n" + "="*50)
    print("📋 檢查結果摘要:")
    print("="*50)
    
    if all_good:
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
    
    return all_good

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1) 