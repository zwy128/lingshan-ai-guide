#!/usr/bin/env python3
"""压缩效果基准测试"""
import requests
import time
import json
from pathlib import Path

def test_compression():
    """测试压缩效果"""
    base_url = "http://localhost:8000"
    
    # 测试API响应
    print("📊 API响应测试:")
    endpoints = [
        "/api/config/models",
        "/api/config/voices",
        "/api/config/current",
    ]
    
    for endpoint in endpoints:
        # 不压缩请求
        start = time.time()
        response = requests.get(f"{base_url}{endpoint}")
        time_no_compress = time.time() - start
        size_no_compress = len(response.content)
        
        # 压缩请求
        start = time.time()
        response = requests.get(
            f"{base_url}{endpoint}",
            headers={"Accept-Encoding": "gzip, deflate, br"}
        )
        time_compress = time.time() - start
        size_compress = len(response.content)
        
        compression_ratio = (1 - size_compress / size_no_compress) * 100 if size_no_compress > 0 else 0
        
        print(f"  {endpoint}:")
        print(f"    无压缩: {size_no_compress} bytes, {time_no_compress:.3f}s")
        print(f"    有压缩: {size_compress} bytes, {time_compress:.3f}s")
        print(f"    压缩率: {compression_ratio:.1f}%")
        print()
    
    # 测试静态文件
    print("📁 静态文件测试:")
    static_files = [
        "/static/live2d/models.json",
        "/static/js/lazy-loading.js",
        "/static/js/performance-monitor.js",
    ]
    
    for file_path in static_files:
        start = time.time()
        response = requests.get(f"{base_url}{file_path}")
        time_no_compress = time.time() - start
        size_no_compress = len(response.content)
        
        start = time.time()
        response = requests.get(
            f"{base_url}{file_path}",
            headers={"Accept-Encoding": "gzip, deflate, br"}
        )
        time_compress = time.time() - start
        size_compress = len(response.content)
        
        compression_ratio = (1 - size_compress / size_no_compress) * 100 if size_no_compress > 0 else 0
        
        print(f"  {file_path}:")
        print(f"    无压缩: {size_no_compress} bytes, {time_no_compress:.3f}s")
        print(f"    有压缩: {size_compress} bytes, {time_compress:.3f}s")
        print(f"    压缩率: {compression_ratio:.1f}%")
        print()

if __name__ == "__main__":
    print("🚀 开始压缩效果基准测试...")
    print("⚠️ 请确保后端服务正在运行: http://localhost:8000")
    print()
    
    try:
        test_compression()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请先启动后端:")
        print("   python3 backend/main.py")
