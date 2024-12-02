from typing import List
import json
import re
from app.utils.logger import logger
from app.services.coze import CozeService
from app.services.supabase import SupabaseService
from app.config import settings

class ContentDetailerService:
    """分段详述服务"""
    
    @classmethod
    async def process_article_content(
        cls,
        article_id: int,
        chapters: str,
        language: str,
        workflow_id: str
    ) -> None:
        """处理文章内容的完整流程
        
        Args:
            article_id: 文章ID
            chapters: 章节信息
            language: 语言类型
            workflow_id: Coze 工作流 ID
        """
        try:
            logger.info(f"开始处理分段详述: article_id={article_id}, language={language}")
            
            # 1. 获取对应的请求ID
            request_id = await SupabaseService.get_request_id_by_article_id(article_id)

            # 2. 获取原文字幕内容
            subtitle_content = await cls.get_subtitle_content(article_id)
            
            # 3. 按章节拆分内容
            batches = cls.split_captions_to_batches(subtitle_content, chapters)
            logger.info(f"内容已拆分为 {len(batches)} 个批次")
            
            # 4. 调用 Coze 接口一次性处理所有批次
            coze_result = await cls.process_content(
                batches,
                language,
                workflow_id
            )
            
            # 5. 保存 Coze 返回结果到请求表
            await SupabaseService.update_detailed_content(
                request_id=request_id,
                detailed_content=coze_result,
                language=language
            )
            logger.info(f"已保存分段详述结果到请求表: request_id={request_id}")
            
            # 6. 解析处理后的内容
            result_data = json.loads(coze_result['data'])
            detailed_content = await cls.parse_detailed_content(
                result_data['seg_header']
            )
            
            # 7. 保存处理后的内容到小节
            await cls.save_detailed_content(
                article_id,
                detailed_content,
                language
            )
            
            logger.info(f"文章分段详述处理完成: article_id={article_id}, language={language}")
            
        except Exception as e:
            logger.error(f"处理文章分段详述失败: {str(e)}", exc_info=True)
            raise
            
    @staticmethod
    async def process_content(content: str, language: str, workflow_id: str) -> dict:
        """调用 Coze API 处理内容
        
        Args:
            content: 待处理的内容
            language: 语言类型
            workflow_id: Coze 工作流 ID
            
        Returns:
            dict: Coze API 的响应结果
        """
        try:
            logger.info(f"开始调用 Coze API 处理分段详述: language={language}")
            
            # 调用 Coze API
            coze_result = await CozeService.process_detailed_content(
                content=content,
                workflow_id=workflow_id
            )
            
            logger.info(f"Coze API 处理完成: token_cost={coze_result.get('cost', 'unknown')}")
            return coze_result
            
        except Exception as e:
            logger.error(f"调用 Coze API 处理分段详述失败: {str(e)}", exc_info=True)
            raise
            
    @staticmethod
    async def parse_detailed_content(
        seg_headers: List[str]
    ) -> str:
        """解析分段详述内容
        
        Args:
            seg_headers: 段落标题数组
            
        Returns:
            str: 解析并格式化后的内容
        """
        try:
            logger.info(f"开始解析分段详述内容: {len(seg_headers)} 个段落")
            
            # 初始化结果字符串
            result = []
            
            # 处理所有段落标题
            for header in seg_headers:
                result.append(header.strip())
            
            # 合并所有内容
            final_content = "\n".join(result)
            logger.info(f"内容解析完成，最终长度: {len(final_content)}")
            
            return final_content
            
        except Exception as e:
            logger.error(f"解析分段详述内容失败: {str(e)}")
            raise
            
    @staticmethod
    async def save_detailed_content(
        article_id: int,
        detailed_content: str,
        language: str
    ) -> None:
        """保存分段详述内容
        
        Args:
            article_id: 文章ID
            detailed_content: 分段详述内容
            language: 语言类型
        """
        try:
            logger.info(f"开始保存分段详述内容: article_id={article_id}, language={language}")
            
            # 准备小节数据
            section_data = {
                "article_id": article_id,
                "section_type": "分段详述",
                "content": detailed_content,
                "language": language,
                "sort_order": 700  # 在总结和字幕之后显示
            }
            
            # 先删除已存在的同类型同语言的小节
            await SupabaseService.delete_article_section(
                article_id=article_id,
                section_type="分段详述",
                language=language
            )
            
            # 创建新的小节
            await SupabaseService.create_article_sections(article_id, [section_data])
            
            logger.info(f"分段详述内容保存完成: article_id={article_id}, language={language}")
            
        except Exception as e:
            logger.error(f"保存分段详述内容失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> int:
        """将时间戳字符串转换为秒数
        
        Args:
            timestamp_str: 格式为 "HH:MM:SS" 或 "MM:SS" 的时间戳字符串
            
        Returns:
            int: 转换后的秒数
        """
        try:
            # 处理 HH:MM:SS 格式
            if len(timestamp_str.split(':')) == 3:
                hours, minutes, seconds = map(int, timestamp_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds
            # 处理 MM:SS 格式
            else:
                minutes, seconds = map(int, timestamp_str.split(':'))
                return minutes * 60 + seconds
        except Exception as e:
            logger.error(f"时间戳转换失败: {str(e)}")
            raise
    
    @staticmethod
    def extract_timestamps_and_titles(chapters: str) -> List[dict]:
        """从章节信息中提取时间戳和标题
        
        Args:
            chapters: 章节信息文本
            
        Returns:
            List[dict]: 包含段落信息的字典列表
        """
        try:
            # 提取时间戳和标题的正则表达式
            pattern = r'\[(\d{1,2}:\d{2}:\d{2})\] (.*?)(?=\[\d{1,2}:\d{2}:\d{2}\]|$)'
            
            # 提取所有匹配
            segments = re.findall(pattern, chapters, re.DOTALL)
            
            # 存储结果的列表
            results = []
            
            # 处理结果
            for i, (timestamp, title) in enumerate(segments):
                # 计算下一个时间戳（如果有）
                end_time = segments[i + 1][0] if i < len(segments) - 1 else "23:59:59"
                
                segment_info = {
                    'segment_number': i + 1,
                    'start_time': timestamp,
                    'end_time': end_time,
                    'title': title.strip()
                }
                results.append(segment_info)
            
            return results
            
        except Exception as e:
            logger.error(f"提取时间戳和标题失败: {str(e)}")
            raise
    
    @staticmethod
    def split_captions_to_batches(content: str, chapters: str) -> List[str]:
        """将字幕内容按章节信息分段
        
        Args:
            content: 原始字幕内容
            chapters: 章节信息
            
        Returns:
            List[str]: 按段落分割的内容数组
        """
        try:
            # 1. 提取段落信息
            segments = ContentDetailerService.extract_timestamps_and_titles(chapters)
            logger.info(f"提取到 {len(segments)} 个段落")
            
            # 2. 使用正则表达式匹配对话内容
            content_pattern = r'\[(\d{1,2}:\d{2}:\d{2})\] (.*?)(?=\[\d{1,2}:\d{2}:\d{2}\]|$)'
            dialogues = re.findall(content_pattern, content, re.DOTALL)
            logger.info(f"提取到 {len(dialogues)} 条对话")
            
            # 3. 为每个段落收集内容
            segment_contents = []
            for segment in segments:
                start_time = segment['start_time']
                end_time = segment['end_time']
                title = segment['title']
                
                # 收集该时间段内的所有对话
                segment_content = []
                segment_content.append(f"# {title}")
                segment_content.append("")  # 空行
                
                for time_stamp, content_text in dialogues:
                    # 将时间戳转换为秒数进行比较
                    dialogue_seconds = ContentDetailerService.parse_timestamp(time_stamp)
                    start_seconds = ContentDetailerService.parse_timestamp(start_time)
                    end_seconds = ContentDetailerService.parse_timestamp(end_time)
                    
                    if start_seconds <= dialogue_seconds < end_seconds:
                        segment_content.append(f"[{time_stamp}] {content_text.strip()}")
                
                # 只有当段落有内容时才添加
                if len(segment_content) > 2:  # 标题和空行之外还有内容
                    segment_contents.append("\n".join(segment_content))
            
            logger.info(f"成功分割内容为 {len(segment_contents)} 个段落")
            return segment_contents
            
        except Exception as e:
            logger.error(f"分割字幕内容失败: {str(e)}")
            raise
    
    @classmethod
    async def get_subtitle_content(cls, article_id: int) -> str:
        """获取文章的原文字幕内容
        
        Args:
            article_id: 文章ID
            
        Returns:
            str: 原文字幕内容
        """
        try:
            # 获取任意语言的原文字幕
            subtitle_sections = await SupabaseService.get_article_section_by_type(
                article_id=article_id,
                section_type="原文字幕"
            )
            
            # 如果返回多条记录,优先取英文的一条
            subtitle_section = None
            if subtitle_sections:
                # 优先查找英文字幕
                for section in subtitle_sections:
                    if section.get("language") == "en":
                        subtitle_section = section
                        break
                # 如果没有英文字幕,取第一条
                if not subtitle_section:
                    subtitle_section = subtitle_sections[0]

            if not subtitle_section:
                raise ValueError(f"未找到原文字幕: article_id={article_id}")
            
            subtitle_content = subtitle_section.get("content")
            if not subtitle_content:
                raise ValueError(f"原文字幕内容为空: article_id={article_id}")
            
            logger.info(f"获取到原文字幕内容，长度: {len(subtitle_content)}")
            return subtitle_content
            
        except Exception as e:
            logger.error(f"获取原文字幕内容失败: {str(e)}")
            raise