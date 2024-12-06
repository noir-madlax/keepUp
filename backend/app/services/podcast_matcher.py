from urllib.parse import urlparse, parse_qs

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
import os
import csv
from datetime import datetime
from difflib import SequenceMatcher
import logging
from googleapiclient.discovery_cache.base import Cache
import json
import googleapiclient.discovery
import socket
from youtubesearchpython import VideosSearch
import re
from dateutil import parser
from datetime import timedelta
import glob

# 配置日志输出格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# API 配置
# Spotify API credentials - 从 Spotify Developer Dashboard 获取
# https://developer.spotify.com/dashboard/
client_id = '8e07329a94b540ae87a1c4e74457f425'        # Spotify Developer Dashboard 中的 Client ID
client_secret = '41671b5ee52d4b97878339a29b704b15' # Spotify Developer Dashboard 中的 Client Secret

# 设置全局 socket 超时
socket.setdefaulttimeout(30)  # 设置30秒超时

# 添加一个空的缓存类
class MemoryCache(Cache):
    _CACHE = {}

    def get(self, url):
        return self._CACHE.get(url)

    def set(self, url, content):
        self._CACHE[url] = content

# 在文件顶部添加三个不同的阈值常量
SPOTIFY_APPLE_THRESHOLD = 0.8    # Spotify 和 Apple 之间的匹配阈值
SPOTIFY_YOUTUBE_THRESHOLD = 0.5  # Spotify 和 YouTube 之间的匹配阈值
APPLE_YOUTUBE_THRESHOLD = 0.5    # Apple 和 YouTube 之间的匹配阈值

def setup_output_directory():
    """创建输出目录，如果目录已存在则跳过"""
    # 获取当前文件所在的prd目录的父目录
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 在父目录下创建UrlSwitcher目录
    output_dir = os.path.join(current_dir, 'UrlSwitcher')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"创建输出目录: {output_dir}")
    return output_dir

def convert_duration_to_ms(duration_str):
    """将时间字符串转换为毫秒
    支持格式：
    - "H:MM:SS" (例如 "1:38:27")
    - "MM:SS" (例如 "3:43")
    """
    try:
        parts = duration_str.split(':')
        if len(parts) == 2:  # MM:SS 格式
            minutes, seconds = map(int, parts)
            total_seconds = minutes * 60 + seconds
        elif len(parts) == 3:  # H:MM:SS 格
            hours, minutes, seconds = map(int, parts)
            total_seconds = hours * 3600 + minutes * 60 + seconds
        else:
            logging.error(f"无效的时长格式: {duration_str}")
            return 0
        
        return total_seconds * 1000  # 转换为毫秒
    except Exception as e:
        logging.error(f"转换时长时出错 ({duration_str}): {str(e)}")
        return 0

def calculate_similarity(video_info, source_podcast_info, weights):
    """计算两个节目之间的相似度"""
    def clean_title(title):
        # 移除特殊字符、标点符号和多余空格，转换为小写
        cleaned = re.sub(r'[^\w\s]', ' ', title.lower())
        return ' '.join(cleaned.split())
    
    def calculate_text_similarity(text1, text2):
        """使用 SequenceMatcher 计算两个文本的相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 清理文本
        cleaned1 = clean_title(text1)
        cleaned2 = clean_title(text2)
        
        # 计算相似度
        similarity = SequenceMatcher(None, cleaned1, cleaned2).ratio()
        
        # 返回相似度和计算过程的详细信息
        similarity_info = {
            'original_text1': text1,
            'original_text2': text2,
            'cleaned_text1': cleaned1,
            'cleaned_text2': cleaned2,
            'similarity_score': similarity
        }
        
        return similarity, similarity_info

    # 1. 标题相似度计算
    title1 = video_info.get('title', '') or video_info.get('episode_title', '')
    title2 = source_podcast_info.get('episode_title', '')
    title_similarity, title_details = calculate_text_similarity(title1, title2)
    
    # 2. 节目/频道相似度计算
    show1 = video_info.get('channel', '') or video_info.get('show_name', '')
    show2 = source_podcast_info.get('show_name', '')
    show_similarity, show_details = calculate_text_similarity(show1, show2)
    
    # 3. 时长相似度计算
    duration1 = video_info.get('duration_ms', 0)
    if isinstance(duration1, str):
        duration1 = convert_duration_to_ms(duration1)
    duration2 = source_podcast_info.get('duration_ms', 0)
    
    # 计算时长相似度：使用相对差异
    duration_details = {
        'duration1_ms': duration1,
        'duration2_ms': duration2,
        'difference_ms': None,
        'similarity_score': 0
    }
    
    if duration1 and duration2:
        duration_diff = abs(int(duration1) - int(duration2))
        max_duration = max(int(duration1), int(duration2))
        duration_similarity = 1 - (duration_diff / max_duration)
        duration_similarity = max(0, duration_similarity)
        
        duration_details.update({
            'difference_ms': duration_diff,
            'max_duration_ms': max_duration,
            'similarity_score': duration_similarity
        })
    else:
        duration_similarity = 0
    
    # 计算加权总相似度
    total_similarity = (
        weights.get('title', 0.5) * title_similarity +
        weights.get('show', 0.3) * show_similarity +
        weights.get('duration', 0.2) * duration_similarity
    )
    
    # 构建完整的相似度计算详情
    similarity_details = {
        'title_comparison': {
            'source_title': title2,
            'target_title': title1,
            'details': title_details,
            'weight': weights.get('title', 0.5),
            'weighted_score': weights.get('title', 0.5) * title_similarity
        },
        'show_comparison': {
            'source_show': show2,
            'target_show': show1,
            'details': show_details,
            'weight': weights.get('show', 0.3),
            'weighted_score': weights.get('show', 0.3) * show_similarity
        },
        'duration_comparison': {
            'details': duration_details,
            'weight': weights.get('duration', 0.2),
            'weighted_score': weights.get('duration', 0.2) * duration_similarity
        },
        'total': {
            'title': title1,
            'total_similarity': total_similarity,
            'weights_used': weights
        }
    }
    
    return total_similarity, similarity_details

def extract_spotify_id(url):
    """从 Spotify URL 中提取 episode ID"""
    parsed_url = urlparse(url)
    if 'episode' in parsed_url.path:
        episode_id = parsed_url.path.split('/')[-1]
        logging.info(f"成功提取 Spotify episode ID: {episode_id}")
        return episode_id
    logging.error("无效的 Spotify URL 式")
    return None

def get_spotify_episode(url):
    """获取 Spotify 播客单集信息"""
    logging.info("开始获 Spotify 节目信息...")
    episode_id = extract_spotify_id(url)
    if not episode_id:
        raise ValueError("无效的 Spotify URL")

    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, 
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        episode = sp.episode(episode_id)
        episode_info = {
            'platform': 'Spotify',
            'episode_title': episode['name'],
            'show_name': episode['show']['name'],
            'author': episode['show']['publisher'],
            'url': episode['external_urls']['spotify'],
            'duration_ms': episode['duration_ms'],
            'release_date': episode['release_date'],
            'description': episode['description'],
            'language': episode['language'],
            'explicit': episode['explicit'],
            'show_id': episode['show']['id']
        }
        logging.info("成功获取 Spotify 节目信息")
        return episode_info
    except Exception as e:
        logging.error(f"获 Spotify 信息时发生错误: {str(e)}")
        raise

def search_apple_podcast(query, source_podcast_info, weights, similarity_threshold=SPOTIFY_APPLE_THRESHOLD):
    """在 Apple Podcast 中搜索节目并计算相似度"""
    logging.info(f"开始在 Apple Podcast 中搜索: {query}")
    
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": query,
        "media": "podcast",
        "entity": "podcastEpisode",
        "limit": 5
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = []
        detailed_results = []
        debug_info = {
            "process_log": [],  # 用于收集处理过程的日志
            "comparison_details": []  # 用于收集相似度比较的详细信息
        }
        
        if response.status_code == 200:
            data = response.json()
            debug_info["process_log"].append(f"Apple Podcast API 返回 {data['resultCount']} 个结果")
            
            output_dir = setup_output_directory()
            
            # 保存原始搜索结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_results_file = os.path.join(output_dir, f'apple_search_raw_results_{timestamp}.json')
            with open(raw_results_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"Apple Podcast 搜索原始数据已保存到: {raw_results_file}")
            
            if data['resultCount'] > 0:
                debug_info["process_log"].append(f"开始处理 {data['resultCount']} 个搜索结果")
                
                for idx, item in enumerate(data['results'], 1):
                    current_comparison = {
                        "result_index": idx,
                        "apple_info": {
                            'episode_title': item.get('trackName', ''),
                            'show_name': item.get('collectionName', ''),
                            'duration_ms': item.get('trackTimeMillis', 0)
                        }
                    }
                    
                    similarity, similarity_details = calculate_similarity(
                        current_comparison["apple_info"],
                        source_podcast_info,
                        weights
                    )
                    
                    current_comparison["similarity_calculation"] = {
                        "similarity_score": similarity,
                        "details": similarity_details
                    }
                    
                    detailed_result = {
                        'apple_podcast': {
                            'episode_title': item.get('trackName', ''),
                            'show_name': item.get('collectionName', ''),
                            'duration_ms': item.get('trackTimeMillis', 0),
                            'url': item.get('trackViewUrl', '')
                        },
                        'spotify_source': {
                            'episode_title': source_podcast_info.get('episode_title', ''),
                            'show_name': source_podcast_info.get('show_name', ''),
                            'duration_ms': source_podcast_info.get('duration_ms', 0)
                        },
                        'similarity_calculation': {
                            'title_comparison': similarity_details['title_comparison'],
                            'show_comparison': similarity_details['show_comparison'],
                            'duration_comparison': similarity_details['duration_comparison'],
                            'total_similarity': similarity
                        }
                    }
                    detailed_results.append(detailed_result)
                    debug_info["comparison_details"].append(current_comparison)
                    
                    if similarity >= similarity_threshold:
                        result = {
                            'platform': 'Apple Podcast',
                            'episode_title': item.get('trackName', ''),
                            'show_name': item.get('collectionName', ''),
                            'author': item.get('collectionArtistName', ''),
                            'url': item.get('trackViewUrl', ''),
                            'release_date': item.get('releaseDate', ''),
                            'duration_ms': item.get('trackTimeMillis', ''),
                            'description': item.get('description', ''),
                            'genre': item.get('primaryGenreName', ''),
                            'collection_id': item.get('collectionId', ''),
                            'similarity': similarity,
                            'similarity_details': similarity_details
                        }
                        results.append(result)
                        debug_info["process_log"].append(f"结果 {idx} 满足相似度阈值 {similarity_threshold}")
                    else:
                        debug_info["process_log"].append(f"结果 {idx} 相似度 {similarity} 低于阈值 {similarity_threshold}")
            
            # 构建完整的结果数据
            result_data = {
                "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_title": source_podcast_info['episode_title'],
                "results": results if results else "未找到满足相似度阈值的匹配结果",
                "threshold": similarity_threshold,
                "weights_used": weights,
                "all_comparisons": detailed_results,
                "matching_results_count": len(results),
                "total_results_analyzed": len(detailed_results),
                "debug_information": debug_info  # 添加调试信息
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            similarity_results_file = os.path.join(output_dir, f'apple_similarity_results_{timestamp}.json')
            
            with open(similarity_results_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=4)
            
            return results
            
    except requests.exceptions.RequestException as e:
        logging.error(f"搜索 Apple Podcast 时发生错误: {str(e)}")
        return []

def search_youtube(query, limit=5):
    """在 YouTube 中搜索视频
    
    Args:
        query (str): 搜索关键词
        limit (int): 搜索结果数量限制
        
    Returns:
        list: 搜索结果列表
    """
    logging.info(f"开始在 YouTube 中搜索: {query}")
    
    try:
        print("kaishi")
        videos_search = VideosSearch(query, limit=limit)
        search_results = videos_search.result()
        logging.debug(f"搜索结果类型: {type(search_results)}")
        logging.debug(f"搜索结果内容: {search_results}")
        print("end")
        
        # 使用setup_output_directory获取正确的输出目录
        output_dir = setup_output_directory()
        print("保存原始搜索结果")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_results_file = os.path.join(output_dir, f'youtube_raw_results_{timestamp}.json')
        with open(raw_results_file, 'w', encoding='utf-8') as f:
            json.dump(search_results, f, ensure_ascii=False, indent=4)
        logging.info(f"YouTube 原始搜索结果已保存到: {raw_results_file}")
        
        return search_results.get('result', [])
    
    
    
    except Exception as e:
        logging.error(f"搜索 YouTube 时发生错误: {str(e)}", exc_info=True)
        return []

def calculate_similarity_scores(search_results, source_podcast_info, weights):
    """计算搜索结果与源播客的相似度"""
    all_results = []
    for result in search_results:
        try:
            video_info = {
                'title': result['title'],
                'channel': result['channel']['name'],
                'url': f"https://www.youtube.com/watch?v={result['id']}",
                'duration_ms': result.get('duration', 0)  # 添加时长信息
            }
            print ('video_info!!!!!!!!',video_info['duration_ms'])
            # 添加调试日志
            logging.debug(f"处理视频: {video_info['title']}, 时长: {video_info['duration_ms']}ms")
            
            # 计算相似度
            similarity, similarity_details = calculate_similarity(video_info, source_podcast_info, weights)
            
            video_info['similarity'] = similarity
            video_info['similarity_details'] = similarity_details
            all_results.append(video_info)
        except Exception as e:
            logging.error(f"处理搜索果时出错: {str(e)}", exc_info=True)
            continue
            
    return all_results

def process_similarity_results(search_results, source_podcast_info, weights, similarity_threshold=None):
    """处理搜索结果并计算相似度"""
    if isinstance(search_results, dict):
        search_results = search_results.get('result', [])
    
    logging.debug(f"处理相似度 - 提取后的 search_results: {search_results}")

    default_weights = {'title': 0.5, 'show': 0.2, 'duration': 0.3}
    used_weights = {k: weights.get(k, default_weights[k]) for k in default_weights}
    
    all_results = calculate_similarity_scores(search_results, source_podcast_info, used_weights)
    
    # 确保使用相似度分数进行排序
    all_results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return all_results

def find_similar_youtube_videos(query, source_podcast_info, weights, similarity_threshold=None):
    """主函数：搜索并找到相似的 YouTube 视频"""
    # 根据源数据型选择合适的阈值
    if similarity_threshold is None:
        if 'platform' in source_podcast_info:
            if source_podcast_info['platform'] == 'Spotify':
                similarity_threshold = SPOTIFY_YOUTUBE_THRESHOLD
            elif source_podcast_info['platform'] == 'Apple Podcast':
                similarity_threshold = APPLE_YOUTUBE_THRESHOLD
        else:
            similarity_threshold = APPLE_YOUTUBE_THRESHOLD  # 默认值
    
    search_results = search_youtube(query)
    if not search_results:
        return None
        
    return process_similarity_results(
        search_results,
        source_podcast_info,
        weights,
        similarity_threshold
    )

def write_results_to_markdown(spotify_data, apple_results, youtube_results, output_dir, source_data):
    """结果写入Markdown格式的txt文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'podcast_search_results_{timestamp}.txt'
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            # 写入标题
            file.write("# 播客搜索结果\n\n")
            
            # Spotify 数据
            if spotify_data:
                file.write("## Spotify 源内容\n\n")
                file.write(f"- **单集标题**: {spotify_data.get('episode_title', 'N/A')}\n")
                file.write(f"- **播客节目**: {spotify_data.get('show_name', 'N/A')}\n")
                file.write(f"- **作者/频道**: {spotify_data.get('author', 'N/A')}\n")
                file.write(f"- **发布日期**: {spotify_data.get('release_date', 'N/A')}\n")
                file.write(f"- **时长(ms)**: {spotify_data.get('duration_ms', 'N/A')}\n")
                file.write(f"- **语言**: {spotify_data.get('language', 'N/A')}\n")
                file.write(f"- **URL**: {spotify_data.get('url', 'N/A')}\n")
                file.write(f"- **描述**: {spotify_data.get('description', 'N/A')[:200]}...\n\n")
            
            # Apple Podcast 数据
            if apple_results:
                file.write("## Apple Podcast 搜索结果\n\n")
                for i, result in enumerate(apple_results, 1):
                    file.write(f"### 结果 {i}\n")
                    file.write(f"- **单集标题**: {result.get('episode_title', 'N/A')}\n")
                    file.write(f"- **播客节目**: {result.get('show_name', 'N/A')}\n")
                    file.write(f"- **作者/频道**: {result.get('author', 'N/A')}\n")
                    file.write(f"- **发布日期**: {result.get('release_date', 'N/A')}\n")
                    file.write(f"- **时长(ms)**: {result.get('duration_ms', 'N/A')}\n")
                    file.write(f"- **类**: {result.get('genre', 'N/A')}\n")
                    file.write(f"- **URL**: {result.get('url', 'N/A')}\n")
                    # 只有在似度存在时才写入
                    if 'similarity' in result:
                        file.write(f"- **相似度**: {result['similarity']:.2f}\n")
                    file.write(f"- **描述**: {result.get('description', 'N/A')[:200]}...\n\n")
            else:
                file.write("## Apple Podcast 搜索结果\n\n找到相关结果\n\n")
            
            # YouTube 数据部分
            file.write("\n## YouTube 搜索结\n\n")
            
            if youtube_results is None:
                file.write("未找到符合相似阈值的 YouTube 结\n")
            elif isinstance(youtube_results, list):
                for i, result in enumerate(youtube_results, 1):
                    file.write(f"### 结果 {i}\n")
                    # 使用 'title' 而不是 'episode_title'
                    file.write(f"- **视频标题**: {result.get('title', 'N/A')}\n")
                    file.write(f"- **频道名称**: {result.get('channel', 'N/A')}\n")
                    file.write(f"- **相似度**: {result.get('similarity', 0):.4f}\n")
                    file.write(f"- **URL**: {result.get('url', 'N/A')}\n\n")
            elif isinstance(youtube_results, dict):
                file.write("### 最佳配\n")
                # 使用 'title' 而不是 'episode_title'
                file.write(f"- **视频标题**: {youtube_results.get('title', 'N/A')}\n")
                file.write(f"- **频道名称**: {youtube_results.get('channel', 'N/A')}\n")
                file.write(f"- **相似度**: {youtube_results.get('similarity', 0):.4f}\n")
                file.write(f"- **URL**: {youtube_results.get('url', 'N/A')}\n")
            
            # YouTube 数据部分之后，修改相似度计算结果部分
            file.write("\n## 详细相似度计算结果\n\n")
            
            # 先输出 Spotify 和 Apple 之间的比较���果有）
            if spotify_data and apple_results:
                file.write("### Spotify vs Apple Podcast 比较结果\n")
                for i, apple_result in enumerate(apple_results, 1):
                    if 'similarity_details' in apple_result:
                        details = apple_result['similarity_details']
                        file.write(f"\n#### 结果 {i} 的相似度详情\n")
                        file.write("##### 标题相似度\n")
                        file.write(f"- Spotify题: {spotify_data['episode_title']}\n")
                        file.write(f"- Apple标题: {apple_result.get('episode_title', 'N/A')}\n")
                        file.write(f"- 相似度: {details['title_comparison'].get('similarity_score', 0):.4f}\n\n")
                        
                        file.write("##### 节目相似度\n")
                        file.write(f"- Spotify节目: {spotify_data['show_name']}\n")
                        file.write(f"- Apple节目: {apple_result.get('show_name', 'N/A')}\n")
                        file.write(f"- 相似度: {details['show_comparison'].get('similarity_score', 0):.4f}\n\n")
                        
                        file.write("##### 时长相似度\n")
                        file.write(f"- Spotify时长(ms): {spotify_data['duration_ms']}\n")
                        file.write(f"- Apple时长(ms): {apple_result.get('duration_ms', 'N/A')}\n")
                        file.write(f"- 相似度: {details['duration_comparison'].get('duration_similarity', 0):.4f}\n\n")
                        
                        file.write("##### 总相似度\n")
                        file.write(f"- 总相似度: {details['total'].get('total_similarity', 0):.4f}\n\n")

            # YouTube 比较结果部分
            if youtube_results:
                file.write("\n### 源内容 vs YouTube 比较结果\n")
                for i, result in enumerate(youtube_results, 1):
                    if 'similarity_details' in result:
                        details = result['similarity_details']
                        file.write(f"\n#### 结果 {i} 的相似度详情\n")
                        file.write("##### 标题相似度\n")
                        file.write(f"- {source_data['platform']}标题: {source_data['episode_title']}\n")
                        # 修改这里，使用正确的键名
                        file.write(f"- YouTube标题: {result.get('title', 'N/A')}\n")
                        file.write(f"- 相似度: {details['title_comparison'].get('similarity_score', 0):.4f}\n\n")
                        
                        file.write("##### 节目相似度\n")
                        file.write(f"- {source_data['platform']}节目: {source_data['show_name']}\n")
                        file.write(f"- YouTube频道: {result.get('channel', 'N/A')}\n")
                        file.write(f"- 相似度: {details['show_comparison'].get('similarity_score', 0):.4f}\n\n")
                        
                        file.write("##### 时长相似度\n")
                        file.write(f"- {source_data['platform']}时长(ms): {source_data['duration_ms']}\n")
                        file.write(f"- YouTube时长(ms): {result.get('duration_ms', 'N/A')}\n")
                        file.write(f"- 相似度: {details['duration_comparison'].get('duration_similarity', 0):.4f}\n\n")
                        
                        file.write("##### 总相似度\n")
                        file.write(f"- 总相似度: {details['total'].get('total_similarity', 0):.4f}\n\n")

            # 修改时长比较的详细信息部分
            file.write("\n## 时长比较详细信息\n\n")
            if isinstance(youtube_results, list):
                for i, result in enumerate(youtube_results, 1):
                    file.write(f"### 结果 {i} 的时长比较\n")
                    if 'similarity_details' in result:
                        details = result['similarity_details']
                        duration_info = details.get('duration_comparison', {})
                        file.write("```\n")
                        # 使用 get 方法安全地获取时长信息
                        file.write(f"YouTube 视频时长 (ms): {result.get('duration_ms', 'N/A')}\n")
                        file.write(f"源内容时长 (ms): {source_data.get('duration_ms', 'N/A')}\n")
                        file.write(f"源内容时长 (原始格式): {source_data.get('duration', 'N/A')}\n")
                        file.write(f"时长相似度: {duration_info.get('duration_similarity', 0):.4f}\n")
                        file.write("```\n\n")
            
            # 写入时间戳
            file.write(f"\n---\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        logging.info(f"搜索结果已保存到: {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"写入Markdown文件发生错误: {str(e)}")
        raise

def write_url_mapping(spotify_data, apple_results, youtube_results, output_dir):
    """生成URL对照表文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'url_mapping_{timestamp}.txt'
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write("# URL对照表\n\n")
            
            # 添加阈值和权重信息
            file.write("## 配置信息\n")
            file.write("### 相似度阈值\n")
            file.write(f"- Spotify-Apple 匹配阈值: {SPOTIFY_APPLE_THRESHOLD}\n")
            file.write(f"- Spotify-YouTube 匹配阈值: {SPOTIFY_YOUTUBE_THRESHOLD}\n")
            file.write(f"- Apple-YouTube 匹配阈值: {APPLE_YOUTUBE_THRESHOLD}\n\n")
            
            file.write("### 相似度权重\n")
            file.write("- 标题权重: 0.5\n")
            file.write("- 节目权重: 0.3\n")
            file.write("- 时长权重: 0.2\n\n")
            
            # 写入源URL（使用更明确的格式）
            if spotify_data:
                file.write(f"Spotify URL: {spotify_data.get('url', 'N/A')}\n\n")
            elif apple_results and isinstance(apple_results, list) and len(apple_results) > 0:
                file.write(f"Apple Podcast URL: {apple_results[0].get('url', 'N/A')}\n\n")
            
            # 写入匹配的Apple Podcast URLs（新格式）
            file.write("## Apple Podcast匹配结果\n")
            if apple_results and len(apple_results) > 0:
                max_similarity = max((result.get('similarity', 0) for result in apple_results), default=0)
                max_result = max(apple_results, key=lambda x: x.get('similarity', 0), default=None)
                
                if max_similarity >= SPOTIFY_APPLE_THRESHOLD:
                    for result in apple_results:
                        if result.get('similarity', 0) >= SPOTIFY_APPLE_THRESHOLD:
                            file.write(f"相似度: {result.get('similarity', 0):.4f}\n")
                            file.write(f"相似的Apple URL: {result.get('url', 'N/A')}\n\n")
                else:
                    file.write(f"没有满足阈值({SPOTIFY_APPLE_THRESHOLD})的url，最高匹配相似度为: {max_similarity:.4f}\n")
                    if max_result:
                        file.write(f"最高相似度对应的URL: {max_result.get('url', 'N/A')}\n")
            else:
                # 从search_apple_podcast的结果中获取最高相似度
                try:
                    output_dir = setup_output_directory()
                    # 获取最新的apple_similarity_results文件
                    similarity_files = glob.glob(os.path.join(output_dir, 'apple_similarity_results_*.json'))
                    if similarity_files:
                        latest_file = max(similarity_files, key=os.path.getctime)
                        with open(latest_file, 'r', encoding='utf-8') as f:
                            similarity_data = json.load(f)
                            
                        # 从all_comparisons中获取最高相似度
                        if 'all_comparisons' in similarity_data:
                            all_comparisons = similarity_data['all_comparisons']
                            if all_comparisons:
                                max_similarity = max(
                                    (comp['similarity_calculation']['total_similarity'] 
                                     for comp in all_comparisons 
                                     if 'similarity_calculation' in comp),
                                    default=0
                                )
                                max_result = max(
                                    all_comparisons,
                                    key=lambda x: x['similarity_calculation']['total_similarity']
                                    if 'similarity_calculation' in x else 0
                                )
                                
                                file.write(f"没有满足阈值({SPOTIFY_APPLE_THRESHOLD})的url，最高匹配相似度为: {max_similarity:.4f}\n")
                                if max_result and 'apple_podcast' in max_result:
                                    file.write(f"最高相似度对应的URL: {max_result['apple_podcast'].get('url', 'N/A')}\n")
                            else:
                                file.write("没有找到Apple Podcast匹配结果\n")
                        else:
                            file.write("没有找到Apple Podcast匹配结果\n")
                    else:
                        file.write("没有找到Apple Podcast匹配结果\n")
                except Exception as e:
                    logging.error(f"读取Apple Podcast相似度结果时发生错误: {str(e)}")
                    file.write("没有找到Apple Podcast匹配结果\n")
            file.write("\n")
            
            # 写入匹配的YouTube URLs（新格式）
            file.write("## YouTube匹配结果\n")
            if youtube_results:
                if isinstance(youtube_results, list):
                    max_similarity = max((result.get('similarity', 0) for result in youtube_results), default=0)
                    max_result = max(youtube_results, key=lambda x: x.get('similarity', 0), default=None)
                    threshold = SPOTIFY_YOUTUBE_THRESHOLD if spotify_data else APPLE_YOUTUBE_THRESHOLD
                    
                    if max_similarity >= threshold:
                        for result in youtube_results:
                            if result.get('similarity', 0) >= threshold:
                                file.write(f"相似度: {result.get('similarity', 0):.4f}\n")
                                file.write(f"相似的YouTube URL: {result.get('url', 'N/A')}\n\n")
                    else:
                        file.write(f"没有满足阈值({threshold})的url，最高匹配��似度为: {max_similarity:.4f}\n")
                        if max_result:
                            file.write(f"最高相似度对应的URL: {max_result.get('url', 'N/A')}\n")
                elif isinstance(youtube_results, dict):
                    similarity = youtube_results.get('similarity', 0)
                    threshold = SPOTIFY_YOUTUBE_THRESHOLD if spotify_data else APPLE_YOUTUBE_THRESHOLD
                    if similarity >= threshold:
                        file.write(f"相似度: {similarity:.4f}\n")
                        file.write(f"相似的YouTube URL: {youtube_results.get('url', 'N/A')}\n")
                    else:
                        file.write(f"没有满足阈值({threshold})的url，最高匹配相似度为: {similarity:.4f}\n")
                        file.write(f"最高相似度对应的URL: {youtube_results.get('url', 'N/A')}\n")
            else:
                file.write("没有找到YouTube匹配结果\n")
            
            # 写入时间戳
            file.write(f"\n---\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        logging.info(f"URL对照表已保存到: {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"写入URL对照表文件时发生错误: {str(e)}")
        raise

def extract_apple_podcast_ids(url):
    """从 Apple Podcast URL 中提取 podcast ID 和 episode ID"""
    try:
        # 示例 URL: https://podcasts.apple.com/cn/podcast/391-the-reckoning/id733163012?i=1000676525003
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        # 取 podcast ID (去掉'id'前缀)
        podcast_id = next((part[2:] for part in path_parts if part.startswith('id')), None)
        
        # 从查询参数中提取 episode ID
        query_params = parse_qs(parsed_url.query)
        episode_id = query_params.get('i', [None])[0]
        
        logging.info(f"提取到 Podcast ID: {podcast_id}, Episode ID: {episode_id}")
        return podcast_id, episode_id
    except Exception as e:
        logging.error(f"解析 Apple Podcast URL 时发生错误: {str(e)}")
        return None, None

def get_apple_podcast_episode(url):
    """取 Apple Podcast 集信息"""
    logging.info("开始获取 Apple Podcast 节目信息...")
    try:
        podcast_id, episode_id = extract_apple_podcast_ids(url)
        if not (podcast_id and episode_id):
            raise ValueError("无法从 URL 中提取必要的 ID")

        # 使用 iTunes Search API 获取客信息
        lookup_url = f"https://itunes.apple.com/lookup?id={podcast_id}&entity=podcastEpisode"
        try:
            podcast_response = requests.get(lookup_url)
            podcast_response.raise_for_status()  # 检查请求是否成功
            podcast_data = podcast_response.json()
            if 'resultCount' in podcast_data and podcast_data['resultCount'] > 0:  # 检查返回数据是否包含结果
                logging.info(f"成功从 Apple Podcast 获取返回数据: {podcast_data}")
            else:
                logging.warning(f"从 Apple Podcast 获取的返回数据为空或无结果: {podcast_data}")
        except requests.exceptions.HTTPError as e:
            logging.error(f" Apple Podcast 获取数据时发生 HTTP 错误: {str(e)}")
            podcast_data = None
        except Exception as e:
            logging.error(f"从 Apple Podcast 获取数据时发生错误: {str(e)}")
            podcast_data = None

        # 保原返回数据用于调试
        with open('apple_podcast_raw_results.json', 'w', encoding='utf-8') as f:
            json.dump(podcast_data, f, ensure_ascii=False, indent=4)
        logging.info("Apple Podcast 原始数据已保存到 apple_podcast_raw_results.json")

        # 在有集中找目标单集
        if podcast_data['resultCount'] > 0:
            for episode in podcast_data['results']:
                # 检查是否是播客本身的数据而不是单集
                if episode.get('kind') == 'podcast':
                    continue
                    
                # 通过 trackId 匹具体单集
                if str(episode.get('trackId')) == episode_id:
                    episode_info = {
                        'platform': 'Apple Podcast',
                        'episode_title': episode.get('trackName', ''),
                        'show_name': episode.get('collectionName', ''),
                        'author': episode.get('artistName', ''),
                        'url': url,
                        'duration_ms': episode.get('trackTimeMillis', 0),
                        'release_date': episode.get('releaseDate', ''),
                        'description': episode.get('description', ''),
                        'genre': episode.get('genres', [''])[0],
                        'language': episode.get('languageCodesISO2A', ''),
                        'artwork_url': episode.get('artworkUrl600', '')
                    }
                    logging.info("成功获取 Apple Podcast 节目信息")
                    return episode_info
            
            logging.error(f"客 {podcast_id} 中未找到单集 {episode_id}")
            raise ValueError(f"未找到对应的单集息 (Episode ID: {episode_id})")
        else:
            raise ValueError(f"未找到播客信息 (Podcast ID: {podcast_id})")

    except Exception as e:
        logging.error(f"获取 Apple Podcast 信息时发生错误: {str(e)}")
        raise

class PodcastMatcher:
    def __init__(self):
        """初始化播客匹配服务"""
        self.output_dir = setup_output_directory()
        self.weights = {
            'title': 0.5,
            'show': 0.3,
            'duration': 0.2
        }

    def match_podcast_url(self, podcast_url: str) -> str:
        """
        根据输入的播客URL，返回相似度最高的YouTube URL
        
        Args:
            podcast_url (str): Spotify或Apple播客的URL
            
        Returns:
            str: 匹配到的YouTube URL，如果未找到匹配则返回空字符串
        """
        try:
            source_data = None
            youtube_url = ""

            # 获取源平台信息
            if 'spotify.com' in podcast_url:
                source_data = get_spotify_episode(podcast_url)
            elif 'apple.com' in podcast_url:
                source_data = get_apple_podcast_episode(podcast_url)
            else:
                logging.error("不支持的URL格式，仅支持Spotify和Apple Podcast URL")
                return ""

            # 如果有源数据，尝试查找YouTube匹配
            if source_data:
                youtube_results = find_similar_youtube_videos(
                    source_data['episode_title'],
                    source_data,
                    self.weights
                )
                
                # 获取相似度最高的YouTube URL
                if youtube_results:
                    best_match = max(youtube_results, key=lambda x: x.get('similarity', 0))
                    if best_match.get('similarity', 0) >= SPOTIFY_YOUTUBE_THRESHOLD:
                        youtube_url = best_match.get('url', '')

                # 可选：保存详细结果用于调试
                self._save_results(
                    source_data if 'spotify.com' in podcast_url else None,
                    [source_data] if 'apple.com' in podcast_url else [],
                    youtube_results,
                    podcast_url
                )

            return youtube_url

        except Exception as e:
            logging.error(f"匹配播客URL时发生错误: {str(e)}")
            return ""

    def _save_results(self, spotify_data, apple_results, youtube_results, source_url):
        """保存匹配结果到文件（用于调试）"""
        try:
            write_results_to_markdown(
                spotify_data,
                apple_results,
                youtube_results,
                self.output_dir,
                spotify_data or apple_results[0]
            )
            
            write_url_mapping(
                spotify_data,
                apple_results,
                youtube_results,
                self.output_dir
            )
        except Exception as e:
            logging.error(f"保存结果文件时发生错误: {str(e)}")

# 使用示例：
if __name__ == "__main__":
    # 用于测试的示例代码
    matcher = PodcastMatcher()
    test_url = "https://open.spotify.com/episode/..."
    result_url = matcher.match_podcast_url(test_url)
    print(f"匹配到的URL: {result_url}")

