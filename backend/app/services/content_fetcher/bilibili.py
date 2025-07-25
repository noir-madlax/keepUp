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
from app.services.bilibili_short_url_service import BilibiliShortUrlService
from app.services.request_logger import RequestLogger, Steps

class BilibilitFetcher(ContentFetcher):
    """B站视频内容获取器"""
    
    def __init__(self):
        super().__init__()
        self.platform = "bilibili"
        self.short_url_service = BilibiliShortUrlService()
        # ✅ 移除实例变量，避免并发时的状态共享问题
    
    def can_handle(self, url: str) -> bool:
        """检查是否可以处理该URL"""
        return self.short_url_service.is_bilibili_url(url)
    
    async def load_cookies(self, request_id: int = 0) -> Optional[Dict[str, str]]:
        """从数据库加载B站cookie配置，返回headers而不是设置实例变量"""
        try:
            # 从keep_prompt表获取cookie配置
            cookie_prompt = await PromptRepository.get_prompt_by_type('cookie-bilbli')
            
            if not cookie_prompt:
                error_msg = "未找到B站cookie配置 (类型: cookie-bilbli)"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.BILIBILI_COOKIE_LOAD, error_msg, Exception(error_msg))
                return None
            
            # 解析cookie数据
            try:
                cookies_data = json.loads(cookie_prompt.content)
            except json.JSONDecodeError:
                error_msg = "B站cookie配置格式错误，无法解析JSON"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.BILIBILI_COOKIE_LOAD, error_msg, Exception(error_msg))
                return None
            
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
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': 'https://www.bilibili.com/',
                    'Cookie': f'SESSDATA={sessdata}; bili_jct={bili_jct}; buvid3={buvid3}; DedeUserID={dedeuserid}'
                }
                
                logger.info("✅ 成功加载B站cookie配置")
                return headers
            else:
                error_msg = "B站cookie配置不完整，缺少关键字段SESSDATA或bili_jct"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.BILIBILI_COOKIE_LOAD, error_msg, Exception(error_msg))
                return None
                
        except Exception as e:
            error_msg = f"加载B站cookie配置失败: {str(e)}"
            logger.error(error_msg)
            if request_id:
                await RequestLogger.error(request_id, Steps.BILIBILI_COOKIE_LOAD, error_msg, e)
            return None
    
    async def extract_bv_id(self, video_url: str, request_id: int = 0) -> str:
        """从URL中提取BV号，支持短链接"""
        # 如果是短链接，先解析为长链接
        if 'b23.tv' in video_url:
            resolved_url = await self.short_url_service.resolve_short_url(video_url)
            if resolved_url:
                video_url = resolved_url
            else:
                error_msg = f"无法解析B站短链接: {video_url}"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.BILIBILI_SHORT_URL_RESOLVE, error_msg, Exception(error_msg))
                return ""
        
        # 使用短链接服务提取视频ID
        video_id = self.short_url_service.extract_video_id(video_url)
        if not video_id and request_id:
            error_msg = f"无法从URL提取BV号: {video_url}"
            await RequestLogger.error(request_id, Steps.BILIBILI_BV_EXTRACT, error_msg, Exception(error_msg))
        return video_id or ""
    
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
        """判断字幕质量是否足够高"""
        if not subtitle_content or len(subtitle_content) < 100:
            return False
        
        # 检查音乐符号占比
        music_count = subtitle_content.count('♪')
        total_chars = len(subtitle_content)
        music_ratio = music_count / total_chars if total_chars > 0 else 0
        
        # 如果音乐符号占比超过10%，认为质量不够
        if music_ratio > 0.1:
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
    
    async def fetch(self, url: str, request: Optional[FetchRequest] = None) -> Optional[str]:
        """获取B站视频内容"""
        request_id = request.id if request else 0
        try:
            logger.info(f"🚀 开始获取B站视频内容: {url}")
            
            # 获取视频信息（已整合字幕获取逻辑）
            video_info = await self.get_video_info(url, request_id)
            if not video_info:
                error_msg = f"无法获取B站视频信息: {url}"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.VIDEO_INFO_FETCH, error_msg, Exception(error_msg))
                return None
            
            # 数据一致性检查
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
                f"字幕内容: {video_info.description}"
            ]
            
            content = "\n\n".join(content_parts)
            
            # 最终验证
            logger.info(f"🎯 最终内容组合完成:")
            for i, part in enumerate(content_parts, 1):
                logger.info(f"  第{i}部分长度: {len(part)}")
            
            logger.info(f"✅ 成功获取B站视频内容，总长度: {len(content)}")
            
            return content
            
        except Exception as e:
            error_msg = f"获取B站视频内容失败: {str(e)}"
            logger.error(error_msg)
            if request_id:
                await RequestLogger.error(request_id, Steps.CONTENT_FETCH, error_msg, e)
            return None
    
    async def get_video_info(self, url: str, request_id: int = 0) -> Optional[VideoInfo]:
        """获取B站视频基本信息和字幕"""
        try:
            # 使用新的cookie加载逻辑
            headers = await self.load_cookies(request_id)
            if not headers:
                error_msg = "无法加载B站cookie配置"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.BILIBILI_COOKIE_LOAD, error_msg, Exception(error_msg))
                return None
            
            bv_id = await self.extract_bv_id(url, request_id)
            if not bv_id:
                error_msg = f"无法提取BV号: {url}"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.BILIBILI_BV_EXTRACT, error_msg, Exception(error_msg))
                return None
            
            logger.info(f"📋 开始处理视频: BV={bv_id}, 原始URL={url}")
            
            # Step 1: 获取视频基本信息
            video_info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
            logger.info(f"📡 请求视频信息API: {video_info_url}")
            
            response = requests.get(video_info_url, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"获取B站视频信息失败: HTTP {response.status_code}, URL={video_info_url}"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.BILIBILI_VIDEO_API, error_msg, Exception(error_msg))
                return None
            
            video_data = response.json()
            if video_data.get("code") != 0:
                error_msg = f"B站视频API返回错误: {video_data.get('message')}, BV={bv_id}"
                logger.error(error_msg)
                if request_id:
                    await RequestLogger.error(request_id, Steps.BILIBILI_VIDEO_API, error_msg, Exception(error_msg))
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
            logger.info(f"🔢 BV号验证: 请求={bv_id}, API返回={video_info.get('bvid', 'N/A')}")
            
            # 严格验证BV号匹配，确保获取的是正确视频的信息
            returned_bv_id = video_info.get('bvid', '')
            if returned_bv_id and returned_bv_id != bv_id:
                logger.error(f"❌ BV号不匹配! 请求: {bv_id}, 返回: {returned_bv_id}")
                raise Exception(f"BV号验证失败: 请求{bv_id}但返回{returned_bv_id}")
            
            # Step 2: 获取字幕内容 - 参考test_bilibili_chinese_subtitles.py的逻辑
            subtitle_content = ""
            pages = video_info.get("pages", [])
            
            if pages:
                logger.info(f"📄 视频共有 {len(pages)} 个分页")
                
                # 只处理第一个分页
                first_page = pages[0]
                cid = first_page['cid']
                part_title = first_page.get('part', '默认分页')
                
                logger.info(f"🎯 处理分页1: {part_title} (CID: {cid})")
                
                # 获取播放器信息（包含字幕信息）- 与参考代码保持一致
                logger.info(f"📝 获取播放器信息和字幕列表...")
                player_url = f"https://api.bilibili.com/x/player/v2"
                player_params = {"bvid": bv_id, "cid": cid}
                
                player_response = requests.get(player_url, headers=headers, params=player_params)
                if player_response.status_code != 200:
                    error_msg = f"获取B站播放器信息失败: HTTP {player_response.status_code}, BV={bv_id}, CID={cid}"
                    logger.error(error_msg)
                    if request_id:
                        await RequestLogger.error(request_id, Steps.BILIBILI_PLAYER_API, error_msg, Exception(error_msg))
                    raise Exception(error_msg)
                
                player_data = player_response.json()
                if player_data.get("code") != 0:
                    error_msg = f"B站播放器API返回错误: {player_data.get('message')}, BV={bv_id}, CID={cid}"
                    logger.error(error_msg)
                    if request_id:
                        await RequestLogger.error(request_id, Steps.BILIBILI_PLAYER_API, error_msg, Exception(error_msg))
                    raise Exception(error_msg)
                
                # 检查字幕信息 - 完全按照参考代码的逻辑
                subtitle_info = player_data.get("data", {}).get("subtitle", {})
                subtitles = subtitle_info.get("subtitles", [])
                
                logger.info(f"🌐 找到 {len(subtitles)} 个字幕")
                
                if subtitles:
                    # 查找并下载中文字幕 - 按照参考代码的逻辑
                    chinese_subtitles = []
                    for subtitle in subtitles:
                        lan = subtitle.get('lan', 'unknown')
                        lan_doc = subtitle.get('lan_doc', '未知语言')
                        
                        if self.is_chinese_subtitle(lan, lan_doc):
                            chinese_subtitles.append(subtitle)
                            logger.info(f"  ✅ 找到中文字幕: {lan_doc} ({lan})")
                        else:
                            logger.info(f"  ⏭️ 跳过非中文字幕: {lan_doc} ({lan})")
                    
                    if chinese_subtitles:
                        # 使用第一个中文字幕
                        subtitle = chinese_subtitles[0]
                        lan = subtitle.get('lan', 'unknown')
                        lan_doc = subtitle.get('lan_doc', '未知语言')
                        subtitle_url = subtitle.get('subtitle_url', '')
                        
                        logger.info(f"📄 使用中文字幕: {lan_doc} ({lan})")
                        logger.info(f"🔗 字幕URL: {subtitle_url}")
                        
                        if subtitle_url:
                            try:
                                # 确保URL是完整的 - 与参考代码一致
                                if subtitle_url.startswith("//"):
                                    subtitle_url = "https:" + subtitle_url
                                elif not subtitle_url.startswith("http"):
                                    subtitle_url = "https://" + subtitle_url
                                
                                logger.info(f"📥 下载字幕内容...")
                                subtitle_response = requests.get(subtitle_url, headers=headers, timeout=10)
                                
                                if subtitle_response.status_code == 200:
                                    subtitle_data = json.loads(subtitle_response.text)
                                    logger.info(f"📄 字幕数据解析成功，keys: {list(subtitle_data.keys())}")
                                    
                                    if "body" in subtitle_data and subtitle_data["body"]:
                                        # 提取所有字幕文本 - 与参考代码逻辑一致
                                        subtitle_texts = []
                                        for item in subtitle_data["body"]:
                                            content = item.get("content", "").strip()
                                            if content:
                                                subtitle_texts.append(content)
                                        
                                        subtitle_content = " ".join(subtitle_texts)
                                        
                                        # 简单的质量检查 - 调整为更宽松的标准
                                        if len(subtitle_content) > 20:  # 降低基本长度要求
                                            logger.info(f"✅ 成功获取中文字幕: 共 {len(subtitle_data['body'])} 行，总字符数: {len(subtitle_content)}")
                                        else:
                                            logger.warning(f"⚠️ 字幕内容过短: {len(subtitle_content)} 字符，但仍然使用")
                                            # 即使内容较短也使用，因为可能是API返回的简化版本
                                    else:
                                        logger.warning(f"⚠️ 字幕数据格式异常: 缺少body字段或body为空")
                                else:
                                    error_msg = f"B站字幕下载失败: HTTP {subtitle_response.status_code}, URL={subtitle_url}, BV={bv_id}"
                                    logger.error(f"❌ {error_msg}")
                                    if request_id:
                                        await RequestLogger.error(request_id, Steps.BILIBILI_SUBTITLE_DOWNLOAD, error_msg, Exception(error_msg))
                            except Exception as e:
                                error_msg = f"处理B站字幕异常: {str(e)}, BV={bv_id}, URL={subtitle_url}"
                                logger.error(f"❌ {error_msg}")
                                if request_id:
                                    await RequestLogger.error(request_id, Steps.BILIBILI_SUBTITLE_DOWNLOAD, error_msg, e)
                        else:
                            logger.warning(f"⚠️ 字幕URL为空")
                    else:
                        logger.warning(f"⚠️ 未找到中文字幕")
                else:
                    logger.warning(f"⚠️ 该视频没有字幕")
                    
                # 如果没有获取到字幕内容，记录警告但不抛出异常
                if not subtitle_content:
                    logger.warning(f"⚠️ 未能获取到字幕内容 (BV={bv_id})，但不影响其他内容获取")
            else:
                logger.error(f"❌ 视频没有分页信息 (BV={bv_id})")
                raise Exception(f"视频没有可用的分页信息: {bv_id}")
            
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
            
            # 返回VideoInfo，确保数据一致性
            logger.info(f"📦 构建VideoInfo完成: 标题长度={len(title)}, 字幕长度={len(subtitle_content)}")
            
            return VideoInfo(
                title=title,
                description=subtitle_content,  # 字幕内容作为描述
                author=author,
                article=article
            )
            
        except Exception as e:
            error_msg = f"获取B站视频信息失败 (URL={url}): {str(e)}"
            logger.error(error_msg)
            if request_id:
                await RequestLogger.error(request_id, Steps.VIDEO_INFO_FETCH, error_msg, e)
            return None
    
    async def get_chapters(self, url: str) -> Optional[str]:
        """获取视频章节信息 - B站暂不支持"""
        return None
    
    async def get_author_info(self, url: str) -> Optional[AuthorInfo]:
        """获取作者信息"""
        try:
            video_info = await self.get_video_info(url, 0)  # 没有request_id时使用0
            if video_info and video_info.author:
                return AuthorInfo(
                    name=video_info.author.get('name', '未知作者'),
                    icon=video_info.author.get('icon', ''),
                    platform='bilibili'
                )
        except Exception as e:
            logger.error(f"获取B站作者信息失败: {str(e)}")
            
        return None 