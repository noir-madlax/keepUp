#!/usr/bin/env python3
"""
使用 TikHub API 获取 B站视频信息 (增强版)
API文档: https://api.tikhub.io/#/Bilibili-Web-API/fetch_one_video_v3_api_v1_bilibili_web_fetch_one_video_v3_get
测试视频: https://www.bilibili.com/video/BV1sWobYuEa6

增强功能:
1. 尝试获取字幕信息（如果API支持）
2. 获取更详细的视频统计数据  
3. 提供更完整的 Keep Up 系统数据结构
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

# 从环境变量获取API密钥
TIKHUB_API_KEY = "44wGVlZTxXwGkXQljmuJpycPy0AHsqGF6JQj3gD3ukhczVZVS/RN+xm6Lg=="
TIKHUB_BASE_URL = "https://api.tikhub.io"
TIKHUB_API_ENDPOINT = "/api/v1/bilibili/web/fetch_one_video_v3"

# 测试视频URL
TEST_VIDEO_URL = "https://www.bilibili.com/video/BV1sWobYuEa6"

class TikHubBilibiliEnhancedAPI:
    """TikHub B站视频信息获取器 (增强版)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = TIKHUB_BASE_URL
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头，包含正确的认证信息"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "KeepUp-BilibiliBot/1.0"
        }
    
    def fetch_video_info(self, video_url: str) -> Optional[Dict]:
        """
        使用 TikHub API 获取视频信息
        
        Args:
            video_url: B站视频URL
            
        Returns:
            API 返回的视频信息数据，失败返回 None
        """
        print(f"🚀 使用 TikHub API 获取视频信息...")
        print(f"🔗 视频URL: {video_url}")
        print(f"🔑 API Key: {self.api_key[:20]}...")
        
        try:
            # 构建请求
            url = f"{self.base_url}{TIKHUB_API_ENDPOINT}"
            params = {
                "url": video_url
            }
            headers = self._get_headers()
            
            print(f"📡 请求URL: {url}")
            print(f"📋 请求参数: {params}")
            print(f"🔧 请求头: Authorization: Bearer {self.api_key[:10]}...")
            
            # 发送请求
            response = requests.get(url, params=params, headers=headers)
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 调用成功")
                
                # 打印原始响应数据的结构（用于调试）
                print(f"🔍 响应数据结构预览:")
                if isinstance(data, dict):
                    print(f"   - 顶级字段: {list(data.keys())}")
                    if "data" in data and isinstance(data["data"], dict):
                        print(f"   - data字段内容: {list(data['data'].keys())}")
                
                return data
            else:
                print(f"❌ API 调用失败: HTTP {response.status_code}")
                print(f"📝 响应内容: {response.text[:500]}...")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return None
    
    def extract_keep_up_data(self, tikhub_data: Dict) -> Dict:
        """
        从 TikHub API 返回数据中提取 Keep Up 系统需要的信息
        
        Args:
            tikhub_data: TikHub API 返回的原始数据
            
        Returns:
            符合 Keep Up 系统要求的数据结构
        """
        print(f"🔄 转换数据结构为 Keep Up 系统格式...")
        
        try:
            # 检查API返回是否成功
            if not tikhub_data or tikhub_data.get("code") != 200:
                error_msg = tikhub_data.get("message", "Unknown error") if tikhub_data else "No data returned"
                print(f"❌ API 返回错误: {error_msg}")
                return {"error": error_msg}
            
            # 提取视频数据
            video_data = tikhub_data.get("data", {})
            if not video_data:
                print(f"❌ 无视频数据")
                return {"error": "No video data found"}
            
            # 提取基本信息
            title = video_data.get("title", "未获取到标题")
            desc = video_data.get("desc", "")
            duration = video_data.get("duration", 0)
            
            # 尝试获取更多统计数据
            stat = video_data.get("stat", {})
            view = stat.get("view", video_data.get("view", 0))
            like = stat.get("like", video_data.get("like", 0))
            coin = stat.get("coin", 0)  # 投币数
            favorite = stat.get("favorite", 0)  # 收藏数
            share = stat.get("share", 0)  # 分享数
            reply = stat.get("reply", 0)  # 评论数
            danmaku = stat.get("danmaku", 0)  # 弹幕数
            
            bvid = video_data.get("bvid", "")
            aid = video_data.get("aid", 0)  # AV号
            
            # 提取作者信息
            owner = video_data.get("owner", {})
            author_name = owner.get("name", "未知作者")
            author_face = owner.get("face", "")
            author_mid = owner.get("mid", "")
            
            # 提取封面信息
            pic = video_data.get("pic", "")
            
            # 提取发布时间
            pubdate = video_data.get("pubdate", 0)
            publish_date = datetime.fromtimestamp(pubdate).isoformat() if pubdate else None
            
            # 尝试提取标签信息
            tags = []
            if "tags" in video_data:
                for tag in video_data.get("tags", []):
                    if isinstance(tag, dict):
                        tags.append(tag.get("tag_name", str(tag)))
                    else:
                        tags.append(str(tag))
            
            # 如果没有标签，使用默认标签
            if not tags:
                tags = ["视频", "bilibili"]
            
            # 尝试获取分页信息（可能包含字幕）
            pages = video_data.get("pages", [])
            page_info = []
            for page in pages:
                page_info.append({
                    "cid": page.get("cid", ""),
                    "page": page.get("page", 1),
                    "part": page.get("part", ""),
                    "duration": page.get("duration", 0)
                })
            
            # 构造更完整的 Keep Up 系统数据结构
            keep_up_data = {
                # VideoInfo 结构
                "video_info": {
                    "title": title,
                    "description": desc,  # 对于视频，描述可能比较简短，实际内容在字幕中
                    "author": {
                        "name": author_name,
                        "icon": author_face,
                        "platform": "bilibili",
                        "channel_id": str(author_mid)
                    },
                    "article": {
                        "title": title,
                        "content": desc,  # 这里应该是字幕内容，但TikHub API可能不直接提供
                        "channel": "bilibili", 
                        "tags": tags,
                        "original_link": TEST_VIDEO_URL,
                        "publish_date": publish_date,
                        "cover_image_url": pic
                    }
                },
                
                # 增强的统计数据
                "enhanced_stats": {
                    "view_count": view,
                    "like_count": like,
                    "coin_count": coin,
                    "favorite_count": favorite,
                    "share_count": share,
                    "reply_count": reply,
                    "danmaku_count": danmaku,
                    "duration_seconds": duration,
                    "aid": aid,
                    "bvid": bvid
                },
                
                # 分页信息
                "pages_info": page_info,
                
                # 原始数据（调试用）
                "raw_data": {
                    "title": title,
                    "description": desc,
                    "duration": f"{duration}秒 ({duration//60}分{duration%60}秒)",
                    "view_count": f"{view:,}",
                    "like_count": f"{like:,}",
                    "coin_count": f"{coin:,}",
                    "favorite_count": f"{favorite:,}",
                    "bvid": bvid,
                    "aid": aid,
                    "author": {
                        "name": author_name,
                        "avatar": author_face,
                        "mid": author_mid
                    },
                    "cover_image": pic,
                    "publish_date": publish_date,
                    "tags": tags,
                    "pages_count": len(pages)
                },
                
                # API 信息
                "api_info": {
                    "source": "TikHub API",
                    "endpoint": TIKHUB_API_ENDPOINT,
                    "timestamp": self.timestamp,
                    "success": True
                },
                
                # 字幕提示信息
                "subtitle_note": {
                    "status": "字幕内容需要额外的API调用获取",
                    "suggestion": "TikHub API 的 fetch_one_video_v3 端点主要返回视频基本信息，字幕内容可能需要使用其他端点获取",
                    "pages_available": len(pages),
                    "next_steps": "如需字幕内容，可以使用页面CID调用字幕相关的API端点"
                }
            }
            
            print(f"✅ 数据转换完成")
            print(f"📺 视频标题: {title}")
            print(f"👤 作者: {author_name}")
            print(f"📊 播放: {view:,}, 点赞: {like:,}, 投币: {coin:,}")
            print(f"⏱️ 时长: {duration//60}分{duration%60}秒")
            print(f"📄 分页数: {len(pages)}")
            print(f"🏷️ 标签: {', '.join(tags)}")
            
            return keep_up_data
            
        except Exception as e:
            print(f"❌ 数据转换失败: {str(e)}")
            return {"error": f"Data conversion failed: {str(e)}"}
    
    def save_enhanced_result_to_txt(self, data: Dict, success: bool = True) -> str:
        """
        保存增强结果到txt文件
        
        Args:
            data: 要保存的数据
            success: 是否成功获取数据
            
        Returns:
            保存的文件路径
        """
        filename = f"bilibili_video_info_tikhub_enhanced_{self.timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("B站视频信息获取结果 (TikHub API - 增强版)\n")
            f.write("=" * 80 + "\n\n")
            
            if success and "error" not in data:
                video_info = data.get("video_info", {})
                raw_data = data.get("raw_data", {})
                enhanced_stats = data.get("enhanced_stats", {})
                pages_info = data.get("pages_info", [])
                subtitle_note = data.get("subtitle_note", {})
                
                f.write("📺 视频基本信息:\n")
                f.write("-" * 40 + "\n")
                f.write(f"标题: {raw_data.get('title', 'N/A')}\n")
                f.write(f"描述: {raw_data.get('description', 'N/A')}\n")
                f.write(f"时长: {raw_data.get('duration', 'N/A')}\n")
                f.write(f"BV号: {raw_data.get('bvid', 'N/A')}\n")
                f.write(f"AV号: {raw_data.get('aid', 'N/A')}\n")
                f.write(f"发布时间: {raw_data.get('publish_date', 'N/A')}\n")
                f.write(f"分页数: {raw_data.get('pages_count', 'N/A')}\n\n")
                
                f.write("📊 详细统计数据:\n")
                f.write("-" * 40 + "\n")
                f.write(f"播放量: {raw_data.get('view_count', 'N/A')}\n")
                f.write(f"点赞数: {raw_data.get('like_count', 'N/A')}\n")
                f.write(f"投币数: {raw_data.get('coin_count', 'N/A')}\n")
                f.write(f"收藏数: {raw_data.get('favorite_count', 'N/A')}\n")
                f.write(f"分享数: {enhanced_stats.get('share_count', 'N/A')}\n")
                f.write(f"评论数: {enhanced_stats.get('reply_count', 'N/A')}\n")
                f.write(f"弹幕数: {enhanced_stats.get('danmaku_count', 'N/A')}\n\n")
                
                f.write("👤 作者信息:\n")
                f.write("-" * 40 + "\n")
                author = raw_data.get('author', {})
                f.write(f"作者名称: {author.get('name', 'N/A')}\n")
                f.write(f"头像URL: {author.get('avatar', 'N/A')}\n")
                f.write(f"用户ID: {author.get('mid', 'N/A')}\n")
                f.write(f"平台: bilibili\n\n")
                
                f.write("🏷️ 标签信息:\n")
                f.write("-" * 40 + "\n")
                tags = raw_data.get('tags', [])
                f.write(f"标签: {', '.join(tags) if tags else 'N/A'}\n\n")
                
                if pages_info:
                    f.write("📄 分页信息:\n")
                    f.write("-" * 40 + "\n")
                    for i, page in enumerate(pages_info, 1):
                        f.write(f"分页 {i}:\n")
                        f.write(f"  - CID: {page.get('cid', 'N/A')}\n")
                        f.write(f"  - 标题: {page.get('part', 'N/A')}\n")
                        f.write(f"  - 时长: {page.get('duration', 0)}秒\n")
                    f.write("\n")
                
                f.write("💡 字幕信息说明:\n")
                f.write("-" * 40 + "\n")
                f.write(f"状态: {subtitle_note.get('status', 'N/A')}\n")
                f.write(f"建议: {subtitle_note.get('suggestion', 'N/A')}\n")
                f.write(f"后续步骤: {subtitle_note.get('next_steps', 'N/A')}\n\n")
                
                f.write("📄 Keep Up 系统数据结构:\n")
                f.write("-" * 40 + "\n")
                f.write("VideoInfo JSON:\n")
                f.write(json.dumps(video_info, ensure_ascii=False, indent=2))
                f.write("\n\n")
                
            else:
                f.write("❌ 错误信息:\n")
                f.write("-" * 40 + "\n")
                error_msg = data.get("error", "未知错误")
                f.write(f"错误: {error_msg}\n\n")
            
            f.write("📋 API调用信息:\n")
            f.write("-" * 40 + "\n")
            api_info = data.get("api_info", {})
            f.write(f"API来源: {api_info.get('source', 'TikHub API')}\n")
            f.write(f"端点: {api_info.get('endpoint', TIKHUB_API_ENDPOINT)}\n")
            f.write(f"时间戳: {api_info.get('timestamp', self.timestamp)}\n")
            f.write(f"成功: {api_info.get('success', success)}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")
        
        print(f"📝 结果已保存到: {filename}")
        return filename

def main():
    """主函数"""
    print("🚀 开始使用 TikHub API 获取 B站视频信息 (增强版)")
    print("=" * 60)
    
    # 初始化API客户端
    api_client = TikHubBilibiliEnhancedAPI(TIKHUB_API_KEY)
    
    # 获取视频信息
    tikhub_data = api_client.fetch_video_info(TEST_VIDEO_URL)
    
    if tikhub_data:
        # 转换数据格式
        keep_up_data = api_client.extract_keep_up_data(tikhub_data)
        
        # 保存结果
        filename = api_client.save_enhanced_result_to_txt(keep_up_data, success=True)
        print(f"✅ 处理完成，结果保存在: {filename}")
        
    else:
        # 保存错误结果
        error_data = {
            "error": "API调用失败，请检查网络连接和API密钥",
            "api_info": {
                "source": "TikHub API",
                "endpoint": TIKHUB_API_ENDPOINT,
                "success": False
            }
        }
        filename = api_client.save_enhanced_result_to_txt(error_data, success=False)
        print(f"❌ 处理失败，错误信息保存在: {filename}")

if __name__ == "__main__":
    main() 