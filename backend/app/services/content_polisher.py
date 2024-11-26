from typing import List
import re
from app.utils.logger import logger
from app.services.coze import CozeService
from app.services.supabase import SupabaseService
import json

class ContentPolisherService:
    """内容润色服务"""
    
    BATCH_DURATION = 600  # 10分钟 = 600秒
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> int:
        """将时间戳字符串转换为秒数
        
        Args:
            timestamp_str: 格式为 "HH:MM:SS" 的时间戳字符串
            
        Returns:
            int: 转换后的秒数
        """
        hours, minutes, seconds = map(int, timestamp_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def split_captions_to_batches(content: str) -> List[str]:
        """将字幕内容按时间批次拆分
        
        Args:
            content: 原始字幕内容,格式为 "[HH:MM:SS] text"
            
        Returns:
            List[str]: 按10分钟批次拆分的字幕数组
        """
        try:
            # 修改时间戳模式以匹配 "[00:00:00]" 格式
            time_pattern = r'\[(\d{2}:\d{2}:\d{2})\]'
            
            # 初始化分段列表
            segments: List[List[str]] = []
            current_segment: List[str] = []
            
            # 使用finditer来获取所有时间戳及其位置
            matches = list(re.finditer(time_pattern, content))
            
            for i in range(len(matches)):
                time_str = matches[i].group(1)
                current_time = ContentPolisherService.parse_timestamp(time_str)
                
                # 获取当前时间戳到下一个时间戳之间的内容
                content_start = matches[i].end()
                content_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                content_text = content[content_start:content_end].strip()
                # 去掉换行符，保留时间戳
                content_text = content_text.replace('\n', ' ').strip()
                
                # 计算应该属于哪个段落
                segment_index = current_time // ContentPolisherService.BATCH_DURATION
                
                # 如果需要新的段落，就创建一个
                while len(segments) <= segment_index:
                    segments.append([])
                
                # 添加内容到对应段落，包含时间戳
                if content_text:
                    formatted_content = f"[{time_str}] {content_text}"
                    segments[segment_index].append(formatted_content)
            
            # 将每个段落的内容合并成字符串
            return ['\n'.join(segment) for segment in segments if segment]
            
        except Exception as e:
            logger.error(f"拆分字幕内容失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def polish_content_batch(
        batch: str, 
        language: str,
        workflow_id: str
    ) -> str:
        """调用 Coze 接口润色单个批次的内容"""
        try:
            coze_service = CozeService()
            result = await coze_service.polish_content(batch, workflow_id)
            
            # 从响应中提取润色后的内容
            polished_content = json.loads(result['data'])['polished_content']
            return polished_content
            
        except Exception as e:
            logger.error(f"润色内容批次失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def save_polished_content(
        article_id: int,
        polished_content: str,
        language: str
    ) -> None:
        """保存润色后的内容
        
        Args:
            article_id: 文章ID
            polished_content: 润色后的完整内容
            language: 语言类型
        """
        pass

    @classmethod
    async def process_article_content(
        cls,
        article_id: int,
        original_content: str,
        language: str,
        workflow_id: str
    ) -> None:
        """处理文章内容的完整流程
        
        Args:
            article_id: 文章ID
            original_content: 原始内容
            language: 语言类型
            workflow_id: Coze 工作流 ID
        """
        try:
            logger.info(f"开始处理文章内容: article_id={article_id}, language={language}")
            
            # 1. 拆分内容
            batches = cls.split_captions_to_batches(original_content)
            logger.info(f"内容已拆分为 {len(batches)} 个批次")
            
            # 2. 逐批次处理
            polished_batches = []
            for idx, batch in enumerate(batches):
                logger.info(f"处理第 {idx + 1}/{len(batches)} 个批次")
                polished_content = await cls.polish_content_batch(
                    batch,
                    language,
                    workflow_id
                )
                polished_batches.append(polished_content)
            
            # 3. 合并处理后的内容
            final_content = "\n".join(polished_batches)
            
            # 4. 保存处理后的内容
            await cls.save_polished_content(
                article_id,
                final_content,
                language
            )
            
            logger.info(f"文章内容处理完成: article_id={article_id}, language={language}")
            
        except Exception as e:
            logger.error(f"处理文章内容失败: {str(e)}", exc_info=True)
            raise