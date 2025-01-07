from typing import List
import re
from app.utils.logger import logger
from app.services.coze import CozeService
from app.repositories.supabase import SupabaseService
import json
import asyncio

class ContentPolisherService:
    """内容润色服务"""
    
    BATCH_DURATION = 420  # 10分钟 = 600秒
    
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
                
                # 添加内容到对应段落，含时间戳
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
        batches: str, 
        language: str,
        workflow_id: str
    ) -> List[dict]:
        """调用 Coze 接口润色内容批次
        
        Args:
            batches: JSON格式的批次内容
            language: 语言类型
            workflow_id: Coze 工作流 ID
            
        Returns:
            List[dict]: Coze API 的响应结果列表
        """
        try:
            logger.info(f"开始并发调用 Coze API 处理内容润色: language={language}")
            
            # 创建信号量控制并发数
            semaphore = asyncio.Semaphore(15)
            
            # 解析JSON字符串为Python对象
            content_batches = json.loads(batches)
            
            async def process_single_batch(index: int, batch_content: str) -> tuple[int, dict]:
                """处理单个批次内容"""
                async with semaphore:
                    try:
                        logger.info(f"开始处理第 {index + 1} 个批次")
                        coze_service = CozeService()
                        result = await coze_service.polish_content(batch_content, workflow_id)
                        logger.info(f"处理第 {index + 1} 个批次成功" )
                        return index, result
                    except Exception as e:
                        logger.error(f"处理第 {index + 1} 个批次失败: {str(e)}")
                        raise
            
            # 创建所有任务
            tasks = [
                process_single_batch(i, batch)
                for i, batch in enumerate(content_batches)
            ]
            
            # 并发执行所有任务
            results = await asyncio.gather(*tasks)
            
            # 按原始顺序排序结果并返回
            sorted_results = sorted(results, key=lambda x: x[0])
            combined_result = [result[1] for result in sorted_results]
            
            logger.info(f"并发处理完成: 总批次数={len(combined_result)}")
            return combined_result
            
        except Exception as e:
            logger.error(f"并发调用 Coze API 处理内容润色失败: {str(e)}")
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
        try:
            logger.info(f"开始保存润色内容: article_id={article_id}, language={language}")
            
            # 准备小节数据
            section_data = {
                "article_id": article_id,
                "section_type": "原文字幕",  # 使用预定义的小节类型
                "content": polished_content,
                "language": language,
                "sort_order": 1000  # 给一个较大的排序值,确保显示在最后
            }
            
            # 先删除已存在的同类型同语言的小节
            await SupabaseService.delete_article_section(
                article_id=article_id,
                section_type="原文字幕",
                language=language
            )
            
            # 创建新的小节
            await SupabaseService.create_article_sections(article_id, [section_data])
            
            logger.info(f"润色内容保存完成: article_id={article_id}, language={language}")
            
        except Exception as e:
            logger.error(f"保存润色内容失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def parse_polished_content(
        coze_results: List[dict]
    ) -> str:
        """解析润色后的内容
        
        Args:
            coze_results: Coze API 返回的结果列表
            
        Returns:
            str: 解析并格式化后的内容
        """
        try:
            logger.info(f"开始解析润色内容: {len(coze_results)} 个结果")
            
            # 初始化结果列表
            all_dialogues = []
            header_content = None
            
            # 处理每个批次的结果
            for result in coze_results:
                try:
                    # 解析 data 字段的 JSON 字符串
                    result_data = json.loads(result['data'])
                    
                    # 获取第一个对象的 seg_header
                    if header_content is None and 'seg_header' in result_data:
                        header_content = result_data['seg_header']
                    
                    # 获取对话内容
                    dialogue_content = result_data.get('seg_dialogue', '')
                    if not dialogue_content:
                        continue
                        
                    # 提取所有时间戳行
                    lines = dialogue_content.split('\n')
                    current_timestamp = None
                    current_content = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # 检查是否是时间戳行
                        timestamp_match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]', line)
                        if timestamp_match:
                            # 如果有累积的内容，添加到结果中
                            if current_timestamp and current_content:
                                all_dialogues.append(f"{current_timestamp} {' '.join(current_content)}")
                                
                            # 提取时间戳和内容
                            current_timestamp = f"[{timestamp_match.group(1)}]"
                            content = line[timestamp_match.end():].strip()
                            current_content = [content] if content else []
                        else:
                            # 继续累积当前时间戳的内容
                            if current_timestamp and line:
                                current_content.append(line)
                    
                    # 添加最后一行
                    if current_timestamp and current_content:
                        all_dialogues.append(f"{current_timestamp} {' '.join(current_content)}")
                        
                except Exception as e:
                    logger.error(f"解析单个批次结果失败: {str(e)}")
                    continue
            
            # 按时间戳排序
            all_dialogues.sort()
            
            # 构建最终结果
            result_parts = []
            
            # 添加 header（如果存在）
            if header_content:
                result_parts.append(header_content)
                result_parts.append('')  # 添加空行分隔
            
            # 添加对话内容
            result_parts.append('\n'.join(all_dialogues))
            
            # 合并所有内容
            final_content = '\n'.join(result_parts)
            logger.info(f"内容解析完成，最终长度: {len(final_content)}")
            
            return final_content
            
        except Exception as e:
            logger.error(f"解析润色内容失败: {str(e)}")
            raise

    @staticmethod
    def prepare_batches_json(batches: List[str]) -> str:
        """处理批次数组并转换为 JSON 字符串
        
        Args:
            batches: 原始批次数组
            
        Returns:
            str: 处理后的 JSON 字符串
        """
        try:
            logger.info(f"开始处理批次数组: {len(batches)} 个批次")
            
            # 1. 处理每个批次中的特殊字符
            # escaped_batches = []
            # for batch in batches:
            #     # 转义方括号和其他特殊字符
            #     escaped_batch = batch.replace('[', '\\[').replace(']', '\\]')
            #     escaped_batches.append(escaped_batch)
            
            # 2. 将处理后的批次数组转换为 JSON 字符串
            batches_json = json.dumps(batches, ensure_ascii=False)
            logger.info(f"批次数组处理完成, JSON 长度: {len(batches_json)}")
            
            return batches_json
            
        except Exception as e:
            logger.error(f"处理批次数组失败: {str(e)}", exc_info=True)
            raise

    @classmethod
    async def process_article_content(
        cls,
        article_id: int,
        original_content: str,
        language: str,
        workflow_id: str
    ) -> None:
        """处理文章内容的完整流程"""
        try:
            logger.info(f"开始处理文章内容: article_id={article_id}, language={language}")
            
            # 1. 获取对应的请求ID
            request_id = await SupabaseService.get_request_id_by_article_id(article_id)
            logger.info(f"找到对应的请求ID: {request_id}")
            
            # 2. 拆分内容
            batches = cls.split_captions_to_batches(original_content)
            logger.info(f"内容已拆分为 {len(batches)} 个批次")
            
            # 3. 处理批次数组并转换为 JSON
            batches_json = cls.prepare_batches_json(batches)
            
            # 4. 调用 Coze 接口一次性处理所有批次
            coze_results = await cls.polish_content_batch(
                batches_json,
                language,
                workflow_id
            )
            
            # 5. 保存 Coze 返回结果到请求表
            await SupabaseService.update_polished_content(
                request_id=request_id,
                polished_content=coze_results,
                language=language
            )
            logger.info(f"已保存润色结果到请求表: request_id={request_id}")
            
            # 6. 解析润色后的内容
            polished_content = await cls.parse_polished_content(
                coze_results  # 直接传入结果列表
            )
            logger.info("内容解析完成")
            
            # 7. 保存处理后的内容到小节
            await cls.save_polished_content(
                article_id,
                polished_content,
                language
            )
            
            logger.info(f"文章内容处理完成: article_id={article_id}, language={language}")
            
        except Exception as e:
            logger.error(f"处理文章内容失败: {str(e)}", exc_info=True)
            raise