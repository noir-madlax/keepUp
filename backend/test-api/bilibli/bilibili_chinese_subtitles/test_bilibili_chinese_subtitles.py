#!/usr/bin/env python3
"""
获取B站视频中文字幕
只获取中文字幕版本，优化后的脚本
视频链接示例: https://www.bilibili.com/video/BV1sWobYuEa6
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

class BilibiliChineseSubtitleTester:
    """专门获取B站中文字幕的测试类"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.load_cookies()
    
    def load_cookies(self):
        """从cookie文件加载登录凭证"""
        # 尝试从父目录找cookie文件
        cookie_file = Path(__file__).parent.parent / "ok-result" / "blibli-cookie.txt"
        
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
    
    def is_chinese_subtitle(self, lan: str, lan_doc: str) -> bool:
        """判断是否为中文字幕"""
        chinese_codes = ['ai-zh', 'zh-CN', 'zh-Hant', 'zh', 'zh-Hans']
        chinese_keywords = ['中文', '简体', '繁体', '中字', '汉语']
        
        # 检查语言代码
        if lan.lower() in [code.lower() for code in chinese_codes]:
            return True
        
        # 检查语言描述
        for keyword in chinese_keywords:
            if keyword in lan_doc:
                return True
        
        return False
    
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
    
    def test_chinese_subtitles(self, video_url: str) -> Dict:
        """获取B站视频的中文字幕"""
        print(f"🚀 获取B站视频中文字幕")
        print(f"🔗 视频URL: {video_url}")
        
        result = {
            "video_url": video_url,
            "success": False,
            "chinese_subtitles_found": 0,
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
            self.save_result("video_info", video_data)
            
            if video_data.get("code") != 0:
                result["errors"].append(f"视频信息API错误: {video_data.get('message')}")
                return result
            
            video_info = video_data["data"]
            print(f"🎬 视频标题: {video_info.get('title', 'Unknown')}")
            print(f"📊 视频时长: {video_info.get('duration', 'Unknown')} 秒")
            
            # 获取所有分页的CID
            pages = video_info.get("pages", [])
            print(f"📄 视频共有 {len(pages)} 个分页")
            
            total_chinese_subtitles = 0
            
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
                    # 🔥 关键修改：只处理中文字幕
                    chinese_subtitles = []
                    for subtitle in subtitles:
                        lan = subtitle.get('lan', 'unknown')
                        lan_doc = subtitle.get('lan_doc', '未知语言')
                        
                        if self.is_chinese_subtitle(lan, lan_doc):
                            chinese_subtitles.append(subtitle)
                            print(f"  ✅ 找到中文字幕: {lan_doc} ({lan})")
                        else:
                            print(f"  ⏭️ 跳过非中文字幕: {lan_doc} ({lan})")
                    
                    if not chinese_subtitles:
                        print(f"⚠️ 该分页未找到中文字幕")
                        continue
                    
                    # 处理中文字幕
                    for subtitle_idx, subtitle in enumerate(chinese_subtitles):
                        lan = subtitle.get('lan', 'unknown')
                        lan_doc = subtitle.get('lan_doc', '未知语言')
                        subtitle_url = subtitle.get('subtitle_url', '')
                        
                        print(f"  📄 处理中文字幕 {subtitle_idx+1}: {lan_doc} ({lan})")
                        print(f"      URL: {subtitle_url}")
                        
                        subtitle_detail = {
                            "page": page_idx + 1,
                            "page_title": page_title,
                            "cid": cid,
                            "lan": lan,
                            "lan_doc": lan_doc,
                            "subtitle_url": subtitle_url,
                            "downloaded": False,
                            "content_preview": "",
                            "subtitle_count": 0
                        }
                        
                        # Step 3: 下载中文字幕内容
                        if subtitle_url:
                            try:
                                print(f"      📥 下载中文字幕内容...")
                                
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
                                        subtitle_detail["subtitle_count"] = len(subtitle_data["body"])
                                        
                                        # 保存原始中文字幕内容
                                        self.save_subtitle_content(f"chinese_subtitle_raw_p{page_idx+1}_{lan}", subtitle_content, "json")
                                        
                                        # 转换为SRT格式
                                        srt_content = self.convert_to_srt(subtitle_data["body"])
                                        self.save_subtitle_content(f"chinese_subtitle_srt_p{page_idx+1}_{lan}", srt_content, "srt")
                                        
                                        total_chinese_subtitles += 1
                                        print(f"      ✅ 成功下载中文字幕内容")
                                        
                                        # 显示字幕统计信息
                                        print(f"      📊 中文字幕共 {subtitle_detail['subtitle_count']} 行")
                                        
                                        # 显示字幕预览
                                        preview_lines = srt_content.split('\n')[:8]
                                        print(f"      📖 字幕预览:\n{chr(10).join(['        ' + line for line in preview_lines])}")
                                        
                                    else:
                                        print(f"      ⚠️ 中文字幕内容为空")
                                else:
                                    print(f"      ❌ 下载失败: HTTP {subtitle_response.status_code}")
                            
                            except Exception as e:
                                print(f"      ❌ 下载中文字幕失败: {e}")
                        else:
                            print(f"      ⚠️ 中文字幕URL为空")
                        
                        result["subtitle_details"].append(subtitle_detail)
                else:
                    print(f"⚠️ 该分页未找到任何字幕")
            
            result["success"] = True
            result["chinese_subtitles_found"] = total_chinese_subtitles
            
            # 保存最终结果
            self.save_result("chinese_subtitle_result", result)
            
            return result
            
        except Exception as e:
            error_msg = f"处理错误: {e}"
            print(f"❌ {error_msg}")
            result["errors"].append(error_msg)
            return result

def main():
    """主函数"""
    print("🚀 获取B站视频中文字幕")
    print("=" * 60)
    
    tester = BilibiliChineseSubtitleTester()
    
    # 目标视频
    video_url = "https://www.bilibili.com/video/BV1sWobYuEa6"
    
    try:
        # 获取中文字幕
        result = tester.test_chinese_subtitles(video_url)
        
        print(f"\n📊 中文字幕获取结果:")
        print(f"   - 视频URL: {video_url}")
        print(f"   - 获取成功: {'是' if result['success'] else '否'}")
        print(f"   - 找到中文字幕: {result['chinese_subtitles_found']} 个")
        
        if result['subtitle_details']:
            print(f"   - 中文字幕详情:")
            for detail in result['subtitle_details']:
                status = "✅ 成功" if detail['downloaded'] else "❌ 失败"
                count = f" ({detail['subtitle_count']}行)" if detail.get('subtitle_count') else ""
                print(f"     * P{detail['page']} {detail['lan_doc']} ({detail['lan']}): {status}{count}")
                if detail.get('content_preview'):
                    print(f"       预览: {detail['content_preview'][:50]}...")
        
        if result.get('errors'):
            print(f"   - 错误信息: {'; '.join(result['errors'])}")
        
        if result['chinese_subtitles_found'] > 0:
            print(f"\n✅ 成功获取 {result['chinese_subtitles_found']} 个中文字幕！")
            print(f"📁 结果保存在: {OUTPUT_DIR}")
        else:
            print(f"\n⚠️ 未找到中文字幕")
        
        print(f"\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main() 