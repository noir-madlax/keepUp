"""
私密内容处理服务
处理私密音频/文字上传、ASR转写、AI总结等功能
"""
import os
import json
import re
import secrets
import string
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from app.config import settings
from app.utils.logger import logger
from app.repositories.supabase import SupabaseService
from app.repositories.prompt_repository import PromptRepository
from app.services.transcript.tencent_asr import TencentASRClient
from app.services.openrouter_service import OpenRouterService
from app.repositories.llm_records_repository import LLMRecordsRepository


class PrivateContentService:
    """私密内容处理服务"""
    
    # 支持的音频格式
    SUPPORTED_AUDIO_FORMATS = ['mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac']
    
    # 最大文件大小 100MB
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    # Prompt 类型映射
    PROMPT_TYPE_MAP = {
        'general': 'private_general',
        'parent': 'private_parent', 
        'customer': 'private_customer'
    }

    @staticmethod
    def generate_private_slug(length: int = 16) -> str:
        """生成私密内容的随机访问链接
        
        Args:
            length: slug 长度，默认16位
            
        Returns:
            str: 随机生成的 slug
        """
        # 使用字母和数字生成随机字符串
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_audio_file(filename: str, file_size: int) -> Tuple[bool, str]:
        """验证音频文件
        
        Args:
            filename: 文件名
            file_size: 文件大小（字节）
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        # 检查文件扩展名
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if ext not in PrivateContentService.SUPPORTED_AUDIO_FORMATS:
            return False, f"不支持的音频格式: {ext}，支持的格式: {', '.join(PrivateContentService.SUPPORTED_AUDIO_FORMATS)}"
        
        # 检查文件大小
        if file_size > PrivateContentService.MAX_FILE_SIZE:
            max_mb = PrivateContentService.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"文件大小超过限制，最大支持 {max_mb}MB"
        
        return True, ""
    
    @staticmethod
    async def upload_audio_to_storage(
        file_content: bytes,
        filename: str,
        user_id: str
    ) -> Optional[str]:
        """上传音频文件到 Supabase Storage
        
        Args:
            file_content: 文件内容
            filename: 文件名
            user_id: 用户ID
            
        Returns:
            Optional[str]: 文件的公开访问URL，失败返回None
        """
        try:
            client = SupabaseService.get_client()
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = filename.split('.')[-1].lower() if '.' in filename else 'mp3'
            storage_filename = f"private_audio/{user_id}/{timestamp}_{secrets.token_hex(4)}.{ext}"
            
            # 上传到 Storage
            result = client.storage.from_('private-uploads').upload(
                storage_filename,
                file_content,
                file_options={"content-type": f"audio/{ext}"}
            )
            
            if result:
                # 获取公开URL
                public_url = client.storage.from_('private-uploads').get_public_url(storage_filename)
                logger.info(f"音频文件上传成功: {storage_filename}")
                return public_url
            
            return None
            
        except Exception as e:
            logger.error(f"上传音频文件失败: {str(e)}")
            return None
    
    @staticmethod
    async def transcribe_audio(audio_url: str) -> Optional[str]:
        """使用腾讯ASR转写音频
        
        Args:
            audio_url: 音频文件URL
            
        Returns:
            Optional[str]: 转写后的文字内容
        """
        try:
            asr_client = TencentASRClient()
            
            # 创建ASR任务
            logger.info(f"创建腾讯ASR任务: {audio_url}")
            task_id = asr_client.create_task(audio_url)
            logger.info(f"ASR任务创建成功: task_id={task_id}")
            
            # 轮询获取结果
            result = asr_client.poll_result(task_id)
            
            # 转换为带时间戳的文本格式
            transcript = asr_client.to_bracketed_transcript(result)
            
            if transcript:
                logger.info(f"ASR转写成功，文本长度: {len(transcript)}")
                return transcript
            
            logger.warning("ASR转写结果为空")
            return None
            
        except Exception as e:
            logger.error(f"ASR转写失败: {str(e)}")
            return None
    
    @staticmethod
    async def get_private_prompt(prompt_type: str) -> Optional[str]:
        """获取私密内容的Prompt模版
        
        Args:
            prompt_type: prompt类型 (general/parent/customer)
            
        Returns:
            Optional[str]: prompt内容
        """
        try:
            db_type = PrivateContentService.PROMPT_TYPE_MAP.get(prompt_type, 'private_general')
            prompt = await PromptRepository.get_prompt_by_type(db_type)
            if prompt:
                return prompt.content
            logger.warning(f"未找到prompt类型: {db_type}")
            return None
        except Exception as e:
            logger.error(f"获取prompt失败: {str(e)}")
            return None
    
    @staticmethod
    def extract_title_from_markdown(markdown_content: str) -> Optional[str]:
        """从Markdown内容中提取标题
        
        从第一行的 # 标题 中提取标题文本
        
        Args:
            markdown_content: Markdown格式的内容
            
        Returns:
            Optional[str]: 提取的标题
        """
        try:
            lines = markdown_content.strip().split('\n')
            for line in lines:
                line = line.strip()
                # 匹配 # 开头的标题
                if line.startswith('# '):
                    title = line[2:].strip()
                    # 清理标题中可能的特殊字符
                    title = title.strip('"\'「」【】')
                    if title and len(title) <= 50:
                        logger.info(f"从Markdown提取标题成功: {title}")
                        return title
                # 跳过空行继续查找
                elif line:
                    # 如果第一个非空行不是标题，尝试继续找
                    continue
            return None
        except Exception as e:
            logger.warning(f"从Markdown提取标题失败: {str(e)}")
            return None
    
    @staticmethod
    def remove_title_from_markdown(markdown_content: str) -> str:
        """从Markdown内容中移除第一个标题行
        
        因为标题会单独存储在 article.title 中，内容部分不需要重复
        
        Args:
            markdown_content: Markdown格式的内容
            
        Returns:
            str: 移除标题后的内容
        """
        try:
            lines = markdown_content.strip().split('\n')
            result_lines = []
            title_removed = False
            
            for line in lines:
                stripped = line.strip()
                # 只移除第一个 # 开头的标题
                if not title_removed and stripped.startswith('# '):
                    title_removed = True
                    continue
                result_lines.append(line)
            
            return '\n'.join(result_lines).strip()
        except Exception as e:
            logger.warning(f"移除Markdown标题失败: {str(e)}")
            return markdown_content
    
    @staticmethod
    async def summarize_content(
        content: str,
        prompt_type: str,
        request_id: int,
        article_id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """使用Bedrock总结内容
        
        Args:
            content: 需要总结的内容
            prompt_type: prompt类型
            request_id: 请求ID
            article_id: 文章ID
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (总结结果Markdown, 从Markdown提取的标题)
        """
        try:
            # 获取prompt
            prompt = await PrivateContentService.get_private_prompt(prompt_type)
            if not prompt:
                raise Exception(f"未找到prompt模版: {prompt_type}")
            
            # 调用Bedrock API
            api_response = await OpenRouterService.call_bedrock_api(
                prompt=prompt,
                content=content,
                request_id=request_id,
                lang='zh'
            )
            
            if not api_response:
                raise Exception("Bedrock API调用失败")
            
            # 提取总结内容（Markdown格式）
            raw_content = api_response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if raw_content:
                # 从Markdown中提取标题（第一个 # 开头的行）
                extracted_title = PrivateContentService.extract_title_from_markdown(raw_content)
                
                # 移除标题行，因为标题会单独存储
                markdown_content = PrivateContentService.remove_title_from_markdown(raw_content)
                
                # 保存总结结果（Markdown格式，不含标题）
                await SupabaseService.create_article_sections(article_id, [
                    {
                        'article_id': article_id,
                        'content': markdown_content,
                        'language': 'zh',
                        'section_type': '总结'
                    }
                ])
                logger.info(f"私密内容总结成功: article_id={article_id}, title={extracted_title}")
                return markdown_content, extracted_title
            
            return None, None
            
        except Exception as e:
            logger.error(f"内容总结失败: {str(e)}")
            return None, None
    
    @staticmethod
    async def create_private_article(
        title: str,
        content: str,
        user_id: str,
        original_content: str = None,
        prompt_type: str = 'general'
    ) -> Optional[Dict[str, Any]]:
        """创建私密文章
        
        Args:
            title: 文章标题
            content: 文章内容（总结后的）
            user_id: 用户ID
            original_content: 原始内容（音频转写或用户输入）
            prompt_type: prompt类型，用于确定显示的图标
            
        Returns:
            Optional[Dict]: 创建的文章记录
        """
        try:
            client = SupabaseService.get_client()
            
            # 生成私密链接slug
            private_slug = PrivateContentService.generate_private_slug()
            
            # 根据 prompt_type 设置 channel（用于前端显示对应图标）
            channel_map = {
                'general': 'private_general',
                'parent': 'private_parent',
                'customer': 'private_customer'
            }
            channel = channel_map.get(prompt_type, 'private_general')
            
            # 创建文章记录
            article_data = {
                'title': title or '私密会议纪要',
                'content': original_content or '',
                'channel': channel,
                'is_private': True,
                'private_slug': private_slug,
                'user_id': user_id,
                'is_visible': True,
                'tags': ['私密', '会议纪要']
            }
            
            result = client.table('keep_articles').insert(article_data).execute()
            
            if result.data:
                article = result.data[0]
                logger.info(f"私密文章创建成功: id={article['id']}, slug={private_slug}, channel={channel}")
                return article
            
            return None
            
        except Exception as e:
            logger.error(f"创建私密文章失败: {str(e)}")
            return None
    
    @staticmethod
    async def create_private_request(
        user_id: str,
        input_type: str,
        prompt_type: str,
        title: str = None,
        original_url: str = None
    ) -> Optional[Dict[str, Any]]:
        """创建私密内容处理请求
        
        Args:
            user_id: 用户ID
            input_type: 输入类型 (audio/text)
            prompt_type: prompt类型
            title: 标题
            original_url: 原始URL（文件URL或空）
            
        Returns:
            Optional[Dict]: 创建的请求记录
        """
        try:
            request_data = {
                'original_url': original_url or f'private://{input_type}',
                'platform': 'private',
                'status': 'pending',
                'user_id': user_id
            }
            
            result = await SupabaseService.create_article_request(request_data)
            return result
            
        except Exception as e:
            logger.error(f"创建私密请求失败: {str(e)}")
            return None
    
    @staticmethod
    async def process_private_content(
        request_id: int,
        user_id: str,
        input_type: str,
        prompt_type: str,
        title: str,
        content: str = None,
        audio_url: str = None
    ) -> Optional[Dict[str, Any]]:
        """处理私密内容的完整流程
        
        Args:
            request_id: 请求ID
            user_id: 用户ID
            input_type: 输入类型 (audio/text)
            prompt_type: prompt类型
            title: 标题（为空时AI自动生成）
            content: 文字内容（text类型时）
            audio_url: 音频URL（audio类型时）
            
        Returns:
            Optional[Dict]: 处理结果
        """
        try:
            # 更新状态为处理中
            await SupabaseService.update_status(request_id, 'processing')
            
            # 获取原始内容
            original_content = content
            
            # 如果是音频，先进行ASR转写
            if input_type == 'audio' and audio_url:
                logger.info(f"开始ASR转写: {audio_url}")
                original_content = await PrivateContentService.transcribe_audio(audio_url)
                if not original_content:
                    await SupabaseService.update_status(request_id, 'failed', '音频转写失败')
                    return None
                
                # 保存转写内容到请求记录
                await SupabaseService.update_content(request_id, original_content)
            
            # 先用临时标题创建文章（标题后面会根据LLM生成结果更新）
            temp_title = title if title and title.strip() else '处理中...'
            
            # 创建私密文章，同时记录 prompt_type 用于显示对应图标
            article = await PrivateContentService.create_private_article(
                title=temp_title,
                content='',
                user_id=user_id,
                original_content=original_content,
                prompt_type=prompt_type
            )
            
            if not article:
                await SupabaseService.update_status(request_id, 'failed', '创建文章失败')
                return None
            
            article_id = article['id']
            
            # 更新请求记录的文章ID
            await SupabaseService.update_article_id(request_id, article_id)
            
            # 使用Bedrock总结内容（同时生成标题）
            summary, extracted_title = await PrivateContentService.summarize_content(
                content=original_content,
                prompt_type=prompt_type,
                request_id=request_id,
                article_id=article_id
            )
            
            if not summary:
                await SupabaseService.update_status(request_id, 'failed', '内容总结失败')
                return None
            
            # 确定最终标题：用户输入 > LLM提取 > 默认
            final_title = title.strip() if title and title.strip() else None
            if not final_title and extracted_title:
                final_title = extracted_title
            if not final_title:
                final_title = '私密会议纪要'
            
            # 更新文章标题
            client = SupabaseService.get_client()
            client.table('keep_articles').update({'title': final_title}).eq('id', article_id).execute()
            logger.info(f"更新文章标题: article_id={article_id}, title={final_title}")
            
            # 更新状态为已完成
            await SupabaseService.update_status(request_id, 'processed')
            
            return {
                'article_id': article_id,
                'private_slug': article['private_slug'],
                'title': final_title,
                'summary_length': len(summary)
            }
            
        except Exception as e:
            logger.error(f"处理私密内容失败: {str(e)}")
            await SupabaseService.update_status(request_id, 'failed', str(e))
            return None
