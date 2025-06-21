#!/usr/bin/env python3
"""
YouTube API测试脚本
比较SerpAPI和RapidAPI获取YouTube视频信息的效果
"""

import os
import requests
import json
import time
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, List

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

# 测试用的YouTube URL列表（从截图5中选择）
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - 经典测试视频
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito
    "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",  # Bohemian Rhapsody
    "https://www.youtube.com/watch?v=YQHsXMglC9A",  # Hello - Adele
]

def extract_video_id(url: str) -> Optional[str]:
    """从YouTube URL中提取视频ID"""
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['youtube.com', 'www.youtube.com']:
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.hostname in ['youtu.be']:
            return parsed_url.path[1:]
    except:
        pass
    return None

class SerpAPITester:
    """SerpAPI YouTube Video API测试器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    def get_video_info(self, video_id: str) -> Dict:
        """通过SerpAPI获取YouTube视频信息"""
        params = {
            'engine': 'youtube_video',
            'v': video_id,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

class RapidAPITester:
    """RapidAPI YouTube相关服务测试器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'youtube-v3-alternative.p.rapidapi.com'  # 尝试常见的YouTube API服务
        }
    
    def get_video_info_v1(self, video_id: str) -> Dict:
        """尝试方法1: YouTube v3 Alternative API"""
        url = f"https://youtube-v3-alternative.p.rapidapi.com/video"
        params = {'id': video_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e), 'method': 'v3_alternative'}
    
    def get_video_info_v2(self, video_id: str) -> Dict:
        """尝试方法2: YouTube Data API"""
        self.headers['X-RapidAPI-Host'] = 'youtube-data8.p.rapidapi.com'
        url = f"https://youtube-data8.p.rapidapi.com/video/details/"
        params = {'id': video_id}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e), 'method': 'data8'}
    
    def get_video_info_v3(self, video_id: str) -> Dict:
        """尝试方法3: YouTube v3 API"""
        self.headers['X-RapidAPI-Host'] = 'youtube-v31.p.rapidapi.com'
        url = f"https://youtube-v31.p.rapidapi.com/videos"
        params = {
            'part': 'snippet,statistics',
            'id': video_id
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e), 'method': 'v31'}

def extract_video_data(api_response: Dict, api_type: str) -> Dict:
    """从API响应中提取标准化的视频信息"""
    result = {
        'api_type': api_type,
        'success': False,
        'title': None,
        'author': None,
        'description': None,
        'views': None,
        'duration': None,
        'published_date': None,
        'thumbnail': None,
        'error': None
    }
    
    try:
        if 'error' in api_response:
            result['error'] = api_response['error']
            return result
        
        if api_type == 'serpapi':
            if 'title' in api_response:
                result['success'] = True
                result['title'] = api_response.get('title')
                result['author'] = api_response.get('channel', {}).get('name')
                result['description'] = api_response.get('description', {}).get('content', '')[:200] + '...' if api_response.get('description') else None
                result['views'] = api_response.get('views')
                result['published_date'] = api_response.get('published_date')
                result['thumbnail'] = api_response.get('thumbnail')
        
        elif api_type.startswith('rapidapi'):
            # 根据不同的RapidAPI服务格式解析
            if 'items' in api_response and api_response['items']:
                item = api_response['items'][0]
                result['success'] = True
                result['title'] = item.get('snippet', {}).get('title')
                result['author'] = item.get('snippet', {}).get('channelTitle')
                result['description'] = item.get('snippet', {}).get('description', '')[:200] + '...'
                result['views'] = item.get('statistics', {}).get('viewCount')
                result['published_date'] = item.get('snippet', {}).get('publishedAt')
                result['thumbnail'] = item.get('snippet', {}).get('thumbnails', {}).get('high', {}).get('url')
            elif 'title' in api_response:
                result['success'] = True
                result['title'] = api_response.get('title')
                result['author'] = api_response.get('channelTitle') or api_response.get('author')
                result['description'] = api_response.get('description', '')[:200] + '...' if api_response.get('description') else None
                result['views'] = api_response.get('viewCount')
                result['published_date'] = api_response.get('publishedAt')
                result['thumbnail'] = api_response.get('thumbnail')
    
    except Exception as e:
        result['error'] = f"解析错误: {str(e)}"
    
    return result

def test_apis():
    """测试两个API平台的性能"""
    # 从环境变量获取API密钥
    serpapi_key = os.getenv('serpAPI_KEY')
    rapidapi_key = os.getenv('rapidAPI_KEY')
    
    if not serpapi_key:
        print("❌ 未找到 serpAPI_KEY 环境变量")
        return
    
    if not rapidapi_key:
        print("❌ 未找到 rapidAPI_KEY 环境变量")
        return
    
    print("🔍 开始测试YouTube API服务...")
    print("=" * 60)
    
    # 初始化测试器
    serpapi_tester = SerpAPITester(serpapi_key)
    rapidapi_tester = RapidAPITester(rapidapi_key)
    
    results = []
    
    for i, url in enumerate(TEST_URLS[:2], 1):  # 先测试前2个URL
        video_id = extract_video_id(url)
        if not video_id:
            print(f"❌ 无法从URL中提取视频ID: {url}")
            continue
        
        print(f"\n📹 测试视频 {i}: {video_id}")
        print(f"🔗 URL: {url}")
        print("-" * 40)
        
        # 测试SerpAPI
        print("🔍 测试 SerpAPI...")
        start_time = time.time()
        serpapi_response = serpapi_tester.get_video_info(video_id)
        serpapi_time = time.time() - start_time
        serpapi_result = extract_video_data(serpapi_response, 'serpapi')
        serpapi_result['response_time'] = round(serpapi_time, 2)
        
        # 测试RapidAPI的多种方法
        rapidapi_results = []
        
        print("🔍 测试 RapidAPI (方法1)...")
        start_time = time.time()
        rapidapi_response1 = rapidapi_tester.get_video_info_v1(video_id)
        rapidapi_time1 = time.time() - start_time
        rapidapi_result1 = extract_video_data(rapidapi_response1, 'rapidapi_v1')
        rapidapi_result1['response_time'] = round(rapidapi_time1, 2)
        rapidapi_results.append(rapidapi_result1)
        
        print("🔍 测试 RapidAPI (方法2)...")
        start_time = time.time()
        rapidapi_response2 = rapidapi_tester.get_video_info_v2(video_id)
        rapidapi_time2 = time.time() - start_time
        rapidapi_result2 = extract_video_data(rapidapi_response2, 'rapidapi_v2')
        rapidapi_result2['response_time'] = round(rapidapi_time2, 2)
        rapidapi_results.append(rapidapi_result2)
        
        print("🔍 测试 RapidAPI (方法3)...")
        start_time = time.time()
        rapidapi_response3 = rapidapi_tester.get_video_info_v3(video_id)
        rapidapi_time3 = time.time() - start_time
        rapidapi_result3 = extract_video_data(rapidapi_response3, 'rapidapi_v3')
        rapidapi_result3['response_time'] = round(rapidapi_time3, 2)
        rapidapi_results.append(rapidapi_result3)
        
        # 显示结果
        print("\n📊 结果对比:")
        print(f"SerpAPI: {'✅' if serpapi_result['success'] else '❌'} ({serpapi_result['response_time']}s)")
        if serpapi_result['success']:
            print(f"  标题: {serpapi_result['title']}")
            print(f"  作者: {serpapi_result['author']}")
            print(f"  观看数: {serpapi_result['views']}")
        else:
            print(f"  错误: {serpapi_result['error']}")
        
        for j, rapid_result in enumerate(rapidapi_results, 1):
            print(f"RapidAPI(方法{j}): {'✅' if rapid_result['success'] else '❌'} ({rapid_result['response_time']}s)")
            if rapid_result['success']:
                print(f"  标题: {rapid_result['title']}")
                print(f"  作者: {rapid_result['author']}")
                print(f"  观看数: {rapid_result['views']}")
            else:
                print(f"  错误: {rapid_result['error']}")
        
        # 保存详细结果
        test_result = {
            'video_id': video_id,
            'url': url,
            'serpapi': serpapi_result,
            'rapidapi': rapidapi_results,
            'raw_responses': {
                'serpapi': serpapi_response,
                'rapidapi': [rapidapi_response1, rapidapi_response2, rapidapi_response3]
            }
        }
        results.append(test_result)
        
        # 防止API限制，稍作休息
        time.sleep(1)
    
    # 保存详细结果到文件
    with open('youtube_api_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    
    serpapi_success = sum(1 for r in results if r['serpapi']['success'])
    rapidapi_success_counts = [0, 0, 0]
    
    for result in results:
        for i, rapid_result in enumerate(result['rapidapi']):
            if rapid_result['success']:
                rapidapi_success_counts[i] += 1
    
    print(f"SerpAPI 成功率: {serpapi_success}/{len(results)} ({serpapi_success/len(results)*100:.1f}%)")
    for i, count in enumerate(rapidapi_success_counts, 1):
        print(f"RapidAPI(方法{i}) 成功率: {count}/{len(results)} ({count/len(results)*100:.1f}%)")
    
    # 计算平均响应时间
    serpapi_avg_time = sum(r['serpapi']['response_time'] for r in results) / len(results)
    rapidapi_avg_times = [
        sum(r['rapidapi'][i]['response_time'] for r in results) / len(results)
        for i in range(3)
    ]
    
    print(f"\n⏱️ 平均响应时间:")
    print(f"SerpAPI: {serpapi_avg_time:.2f}s")
    for i, avg_time in enumerate(rapidapi_avg_times, 1):
        print(f"RapidAPI(方法{i}): {avg_time:.2f}s")
    
    print(f"\n💾 详细结果已保存到: youtube_api_test_results.json")

if __name__ == "__main__":
    test_apis() 