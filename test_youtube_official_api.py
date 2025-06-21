#!/usr/bin/env python3
"""
YouTube官方API测试脚本
测试YouTube Data API v3获取视频信息的效果
"""

import os
import requests
import json
import time
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional

# 加载环境变量
def load_env_file(file_path: str):
    """从.env文件加载环境变量"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 移除引号
                    value = value.strip('"\'')
                    os.environ[key] = value

# 尝试加载不同位置的.env文件
env_files = ['backend/.env', '.env']
for env_file in env_files:
    if os.path.exists(env_file):
        load_env_file(env_file)
        print(f"✅ 已加载环境变量文件: {env_file}")
        break

# 测试用的YouTube URL列表
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito
]

def extract_video_id(url: str) -> Optional[str]:
    """从YouTube URL中提取视频ID"""
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['youtube.com', 'www.youtube.com']:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        return None
    except Exception:
        return None

def test_youtube_official_api(video_id: str) -> Dict:
    """测试YouTube官方API"""
    # 注意：这需要YouTube Data API v3的API密钥
    # 由于我们没有设置YouTube API密钥，这个测试会失败
    # 但可以展示如何使用官方API
    
    api_key = os.getenv('YOUTUBE_API_KEY')  # 需要在.env中添加
    if not api_key:
        return {
            "success": False,
            "error": "YouTube API密钥未设置",
            "note": "需要在.env文件中添加 YOUTUBE_API_KEY=your_api_key"
        }
    
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'snippet,statistics',
        'id': video_id,
        'key': api_key
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, params=params, timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                item = data['items'][0]
                snippet = item.get('snippet', {})
                statistics = item.get('statistics', {})
                
                return {
                    "success": True,
                    "title": snippet.get('title'),
                    "author": snippet.get('channelTitle'),
                    "description": snippet.get('description', '')[:200] + '...' if snippet.get('description') else None,
                    "views": statistics.get('viewCount'),
                    "published_date": snippet.get('publishedAt'),
                    "thumbnail": snippet.get('thumbnails', {}).get('high', {}).get('url'),
                    "response_time": round(response_time, 2)
                }
            else:
                return {
                    "success": False,
                    "error": "视频未找到",
                    "response_time": round(response_time, 2)
                }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "response_time": round(response_time, 2)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": 0
        }

def main():
    print("🔍 YouTube官方API测试")
    print("=" * 60)
    
    # 检查是否有YouTube API密钥
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ 未设置YouTube API密钥")
        print("💡 要使用YouTube官方API，需要：")
        print("   1. 在Google Cloud Console创建项目")
        print("   2. 启用YouTube Data API v3")
        print("   3. 创建API密钥")
        print("   4. 在.env文件中添加 YOUTUBE_API_KEY=your_api_key")
        print("\n📋 YouTube官方API优势：")
        print("   ✅ 官方支持，稳定性高")
        print("   ✅ 数据完整准确")
        print("   ✅ 每日10,000单位免费配额")
        print("   ✅ 获取视频详情只需1单位配额")
        print("   ✅ 支持批量查询（一次最多50个视频ID）")
        print("\n📋 配额使用示例：")
        print("   - videos.list (获取视频详情): 1单位")
        print("   - search.list (搜索): 100单位")
        print("   - 每日10,000单位 = 可获取10,000个视频详情")
        print("\n🔗 设置指南：https://developers.google.com/youtube/v3/getting-started")
        return
    
    results = []
    
    for i, url in enumerate(TEST_URLS, 1):
        video_id = extract_video_id(url)
        if not video_id:
            print(f"❌ 无法解析视频ID: {url}")
            continue
            
        print(f"\n📹 测试视频 {i}: {video_id}")
        print(f"🔗 URL: {url}")
        print("-" * 40)
        
        result = test_youtube_official_api(video_id)
        results.append({
            "video_id": video_id,
            "url": url,
            "result": result
        })
        
        if result["success"]:
            print(f"✅ 成功获取视频信息 ({result['response_time']}s)")
            print(f"   标题: {result['title']}")
            print(f"   作者: {result['author']}")
            print(f"   观看数: {result['views']}")
            print(f"   发布时间: {result['published_date']}")
        else:
            print(f"❌ 失败: {result['error']}")
    
    # 保存结果
    with open('youtube_official_api_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已保存到: youtube_official_api_test_results.json")

if __name__ == "__main__":
    main() 