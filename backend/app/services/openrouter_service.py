import httpx
from typing import Optional, Dict, Any
from app.config import settings
from app.utils.logger import logger
from app.repositories.prompt_repository import PromptRepository
from app.repositories.supabase import SupabaseService
from app.repositories.llm_records_repository import LLMRecordsRepository
from app.utils.decorators import retry_decorator

class OpenRouterService:
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "anthropic/claude-3.7-sonnet"
    
    @staticmethod
    async def get_prompt_data(lang: str) -> Optional[str]:
        """获取对应语言的提示词
        
        Args:
            lang: 语言代码 ('zh' 或 'en')
            
        Returns:
            Optional[str]: 提示词内容
        """
        try:
            prompt_type = f"summary_{lang}"
            prompt = await PromptRepository.get_prompt_by_type(prompt_type)
            if not prompt:
                logger.error(f"未找到语言 {lang} 的提示词")
                return None
            return prompt.content
        except Exception as e:
            logger.error(f"获取提示词失败: {str(e)}")
            return None

    @staticmethod
    @retry_decorator()
    async def call_openrouter_api(prompt: str, content: str, request_id: int, lang: str) -> Optional[Dict[str, Any]]:
        """调用 OpenRouter API
        
        Args:
            prompt: 提示词
            content: 需要总结的内容
            request_id: 请求ID
            lang: 语言代码
            
        Returns:
            Optional[Dict[str, Any]]: API 返回的原始响应
            
        Raises:
            Exception: API调用失败时抛出异常
            
        Note:
            2024-03-14: 第三次重试时使用beta模型
        """
        response_data = None
        error_msg = None
        
        try:
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"
            }
            
            request_data = {
                "model": OpenRouterService.MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": "Please follow my requirement to summary the content"
                    },
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "text",
                                "text": content
                            }
                        ]
                    }
                ],
                "provider": {
                    "order": [
                      "Amazon Bedrock",
                      "Google"
                    ],
                    "allow_fallbacks": False
                },
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    OpenRouterService.API_URL,
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                )
                
                response_data = response.json()
                
                # 检查错误响应
                if 'error' in response_data:
                    # 2024-03-14: 添加完整的响应数据日志
                    logger.error(f"API完整响应数据: {response_data}")
                    
                    error_info = response_data['error']
                    error_code = error_info.get('code', 0)
                    error_message = error_info.get('message', 'Unknown error')
                    metadata = error_info.get('metadata', {})
                    # 2024-03-14: 添加provider信息到错误日志
                    provider = response_data.get('provider', 'Unknown provider')
                    
                    error_msg = (
                        f"OpenRouter API调用失败: \n"
                        f"错误码: {error_code}\n"
                        f"错误信息: {error_message}\n"
                        f"Provider: {provider}\n"
                        f"元数据: {metadata}"
                    )
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                # 检查响应状态码
                if response.status_code == 200:
                    logger.info(f"OpenRouter API调用成功: {response_data}")
                    return response_data
                else:
                    error_msg = f"OpenRouter API调用失败: HTTP状态码 {response.status_code}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"OpenRouter API调用异常: {error_msg}")
            raise e
            
        finally:
            # 无论成功失败都记录调用结果
            await LLMRecordsRepository.create_record(
                request_id=request_id,
                provider="openrouter",
                model=OpenRouterService.MODEL,
                prompt_type=f"summary_{lang}",
                input_content=request_data,  # 存储完整的请求数据
                output_content=response_data,  # 存储完整的响应数据
                error_message=error_msg
            )

    @staticmethod
    def validate_api_response(response: Optional[Dict[str, Any]], lang: str) -> Optional[str]:
        """验证API响应的有效性并提取内容
        
        Args:
            response: API的原始响应
            lang: 语言代码 ('zh' 或 'en')
            
        Returns:
            Optional[str]: 提取的内容摘要，验证失败返回None
            
        Raises:
            ValueError: 当内容长度不足时抛出异常
        """
        try:
            if not response:
                return None
                
            if 'choices' not in response or not response['choices']:
                logger.error("API响应中未找到choices字段")
                return None
                
            content = response['choices'][0].get('message', {}).get('content')
            if not content:
                logger.error("API响应中未找到content内容")
                return None
            
            # 根据语言类型计算内容长度
            if lang == 'zh':
                # 计算中文字符数（去除空白字符）
                char_count = len([c for c in content if not c.isspace()])
                min_length = 100  # 中文最少200字
                if char_count < min_length:
                    error_msg = f"Summary content too short, current character count: {char_count}, minimum required: {min_length} characters"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            else:
                # 计算英文单词数
                word_count = len(content.split())
                min_length = 100  # 英文最少100词
                if word_count < min_length:
                    error_msg = f"Summary content too short, current word count: {word_count}, minimum required: {min_length} words"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
            return content
            
        except Exception as e:
            logger.error(f"验证API响应失败: {str(e)}")
            raise e

    @staticmethod
    async def save_summary_result(article_id: int, content: str, lang: str) -> bool:
        """保存摘要结果到数据库
        
        Args:
            article_id: 文章ID
            content: 摘要内容
            lang: 语言代码
            
        Returns:
            bool: 保存是否成功
        """
        try:
            await SupabaseService.create_article_sections(article_id, [
                {
                    'article_id': article_id,
                    'content': content,
                    'language': lang,
                    'section_type': '总结'
                }
            ])
            return True
        except Exception as e:
            logger.error(f"保存摘要结果失败: {str(e)}")
            raise e

    @staticmethod
    def extract_summary_content(content: str) -> Optional[str]:
        """从内容中提取Summary部分
        
        Args:
            content: 原始内容
            
        Returns:
            Optional[str]: 提取的Summary内容，如果没有找到返回None
        """
        try:
            # 查找开始和结束标记
            start_marker = "## Summary"
            end_marker = "## End"
            
            start_index = content.find(start_marker)
            end_index = content.find(end_marker)
            
            if start_index == -1 or end_index == -1:
                logger.error("未找到完整的Summary标记")
                return None
                
            # 提取Summary内容（不包含标记本身）
            summary_content = content[start_index + len(start_marker):end_index].strip()
            
            if not summary_content:
                logger.error("提取的Summary内容为空")
                return None
                
            return summary_content
            
        except Exception as e:
            logger.error(f"提取Summary内容失败: {str(e)}")
            return None

    @staticmethod
    def preprocess_api_response(response: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """预处理API响应内容
        
        Args:
            response: API的原始响应
            
        Returns:
            Optional[Dict[str, Any]]: 预处理后的响应，失败返回None
        """
        try:
            if not response:
                return None
                
            # 1. 检查响应格式
            if not isinstance(response, dict):
                logger.error("API响应格式错误，预期为字典类型")
                return None
            
            # 2. 检查必要字段
            required_fields = ['choices', 'model', 'usage']
            for field in required_fields:
                if field not in response:
                    logger.error(f"API响应缺少必要字段: {field}，完整响应内容: {response}")
                    return None
            
            # 3. 检查并记录token使用情况
            usage = response.get('usage', {})
            if usage:
                logger.info(f"Token使用情况: 完成={usage.get('completion_tokens', 0)}, "
                          f"提示={usage.get('prompt_tokens', 0)}, "
                          f"总计={usage.get('total_tokens', 0)}")
            
            # 4. 检查响应模型是否匹配
            if response.get('model') != OpenRouterService.MODEL:
                logger.warning(f"响应模型不匹配: 预期={OpenRouterService.MODEL}, "
                             f"实际={response.get('model')}")
            
            # 5. 处理响应内容中的特殊字符和格式
            if response.get('choices') and response['choices'][0].get('message', {}).get('content'):
                content = response['choices'][0]['message']['content']
                # 清理内容中的特殊字符
                content = content.strip()
                
                # 提取Summary部分
                summary_content = OpenRouterService.extract_summary_content(content)
                if not summary_content:
                    return None
                
                # 更新处理后的内容
                response['choices'][0]['message']['content'] = summary_content
            
            return response
            
        except Exception as e:
            logger.error(f"预处理API响应失败: {str(e)}")
            raise e

    @staticmethod
    async def translate_and_save_summary(article_id: int, summary_content: str) -> None:
        """将英文总结翻译成中文并保存
        
        Args:
            article_id: 文章ID
            summary_content: 英文总结内容
            
        Note:
            2024-03-14: 新增自动翻译功能
        """
        try:
            # 构造翻译的system prompt
            system_prompt = """你是一位专业的翻译专家，擅长将英文准确流畅地翻译成中文。请遵循以下要求：

1. 保持原文的格式结构完全不变，包括markdown格式、缩进、换行等
2. 准确传达原文的专业术语和技术内容
3. 保持原文的段落结构和标题层级
4. 对于数字、日期、百分比等内容保持原样
5. 翻译时要注意上下文连贯性，使用恰当的中文表达
6. 保持专业性的同时确保中文表达通顺自然
7. 对于专有名词，第一次出现时可以保留英文原文，后续使用中文译名

请将以下内容翻译成中文："""

            # 调用deepseek进行翻译
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"
            }
            
            request_data = {
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": summary_content
                    }
                ],
                "max_tokens": 3000,
                "temperature": 0.1,
                "provider": {
                    "order": [
                      "Fireworks",
                      "DeepInfra"
                    ],
                    "allow_fallbacks": True
                }
            }
            
            # 调用deepseek进行翻译
            logger.info(f"开始调用翻译API，使用模型: {request_data['model']}")
            logger.info(f"翻译内容长度: {len(summary_content)} 字符")
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=request_data,
                        timeout=30.0
                    )
                    logger.info(f"翻译API响应状态码: {response.status_code}")
                    logger.info(f"翻译API原始响应: {response.text}")
                    
                    response_data = response.json()
                    logger.info(f"翻译API响应数据: {response_data}")
                    
                    if response.status_code == 200 and 'choices' in response_data:
                        translated_content = response_data['choices'][0]['message']['content']
                        logger.info(f"翻译成功，翻译后内容长度: {len(translated_content)} 字符")
                        # 保存中文翻译结果
                        await OpenRouterService.save_summary_result(article_id, translated_content, 'zh')
                        logger.info(f"英文总结已成功翻译并保存为中文版本: article_id={article_id}")
                    else:
                        logger.error(f"翻译API调用失败: {response_data}")
                except Exception as e:
                    logger.error(f"翻译API请求过程中发生错误: {str(e)}", exc_info=True)
                    
        except Exception as e:
            # 翻译失败不影响主流程
            logger.error(f"翻译英文总结到中文时发生错误: {str(e)}")

    @staticmethod
    async def get_summary(content: str, request_id: int, article_id: int, lang: str) -> Optional[str]:
        """获取内容总结的主方法
        
        Args:
            content: 需要总结的内容
            article_id: 文章ID
            lang: 语言代码
            
        Returns:
            Optional[str]: 总结结果，如果失败返回 None
        """
        # 1. 获取提示词
        prompt = await OpenRouterService.get_prompt_data(lang)
        if not prompt:
            raise Exception("获取提示词失败")
            
        # 2. 调用API
        api_response = await OpenRouterService.call_openrouter_api(prompt, content, request_id, lang)
        
        # 3. 预处理响应
        processed_response = OpenRouterService.preprocess_api_response(api_response)
        if not processed_response:
            raise Exception("预处理API响应失败")
        
        # 4. 验证响应
        summary_content = OpenRouterService.validate_api_response(processed_response, lang)
        if not summary_content:
            raise Exception("验证API响应失败")
            
        # 5. 保存结果
        await OpenRouterService.save_summary_result(article_id, summary_content, lang)
            
        # 6. 如果是英文总结，则自动翻译成中文并保存
        # if lang == 'en':
        #     await OpenRouterService.translate_and_save_summary(article_id, summary_content)
            
        return summary_content 
