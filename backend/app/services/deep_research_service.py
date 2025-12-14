"""
Deep Research Service - 使用 Gemini Deep Research API 进行深度分析

主要用于分析 GitHub Agent 项目，生成详细的分析报告。
"""

import os
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional
from app.utils.logger import logger
from app.config import settings


class DeepResearchService:
    """Gemini Deep Research 服务"""
    
    # Deep Research Agent 配置
    AGENT_NAME = "deep-research-pro-preview-12-2025"
    POLL_INTERVAL = 15  # 轮询间隔（秒）
    MAX_WAIT_TIME = 60 * 60  # 最长等待时间（60分钟）
    
    # GitHub Agent 分析 Prompt 模板
    GITHUB_AGENT_PROMPT_TEMPLATE = """# 背景
- 我需要学习AI agent的设计和架构，我要自己开发一个非常领先和设计的agent的面向业务场景的应用，用来减少人类工作中的反复和重复性的工作。Github上有很多好的agent的项目，需要阅读代码来了解后学习。
# 角色
- 你是一个ai agent的开发和设计架构的专家，你很擅长用中文讲解github中的agent项目。你特别会对于，agent的内部调用流程和实际ai完成业务场景的流程，这个之间的结合和契合有很深入的探索和表达。
请你深入研究这个 GitHub 上的 AI Agent 项目：{github_url}
# 要求
请按照以下维度进行分析，每个维度都要详细讲解：

---

## 一、项目整体理解

### 1.1 业务场景
- 这个项目解决什么问题？
- 目标用户是谁？
- 核心价值是什么？

### 1.2 人类流程对比
- 如果人类来做这件事，流程是什么？
- 项目如何将人类流程映射为 Agent 流程？
- 哪些步骤被自动化了，哪些保留了人工介入？

---

## 二、架构设计

### 2.1 整体架构
- 请画出架构图（ASCII 或描述）
- 系统分为哪几层？各层职责是什么？
- 数据如何在各层之间流动？

### 2.2 Agent 设计
- 有几个 Agent？各自的职责是什么？
- Agent 之间是什么关系（独立/协作/层级）？
- 为什么要这样拆分 Agent？

### 2.3 编排层 (Orchestrator)
- 编排逻辑在哪个文件？
- 采用什么编排模式（顺序/并行/条件/层级）？
- 为什么选择这种编排方式？
- 编排的核心流程是什么？

---

## 三、Agent 框架分析

### 3.1 使用的框架
- 用了什么 Agent 框架（LangChain/CrewAI/Agno/自研）？
- 框架的特点是什么？
- 与其他主流框架对比有什么优劣？

### 3.2 框架使用情况
- 代码中用到了框架的哪些功能？
- 框架的哪些功能定义了但没用上？为什么？
- 框架与业务代码是如何结合的？职责如何分离？

---

## 四、Agent 实现细节

### 4.1 单个 Agent 的结构
- Agent 由哪些部分组成？
- 每个部分的作用是什么？
- 请举一个具体 Agent 的例子详细说明

### 4.2 Prompt 工程
- instructions 的结构是怎样的？
- expected_output 是如何定义的？
- 有哪些 Prompt 写法值得学习？
- 请列出 3-5 个 Prompt 亮点并解释原因

### 4.3 工具 (Tools)
- 定义了哪些工具？
- 工具是如何与 Agent 关联的？
- 工具的输入输出设计有什么特点？

---

## 五、上下文管理

### 5.1 上下文传递
- Agent 之间如何传递上下文？
- 上下文的格式是固定的还是动态的？
- 上下文内容有多长？如何处理超长情况？

### 5.2 上下文存储
- 运行中的上下文存在哪里（内存/数据库/文件）？
- 是否有持久化？如何实现？
- 中间结果是否保存？

### 5.3 多模态
- 是否涉及多模态内容（图片/音频/视频）？
- 如果有，是如何处理的？

---

## 六、外部依赖

### 6.1 外部 API
- 调用了哪些外部 API？
- 每个 API 的作用是什么？
- API Key 是如何管理的？

### 6.2 LLM 配置
- 使用了什么 LLM 模型？
- 是直接调用还是通过路由层（如 OpenRouter）？
- 模型参数（temperature 等）是如何设置的？

---

## 七、基础设施

### 7.1 日志
- 使用什么日志库？
- 日志的格式和级别是什么？
- 有哪些值得学习的日志实践？

### 7.2 错误处理
- 重试机制是如何实现的？
- 有没有指数退避？
- 异常是如何捕获和处理的？

### 7.3 状态管理
- 有没有任务状态追踪？
- 状态存储在哪里？
- 前端如何获取执行进度？

---

## 八、输入输出处理

### 8.1 输入处理
- 用户输入是什么格式？
- 如何转换为 Agent 可用的格式？
- 有没有输入规范化的设计？

### 8.2 输出处理
- Agent 的原始输出是什么格式？
- 如何转换为结构化数据？
- 是否使用了 Pydantic 等数据验证？

---

## 九、项目特色

### 9.1 创新点
- 这个项目有哪些有创意的设计？
- 有哪些值得借鉴的最佳实践？

### 9.2 不足之处
- 项目有哪些可以改进的地方？
- 如果你来设计，会有什么不同？

---

## 十、学习总结

### 10.1 核心收获
- 从这个项目学到的最重要的 3-5 点是什么？

### 10.2 可复用模式
- 哪些设计模式可以应用到其他 Agent 项目？

### 10.3 下一步
- 如果我要基于此开发自己的 Agent，第一步应该做什么？

---

## 输出要求

1. **不要大段代码**：只给关键几行说明即可
2. **用表格对比**：适合对比的内容用表格呈现
3. **画架构图**：用 ASCII 或描述画出关键架构
4. **举具体例子**：每个概念都用项目中的实例说明
5. **对比人类流程**：始终关联人类做同样事情的方式
6. **语言**：使用中文回答

## 额外检查，完成上面任务后确保以下内容都完成了：
- 专业的分析prompt起到的作用（结合实际内容进行讲解）和结构分层，并且说明为什么要这样设计的深层原因
- 单个或多个agent都是在完成业务流程，你需要把agent之间的调用流程和业务流程（人类原来的工作流程和场景）进行结合说明
- 项目中写代码用到的底层通用代码工具，进行简单的罗列，不赘述（比如日志、容错等基础框架），语言精炼
- agent之间是如何通讯和协调工作的，状态流转这块需要讲解
- agent用到的tools进行简单的罗列，不赘述，语言精炼
- 项目用到的外部api和功能进行简单的罗列，完成的功能和目标说明，其他不赘述，语言精炼
- 给出对我开发自己 "业务场景 agent" 的启发（基于这个咨询 agent，在构建我自己的业务自动化 agent 时可以借鉴的设计思路）
- 这个agent中的独特的亮点是什么，很巧妙的设计有哪些
"""
    
    @classmethod
    def _get_api_key(cls) -> str:
        """获取 Gemini API Key"""
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        if api_key:
            return api_key
        
        # 尝试从环境变量获取
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_ANALYZE")
        
        if not api_key:
            raise RuntimeError("未配置 GEMINI_API_KEY，请在 .env 文件中添加")
        
        return api_key
    
    @classmethod
    def build_github_agent_prompt(cls, github_url: str) -> str:
        """
        构建 GitHub Agent 项目分析的 prompt
        
        Args:
            github_url: GitHub 项目 URL
            
        Returns:
            str: 完整的分析 prompt
        """
        return cls.GITHUB_AGENT_PROMPT_TEMPLATE.format(github_url=github_url)
    
    @classmethod
    async def run_deep_research(cls, github_url: str, request_id: int = None) -> dict:
        """
        运行 Gemini Deep Research 分析
        
        Args:
            github_url: GitHub 项目 URL
            request_id: 请求 ID（用于日志）
            
        Returns:
            dict: {
                "success": bool,
                "report": str (Markdown 格式的分析报告),
                "elapsed_seconds": float,
                "error": str (如果失败)
            }
        """
        try:
            from google import genai
        except ImportError:
            logger.error("[DeepResearch] 缺少 google-genai 包，请安装: pip install google-genai")
            return {
                "success": False,
                "report": None,
                "elapsed_seconds": 0,
                "error": "缺少 google-genai 包"
            }
        
        log_prefix = f"[DeepResearch][Request:{request_id}]" if request_id else "[DeepResearch]"
        
        try:
            api_key = cls._get_api_key()
            client = genai.Client(api_key=api_key)
            
            # 构建分析 prompt
            prompt = cls.build_github_agent_prompt(github_url)
            
            logger.info(f"{log_prefix} 启动 Deep Research 分析: {github_url}")
            
            # 启动 Deep Research Agent（后台异步执行）
            interaction = client.interactions.create(
                input=prompt,
                agent=cls.AGENT_NAME,
                background=True
            )
            
            interaction_id = interaction.id
            logger.info(f"{log_prefix} 研究任务已启动, Interaction ID: {interaction_id}")
            
            # 轮询等待结果
            start_time = time.time()
            last_status = None
            
            while True:
                elapsed = time.time() - start_time
                
                if elapsed > cls.MAX_WAIT_TIME:
                    logger.warning(f"{log_prefix} 超时: 已等待超过 {cls.MAX_WAIT_TIME // 60} 分钟")
                    return {
                        "success": False,
                        "report": None,
                        "elapsed_seconds": elapsed,
                        "error": "Deep Research 超时"
                    }
                
                # 使用异步 sleep 避免阻塞
                await asyncio.sleep(cls.POLL_INTERVAL)
                
                try:
                    interaction = client.interactions.get(interaction_id)
                    current_status = interaction.status
                    
                    # 状态变化时记录日志
                    if current_status != last_status:
                        logger.info(f"{log_prefix} 状态更新: {current_status} (已等待 {int(elapsed)} 秒)")
                        last_status = current_status
                    
                    if current_status == "completed":
                        elapsed = time.time() - start_time
                        logger.info(f"{log_prefix} 分析完成! 耗时: {int(elapsed // 60)} 分钟 {int(elapsed % 60)} 秒")
                        break
                    elif current_status == "failed":
                        error_msg = getattr(interaction, 'error', '未知错误')
                        logger.error(f"{log_prefix} 分析失败: {error_msg}")
                        return {
                            "success": False,
                            "report": None,
                            "elapsed_seconds": time.time() - start_time,
                            "error": f"Deep Research 失败: {error_msg}"
                        }
                    elif current_status == "cancelled":
                        logger.warning(f"{log_prefix} 分析被取消")
                        return {
                            "success": False,
                            "report": None,
                            "elapsed_seconds": time.time() - start_time,
                            "error": "Deep Research 被取消"
                        }
                        
                except Exception as poll_error:
                    logger.warning(f"{log_prefix} 轮询出错: {poll_error}")
                    # 继续轮询，不立即失败
            
            # 提取分析报告
            report = None
            if interaction.status == "completed" and interaction.outputs:
                for output in interaction.outputs:
                    if hasattr(output, 'text') and output.text:
                        report = output.text
            
            if not report:
                logger.warning(f"{log_prefix} 分析完成但未获取到报告内容")
                return {
                    "success": False,
                    "report": None,
                    "elapsed_seconds": time.time() - start_time,
                    "error": "未获取到分析报告内容"
                }
            
            logger.info(f"{log_prefix} 成功获取分析报告, 长度: {len(report)} 字符")
            
            return {
                "success": True,
                "report": report,
                "elapsed_seconds": time.time() - start_time,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"{log_prefix} Deep Research 异常: {e}")
            return {
                "success": False,
                "report": None,
                "elapsed_seconds": 0,
                "error": str(e)
            }
