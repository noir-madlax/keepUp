#!/usr/bin/env python3
"""
使用cookie登录凭证获取B站视频字幕
基于LangChain的Bilibili文档加载器和用户提供的cookie
视频链接: https://www.bilibili.com/video/BV1Bz421h7B1/
"""

import os
import json
import asyncio
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from urllib.parse import unquote

# 创建 output 目录  
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

class BiliBiliCookieTester:
    """使用Cookie获取B站字幕的测试类"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.load_cookies()
    
    def load_cookies(self):
        """从cookie文件加载登录凭证"""
        cookie_file = Path(__file__).parent / "blibli-cookie.txt"
        
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # 提取关键cookie信息
            self.sessdata = None
            self.bili_jct = None
            self.buvid3 = None
            self.dedeuserid = None
            
            for cookie in cookies_data:
                if cookie['name'] == 'SESSDATA':
                    self.sessdata = unquote(cookie['value'])
                elif cookie['name'] == 'bili_jct':
                    self.bili_jct = cookie['value']
                elif cookie['name'] == 'buvid3':
                    self.buvid3 = cookie['value']
                elif cookie['name'] == 'DedeUserID':
                    self.dedeuserid = cookie['value']
            
            print(f"✅ 成功加载cookie信息")
            print(f"   - SESSDATA: {self.sessdata[:20]}..." if self.sessdata else "   - SESSDATA: 未找到")
            print(f"   - bili_jct: {self.bili_jct}" if self.bili_jct else "   - bili_jct: 未找到")
            print(f"   - DedeUserID: {self.dedeuserid}" if self.dedeuserid else "   - DedeUserID: 未找到")
            
            # 构建请求头
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.bilibili.com/',
                'Cookie': f'SESSDATA={self.sessdata}; bili_jct={self.bili_jct}; buvid3={self.buvid3}; DedeUserID={self.dedeuserid}'
            }
            
        except Exception as e:
            print(f"❌ 加载cookie失败: {e}")
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
    
    def save_result(self, filename: str, data: any) -> None:
        """保存结果到文件（仅保存成功结果）"""
        if isinstance(data, dict):
            if data.get("code") and data.get("code") != 0:
                print(f"⚠️ 跳过保存错误结果: {filename} (code: {data.get('code')})")
                return
        
        file_path = OUTPUT_DIR / f"{filename}_{self.timestamp}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"📝 结果已保存到: {file_path}")
    
    def save_subtitle_content(self, filename: str, content: str, subtitle_type: str = "srt") -> None:
        """保存字幕内容到文件"""
        file_path = OUTPUT_DIR / f"{filename}_{self.timestamp}.{subtitle_type}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 字幕内容已保存到: {file_path}")
    
    def convert_to_srt(self, subtitle_body: List[Dict]) -> str:
        """将B站字幕格式转换为SRT格式"""
        srt_content = ""
        for i, item in enumerate(subtitle_body, 1):
            start_time = self.seconds_to_srt_time(item.get("from", 0))
            end_time = self.seconds_to_srt_time(item.get("to", 0))
            content = item.get("content", "")
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{content}\n\n"
        
        return srt_content
    
    def seconds_to_srt_time(self, seconds: float) -> str:
        """将秒数转换为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def extract_bv_id(self, video_url: str) -> str:
        """从URL中提取BV号"""
        if "/video/" in video_url:
            bv_part = video_url.split("/video/")[1]
            if "/" in bv_part:
                bv_id = bv_part.split("/")[0]
            else:
                bv_id = bv_part
            if "?" in bv_id:
                bv_id = bv_id.split("?")[0]
            return bv_id
        return ""
    
    def test_bilibili_with_cookies(self, video_url: str) -> Dict:
        """使用cookie获取B站视频字幕"""
        print(f"🚀 使用cookie获取B站视频字幕")
        print(f"🔗 视频URL: {video_url}")
        
        result = {
            "video_url": video_url,
            "success": False,
            "subtitles_found": 0,
            "subtitle_details": [],
            "errors": []
        }
        
        try:
            bv_id = self.extract_bv_id(video_url)
            print(f"📋 提取到BV号: {bv_id}")
            
            if not bv_id:
                result["errors"].append("无法提取BV号")
                return result
            
            # Step 1: 获取视频基本信息和CID
            print(f"📥 获取视频基本信息...")
            video_info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
            
            response = requests.get(video_info_url, headers=self.headers)
            if response.status_code != 200:
                result["errors"].append(f"获取视频信息失败: HTTP {response.status_code}")
                return result
            
            video_data = response.json()
            self.save_result("video_info_with_cookies", video_data)
            
            if video_data.get("code") != 0:
                result["errors"].append(f"视频信息API错误: {video_data.get('message')}")
                return result
            
            video_info = video_data["data"]
            print(f"🎬 视频标题: {video_info.get('title', 'Unknown')}")
            print(f"📊 视频时长: {video_info.get('duration', 'Unknown')} 秒")
            
            # 获取所有分页的CID
            pages = video_info.get("pages", [])
            print(f"📄 视频共有 {len(pages)} 个分页")
            
            total_subtitles = 0
            
            # 处理每个分页
            for page_idx, page in enumerate(pages):
                cid = page['cid']
                page_title = page.get('part', f'P{page_idx+1}')
                
                print(f"\n🔍 处理分页 {page_idx+1}: {page_title} (CID: {cid})")
                
                # Step 2: 获取播放器信息（包含字幕信息）
                print(f"📝 获取播放器信息和字幕列表...")
                player_url = f"https://api.bilibili.com/x/player/v2"
                player_params = {
                    "bvid": bv_id,
                    "cid": cid
                }
                
                player_response = requests.get(player_url, headers=self.headers, params=player_params)
                if player_response.status_code != 200:
                    error_msg = f"分页 {page_idx+1} 播放器信息获取失败: HTTP {player_response.status_code}"
                    print(f"❌ {error_msg}")
                    result["errors"].append(error_msg)
                    continue
                
                player_data = player_response.json()
                self.save_result(f"player_info_p{page_idx+1}", player_data)
                
                if player_data.get("code") != 0:
                    error_msg = f"分页 {page_idx+1} 播放器API错误: {player_data.get('message')}"
                    print(f"❌ {error_msg}")
                    result["errors"].append(error_msg)
                    continue
                
                # 检查字幕信息
                subtitle_info = player_data.get("data", {}).get("subtitle", {})
                subtitles = subtitle_info.get("subtitles", [])
                
                print(f"🌐 找到 {len(subtitles)} 个字幕")
                
                if subtitles:
                    for subtitle_idx, subtitle in enumerate(subtitles):
                        lan = subtitle.get('lan', 'unknown')
                        lan_doc = subtitle.get('lan_doc', '未知语言')
                        subtitle_url = subtitle.get('subtitle_url', '')
                        
                        print(f"  📄 字幕 {subtitle_idx+1}: {lan_doc} ({lan})")
                        print(f"      URL: {subtitle_url}")
                        
                        subtitle_detail = {
                            "page": page_idx + 1,
                            "page_title": page_title,
                            "cid": cid,
                            "lan": lan,
                            "lan_doc": lan_doc,
                            "subtitle_url": subtitle_url,
                            "downloaded": False,
                            "content_preview": ""
                        }
                        
                        # Step 3: 下载字幕内容
                        if subtitle_url:
                            try:
                                print(f"      📥 下载字幕内容...")
                                
                                # 确保URL是完整的
                                if subtitle_url.startswith("//"):
                                    subtitle_url = "https:" + subtitle_url
                                elif not subtitle_url.startswith("http"):
                                    subtitle_url = "https://" + subtitle_url
                                
                                subtitle_response = requests.get(subtitle_url, headers=self.headers)
                                if subtitle_response.status_code == 200:
                                    subtitle_content = subtitle_response.text
                                    subtitle_data = json.loads(subtitle_content)
                                    
                                    if "body" in subtitle_data and subtitle_data["body"]:
                                        subtitle_detail["downloaded"] = True
                                        subtitle_detail["content_preview"] = subtitle_data["body"][0].get("content", "")[:100]
                                        
                                        # 保存原始字幕内容
                                        self.save_subtitle_content(f"subtitle_raw_p{page_idx+1}_{lan}", subtitle_content, "json")
                                        
                                        # 转换为SRT格式
                                        srt_content = self.convert_to_srt(subtitle_data["body"])
                                        self.save_subtitle_content(f"subtitle_srt_p{page_idx+1}_{lan}", srt_content, "srt")
                                        
                                        total_subtitles += 1
                                        print(f"      ✅ 成功下载字幕内容")
                                        
                                        # 显示字幕预览
                                        preview_lines = srt_content.split('\n')[:8]
                                        print(f"      📖 字幕预览:\n{chr(10).join(['        ' + line for line in preview_lines])}")
                                        
                                        # 显示字幕统计
                                        subtitle_lines = len(subtitle_data["body"])
                                        print(f"      📊 字幕共 {subtitle_lines} 行")
                                        
                                    else:
                                        print(f"      ⚠️ 字幕内容为空")
                                else:
                                    print(f"      ❌ 下载失败: HTTP {subtitle_response.status_code}")
                            
                            except Exception as e:
                                print(f"      ❌ 下载字幕失败: {e}")
                        else:
                            print(f"      ⚠️ 字幕URL为空")
                        
                        result["subtitle_details"].append(subtitle_detail)
                else:
                    print(f"⚠️ 该分页未找到字幕")
            
            result["success"] = True
            result["subtitles_found"] = total_subtitles
            
            # 保存最终结果
            self.save_result("bilibili_cookie_test_result", result)
            
            return result
            
        except Exception as e:
            error_msg = f"处理错误: {e}"
            print(f"❌ {error_msg}")
            result["errors"].append(error_msg)
            return result
    
    def test_langchain_bilibili_loader(self, video_url: str):
        """尝试使用LangChain的Bilibili加载器"""
        print(f"\n🔧 尝试使用LangChain Bilibili加载器...")
        
        try:
            # 先检查是否安装了langchain
            try:
                from langchain_community.document_loaders import BilibiliLoader
                print(f"✅ 成功导入LangChain BilibiliLoader")
                
                # 使用加载器
                loader = BilibiliLoader([video_url])
                documents = loader.load()
                
                print(f"📊 LangChain加载器获得 {len(documents)} 个文档")
                
                for i, doc in enumerate(documents):
                    print(f"📄 文档 {i+1}:")
                    print(f"   - 内容长度: {len(doc.page_content)} 字符")
                    print(f"   - 元数据: {doc.metadata}")
                    if doc.page_content:
                        print(f"   - 内容预览: {doc.page_content[:200]}...")
                        
                        # 保存LangChain获取的内容
                        self.save_subtitle_content(f"langchain_content_{i+1}", doc.page_content, "txt")
                
                return len(documents)
                
            except ImportError:
                print(f"⚠️ LangChain未安装或BilibiliLoader不可用")
                return 0
                
        except Exception as e:
            print(f"❌ LangChain加载器失败: {e}")
            return 0

def main():
    """主函数"""
    print("🚀 使用Cookie获取B站视频字幕测试")
    print("=" * 60)
    
    tester = BiliBiliCookieTester()
    
    # 用户提供的有字幕的视频
    video_url = "https://www.bilibili.com/video/BV1Bz421h7B1/"
    
    try:
        # 方法1: 使用cookie直接调用API
        result = tester.test_bilibili_with_cookies(video_url)
        
        print(f"\n📊 Cookie方法结果摘要:")
        print(f"   - 视频URL: {video_url}")
        print(f"   - 测试成功: {'是' if result['success'] else '否'}")
        print(f"   - 找到字幕: {result['subtitles_found']} 个")
        
        if result['subtitle_details']:
            print(f"   - 字幕详情:")
            for detail in result['subtitle_details']:
                status = "✅ 成功" if detail['downloaded'] else "❌ 失败"
                print(f"     * P{detail['page']} {detail['lan_doc']} ({detail['lan']}): {status}")
                if detail.get('content_preview'):
                    print(f"       预览: {detail['content_preview'][:50]}...")
        
        if result.get('errors'):
            print(f"   - 错误: {'; '.join(result['errors'])}")
        
        # 方法2: 尝试LangChain加载器
        langchain_docs = tester.test_langchain_bilibili_loader(video_url)
        
        # 最终总结
        total_success = result['subtitles_found'] + langchain_docs
        
        if total_success > 0:
            print(f"\n✅ 总共成功获取 {total_success} 个字幕/文档！")
            print(f"📁 结果保存在: {OUTPUT_DIR}")
        else:
            print(f"\n⚠️ 未能获取任何字幕内容")
        
        print(f"\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main() 