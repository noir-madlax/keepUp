"""
B站视频内容获取器
结合cookie管理、视频信息获取和中文字幕下载功能
"""

import json
import requests
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import unquote

from .base import ContentFetcher, VideoInfo
from app.repositories.prompt_repository import PromptRepository
from app.utils.decorators import retry_decorator
from app.models.request import FetchRequest
from app.models.author import AuthorInfo
from app.models.article import ArticleCreate
from app.utils.logger import logger

class BilibilitFetcher(ContentFetcher):
    """B站视频内容获取器"""
    
    def __init__(self):
        super().__init__()
        self.platform = "bilibili"
        self.headers = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def can_handle(self, url: str) -> bool:
        """检查是否可以处理该URL"""
        bilibili_domains = ['bilibili.com', 'b23.tv']
        return any(domain in url for domain in bilibili_domains)
    
    async def load_cookies(self) -> bool:
        """从数据库加载B站cookie配置"""
        try:
            # 从keep_prompt表获取cookie配置
            cookie_prompt = await PromptRepository.get_prompt_by_type('cookie-bilbli')
            
            if not cookie_prompt:
                logger.error("未找到B站cookie配置 (类型: cookie-bilbli)")
                return False
            
            # 解析cookie数据
            try:
                cookies_data = json.loads(cookie_prompt.content)
            except json.JSONDecodeError:
                logger.error("B站cookie配置格式错误，无法解析JSON")
                return False
            
            # 提取关键cookie信息
            sessdata = None
            bili_jct = None
            buvid3 = None
            dedeuserid = None
            
            for cookie in cookies_data:
                if cookie.get('name') == 'SESSDATA':
                    sessdata = unquote(cookie.get('value', ''))
                elif cookie.get('name') == 'bili_jct':
                    bili_jct = cookie.get('value', '')
                elif cookie.get('name') == 'buvid3':
                    buvid3 = cookie.get('value', '')
                elif cookie.get('name') == 'DedeUserID':
                    dedeuserid = cookie.get('value', '')
            
            # 构建请求头
            if sessdata and bili_jct:
                self.headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': 'https://www.bilibili.com/',
                    'Cookie': f'SESSDATA={sessdata}; bili_jct={bili_jct}; buvid3={buvid3}; DedeUserID={dedeuserid}'
                }
                
                logger.info("✅ 成功加载B站cookie配置")
                return True
            else:
                logger.error("B站cookie配置不完整，缺少关键字段")
                return False
                
        except Exception as e:
            logger.error(f"加载B站cookie配置失败: {str(e)}")
            return False
    
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
    
    def is_high_quality_subtitle(self, subtitle_content: str) -> bool:
        """判断字幕是否为高质量（有实际对话内容）"""
        if not subtitle_content or len(subtitle_content.strip()) == 0:
            return False
        
        # 计算音乐符号占比
        music_count = subtitle_content.count('♪')
        total_chars = len(subtitle_content.strip())
        
        # 如果总字符数太少，认为是低质量
        if total_chars < 200:
            return False
        
        # 如果音乐符号占比过高，认为是低质量
        if music_count > 0:
            music_ratio = music_count / total_chars
            if music_ratio > 0.1:  # 音乐符号占比超过10%
                return False
        
        # 检查是否主要是音乐标记
        music_phrases = ['音乐', '♪', '♫', '♬', '♩']
        music_char_count = sum(subtitle_content.count(phrase) for phrase in music_phrases)
        if music_char_count > total_chars * 0.3:  # 音乐相关字符超过30%
            return False
        
        return True
    
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
    
    async def get_subtitle_with_retry(self, bv_id: str, cid: str, max_retries: int = 5, retry_delay: int = 20) -> str:
        """
        获取高质量字幕，支持重试机制
        
        Args:
            bv_id: B站视频BV号
            cid: 视频分页ID
            max_retries: 最大重试次数，默认5次
            retry_delay: 重试间隔秒数，默认20秒
            
        Returns:
            str: 高质量的字幕内容
            
        Raises:
            Exception: 如果重试次数用完仍未获取到高质量字幕
        """
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 第 {attempt}/{max_retries} 次尝试获取高质量字幕")
            
            try:
                # 获取播放器信息和字幕
                player_url = f"https://api.bilibili.com/x/player/v2"
                player_params = {"bvid": bv_id, "cid": cid}
                
                player_response = requests.get(player_url, headers=self.headers, params=player_params)
                if player_response.status_code == 200:
                    player_data = player_response.json()
                    if player_data.get("code") == 0:
                        subtitle_info = player_data.get("data", {}).get("subtitle", {})
                        subtitles = subtitle_info.get("subtitles", [])
                        
                        logger.info(f"  🌐 找到 {len(subtitles)} 个字幕")
                        
                        # 查找并下载中文字幕
                        for subtitle in subtitles:
                            lan = subtitle.get('lan', 'unknown')
                            lan_doc = subtitle.get('lan_doc', '未知语言')
                            
                            if self.is_chinese_subtitle(lan, lan_doc):
                                subtitle_url = subtitle.get('subtitle_url', '')
                                logger.info(f"  ✅ 找到中文字幕: {lan_doc} ({lan})")
                                
                                if subtitle_url:
                                    # 确保URL是完整的
                                    if subtitle_url.startswith("//"):
                                        subtitle_url = "https:" + subtitle_url
                                    elif not subtitle_url.startswith("http"):
                                        subtitle_url = "https://" + subtitle_url
                                    
                                    logger.info(f"  🔗 字幕URL: {subtitle_url}")
                                    
                                    try:
                                        # 下载字幕内容
                                        subtitle_response = requests.get(subtitle_url, headers=self.headers, timeout=10)
                                        logger.info(f"  📡 字幕请求状态码: {subtitle_response.status_code}")
                                        
                                        if subtitle_response.status_code == 200:
                                            try:
                                                subtitle_data = json.loads(subtitle_response.text)
                                                logger.info(f"  📄 字幕数据解析成功，keys: {list(subtitle_data.keys())}")
                                                
                                                if "body" in subtitle_data and subtitle_data["body"]:
                                                    # 提取所有字幕文本
                                                    subtitle_texts = []
                                                    for item in subtitle_data["body"]:
                                                        content = item.get("content", "").strip()
                                                        if content:
                                                            subtitle_texts.append(content)
                                                    
                                                    subtitle_content = " ".join(subtitle_texts)
                                                    
                                                    # 检查字幕质量
                                                    if self.is_high_quality_subtitle(subtitle_content):
                                                        logger.info(f"  ✅ 成功获取高质量字幕，共 {len(subtitle_data['body'])} 行，总字符数: {len(subtitle_content)}")
                                                        return subtitle_content
                                                    else:
                                                        # 计算质量指标用于日志
                                                        music_count = subtitle_content.count('♪')
                                                        total_chars = len(subtitle_content)
                                                        logger.warning(f"  ⚠️ 字幕质量不佳: 总字符数 {total_chars}，音乐符号 {music_count} 个")
                                                        
                                                        if attempt < max_retries:
                                                            logger.info(f"  ⏳ 等待 {retry_delay} 秒后重试...")
                                                            await asyncio.sleep(retry_delay)
                                                            break  # 跳出字幕循环，开始下一次重试
                                                        else:
                                                            raise Exception(f"重试 {max_retries} 次后仍未获取到高质量字幕，最后一次字幕长度: {total_chars}，音乐符号: {music_count}")
                                                else:
                                                    logger.warning(f"  ⚠️ 字幕数据格式异常: 缺少body字段或body为空")
                                            except json.JSONDecodeError as e:
                                                logger.error(f"  ❌ 字幕JSON解析失败: {str(e)}")
                                        else:
                                            logger.error(f"  ❌ 字幕下载失败: HTTP {subtitle_response.status_code}")
                                    except requests.exceptions.RequestException as e:
                                        logger.error(f"  ❌ 字幕请求异常: {str(e)}")
                                    except Exception as e:
                                        logger.error(f"  ❌ 字幕处理异常: {str(e)}")
                                else:
                                    logger.warning(f"  ⚠️ 字幕URL为空")
                    else:
                        logger.error(f"播放器API返回错误: {player_data.get('message')}")
                else:
                    logger.error(f"获取播放器信息失败: HTTP {player_response.status_code}")
                    
            except Exception as e:
                logger.error(f"第 {attempt} 次尝试失败: {str(e)}")
                if attempt < max_retries:
                    logger.info(f"⏳ 等待 {retry_delay} 秒后重试...")
                    await asyncio.sleep(retry_delay)
                else:
                    raise Exception(f"重试 {max_retries} 次后仍未获取到字幕: {str(e)}")
        
        # 如果所有重试都失败了
        raise Exception(f"经过 {max_retries} 次重试，仍未获取到高质量字幕内容")
    
    async def fetch(self, url: str, request: Optional[FetchRequest] = None) -> Optional[str]:
        """获取B站视频内容"""
        try:
            logger.info(f"开始获取B站视频内容: {url}")
            
            # 获取视频信息（复用已有的get_video_info方法）
            video_info = await self.get_video_info(url)
            if not video_info:
                logger.error("无法获取B站视频信息")
                return None
            
            # 调试信息
            logger.info(f"🔍 视频信息获取成功:")
            logger.info(f"  - 标题: {video_info.title}")
            logger.info(f"  - 作者: {video_info.author.get('name', '未知作者')}")
            logger.info(f"  - 视频简介长度: {len(video_info.article.content) if video_info.article and video_info.article.content else 0}")
            logger.info(f"  - 字幕内容长度: {len(video_info.description) if video_info.description else 0}")
            
            # 组合内容
            content_parts = [
                f"标题: {video_info.title}",
                f"作者: {video_info.author.get('name', '未知作者')}",
                f"描述: {video_info.article.content if video_info.article else ''}",
            ]
            
            # 如果有字幕内容在description中
            if video_info.description:
                logger.info(f"✅ 添加字幕内容到最终内容中")
                content_parts.append(f"字幕内容: {video_info.description}")
            else:
                logger.warning(f"⚠️ 没有字幕内容可添加")
            
            content = "\n\n".join(content_parts)
            logger.info(f"🎯 最终内容组合完成:")
            for i, part in enumerate(content_parts, 1):
                logger.info(f"  第{i}部分长度: {len(part)}")
            
            logger.info(f"成功获取B站视频内容，长度: {len(content)}")
            
            return content
            
        except Exception as e:
            logger.error(f"获取B站视频内容失败: {str(e)}")
            return None
    
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """获取B站视频基本信息和字幕"""
        try:
            # 加载cookie配置
            if not await self.load_cookies():
                logger.error("无法加载cookie配置")
                return None
            
            bv_id = self.extract_bv_id(url)
            if not bv_id:
                logger.error("无法提取BV号")
                return None
            
            logger.info(f"📋 提取到BV号: {bv_id}")
            
            # Step 1: 获取视频基本信息
            video_info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
            response = requests.get(video_info_url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"获取视频信息失败: HTTP {response.status_code}")
                return None
            
            video_data = response.json()
            if video_data.get("code") != 0:
                logger.error(f"视频API返回错误: {video_data.get('message')}")
                return None
            
            video_info = video_data["data"]
            
            # 提取基本信息
            title = video_info.get('title', '未知标题')
            desc = video_info.get('desc', '')
            duration = video_info.get('duration', 0)
            pic = video_info.get('pic', '')
            pubdate = video_info.get('pubdate', 0)
            publish_date = datetime.fromtimestamp(pubdate) if pubdate else None
            
            # 提取作者信息
            owner = video_info.get('owner', {})
            author_name = owner.get('name', '未知作者')
            author_face = owner.get('face', '')
            author_mid = owner.get('mid', '')
            
            logger.info(f"🎬 视频标题: {title}")
            logger.info(f"👤 作者: {author_name}")
            
            # Step 2: 获取高质量字幕内容（支持重试）
            subtitle_content = ""
            pages = video_info.get("pages", [])
            
            if pages:
                # 只处理第一个分页
                first_page = pages[0]
                cid = first_page['cid']
                
                try:
                    # 使用重试机制获取高质量字幕
                    subtitle_content = await self.get_subtitle_with_retry(bv_id, cid)
                    logger.info(f"🎉 成功获取高质量字幕，字符数: {len(subtitle_content)}")
                except Exception as e:
                    logger.error(f"💥 获取高质量字幕失败: {str(e)}")
                    # 根据用户要求，如果获取不到高质量字幕就直接报错中断
                    raise Exception(f"无法获取该视频的高质量字幕内容: {str(e)}")
            
            # 构建作者信息 - 确保头像URL有效
            author = {
                'name': author_name,
                'icon': author_face if author_face and author_face.startswith('http') else '',
                'channel_id': str(author_mid),
                'platform': 'bilibili'
            }
            
            # 构建ArticleCreate对象 - 确保封面图片URL有效
            cover_url = pic if pic and pic.startswith('http') else ''
            
            article = ArticleCreate(
                title=title,
                content=desc,  # 使用视频简介作为初始内容
                channel="bilibili",
                tags=["视频", "bilibili"],
                original_link=url,
                publish_date=publish_date,
                cover_image_url=cover_url
            )
            
            # 返回VideoInfo，将字幕内容放在description中
            return VideoInfo(
                title=title,
                description=subtitle_content,  # 字幕内容作为描述
                author=author,
                article=article
            )
            
        except Exception as e:
            logger.error(f"获取B站视频信息失败: {str(e)}")
            return None
    
    async def get_chapters(self, url: str) -> Optional[str]:
        """获取视频章节信息 - B站暂不支持"""
        return None
    
    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取作者信息"""
        try:
            video_info = await self.get_video_info(url)
            if video_info and video_info.author:
                return AuthorInfo(
                    name=video_info.author.get('name', '未知作者'),
                    icon=video_info.author.get('icon', ''),
                    platform='bilibili'
                )
        except Exception as e:
            logger.error(f"获取B站作者信息失败: {str(e)}")
            
        return None 