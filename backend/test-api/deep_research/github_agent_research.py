#!/usr/bin/env python3
"""
GitHub Agent 项目分析脚本 - 使用 Gemini Deep Research API

分析目标：AI Travel Planner Agent Team
https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_ai_agents/multi_agent_apps/agent_teams/ai_travel_planner_agent_team

使用方法:
    cd backend
    source .venv/bin/activate
    python test-api/deep_research/github_agent_research.py
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# 禁用输出缓冲
sys.stdout.reconfigure(line_buffering=True)

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from google import genai
except ImportError:
    print("❌ 请安装 google-genai: pip install google-genai")
    sys.exit(1)


def get_gemini_api_key() -> str:
    """获取 Gemini API Key"""
    api_key = os.getenv("GEMINI_API_KEY_ANALYZE") or os.getenv("GEMINI_API_KEY")
    
    if api_key:
        return api_key
    
    # 尝试从 .env 文件读取
    env_paths = [
        Path(__file__).parent.parent.parent / ".env",
        Path(__file__).parent / ".env",
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY_ANALYZE="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
                    if line.startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    raise RuntimeError(
        "未找到 GEMINI_API_KEY_ANALYZE 或 GEMINI_API_KEY 环境变量。\n"
        "请在 backend/.env 中配置或设置环境变量。"
    )


def build_github_agent_prompt(github_url: str) -> str:
    """构建 GitHub Agent 项目分析的 prompt"""
    return f"""# 背景
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


def run_deep_research(prompt: str, output_dir: Path, topic_name: str) -> dict:
    """
    运行 Gemini Deep Research Agent
    
    Args:
        prompt: 研究主题和问题
        output_dir: 输出目录
        topic_name: 主题名称，用于文件命名
        
    Returns:
        研究结果字典
    """
    api_key = get_gemini_api_key()
    client = genai.Client(api_key=api_key)
    
    print("=" * 60, flush=True)
    print(f"🔬 Gemini Deep Research Agent - {topic_name}", flush=True)
    print("=" * 60, flush=True)
    print(f"\n📝 研究主题:\n{prompt[:800]}...", flush=True)
    print("\n" + "-" * 60, flush=True)
    
    # 启动 Deep Research Agent
    print("\n🚀 启动 Deep Research Agent...", flush=True)
    print("   Agent: deep-research-pro-preview-12-2025", flush=True)
    print("   模式: 后台异步执行 (background=True)", flush=True)
    
    try:
        interaction = client.interactions.create(
            input=prompt,
            agent="deep-research-pro-preview-12-2025",
            background=True
        )
        
        interaction_id = interaction.id
        print(f"\n✅ 研究任务已启动")
        print(f"   Interaction ID: {interaction_id}")
        print(f"   状态: {interaction.status}")
        
    except Exception as e:
        print(f"\n❌ 启动研究任务失败: {e}")
        raise
    
    # 轮询等待结果
    print("\n⏳ 等待研究完成...")
    print("   (Deep Research 通常需要 5-20 分钟，最长 60 分钟)")
    print()
    
    poll_interval = 15  # 每15秒检查一次
    max_wait_time = 60 * 60  # 最长等待60分钟
    start_time = time.time()
    last_status = None
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > max_wait_time:
            print(f"\n⚠️ 超时: 已等待超过 {max_wait_time // 60} 分钟")
            break
        
        try:
            interaction = client.interactions.get(interaction_id)
            current_status = interaction.status
            
            # 状态变化时打印
            if current_status != last_status:
                print(f"   [{datetime.now().strftime('%H:%M:%S')}] 状态: {current_status}")
                last_status = current_status
            else:
                # 每分钟打印一次进度
                if int(elapsed) % 60 == 0 and int(elapsed) > 0:
                    print(f"   [{datetime.now().strftime('%H:%M:%S')}] 已等待 {int(elapsed // 60)} 分钟...")
            
            if current_status == "completed":
                print(f"\n✅ 研究完成! (耗时: {int(elapsed // 60)} 分钟 {int(elapsed % 60)} 秒)")
                break
            elif current_status == "failed":
                error_msg = getattr(interaction, 'error', '未知错误')
                print(f"\n❌ 研究失败: {error_msg}")
                break
            elif current_status == "cancelled":
                print(f"\n⚠️ 研究被取消")
                break
                
        except Exception as e:
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] 轮询出错: {e}")
        
        time.sleep(poll_interval)
    
    # 提取结果
    result = {
        "interaction_id": interaction_id,
        "status": interaction.status,
        "prompt": prompt,
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": time.time() - start_time,
        "report": None,
        "outputs": []
    }
    
    if interaction.status == "completed" and interaction.outputs:
        # 获取最终报告文本
        for output in interaction.outputs:
            output_data = {
                "type": getattr(output, 'type', 'unknown'),
            }
            if hasattr(output, 'text') and output.text:
                output_data["text"] = output.text
                # 最后一个文本输出通常是最终报告
                result["report"] = output.text
            result["outputs"].append(output_data)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存 JSON 结果
    json_path = output_dir / f"{topic_name}_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n📄 JSON 结果已保存: {json_path}")
    
    # 保存 Markdown 报告
    if result["report"]:
        md_path = output_dir / f"{topic_name}_{timestamp}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# AI Travel Planner Agent Team 项目分析报告\n\n")
            f.write(f"**分析目标**: https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_ai_agents/multi_agent_apps/agent_teams/ai_travel_planner_agent_team\n\n")
            f.write(f"**生成时间**: {result['timestamp']}\n\n")
            f.write(f"**耗时**: {int(result['elapsed_seconds'] // 60)} 分钟 {int(result['elapsed_seconds'] % 60)} 秒\n\n")
            f.write(f"---\n\n")
            f.write(result["report"])
        print(f"📝 Markdown 报告已保存: {md_path}")
    
    return result


def main():
    """主函数"""
    # 目标 GitHub 项目 URL
    github_url = "https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_ai_agents/multi_agent_apps/agent_teams/ai_travel_planner_agent_team"
    
    # 构建分析 prompt
    research_prompt = build_github_agent_prompt(github_url)
    
    # 输出目录
    output_dir = Path(__file__).parent / "output"
    
    print("\n" + "=" * 60)
    print("🔬 GitHub Agent 项目分析 - Gemini Deep Research")
    print("=" * 60)
    print(f"\n📌 分析目标: {github_url}")
    
    try:
        result = run_deep_research(
            research_prompt, 
            output_dir, 
            topic_name="travel_agent_analysis"
        )
        
        print("\n" + "=" * 60)
        print("📊 分析结果摘要")
        print("=" * 60)
        
        if result["report"]:
            # 打印报告前3000字符作为预览
            preview = result["report"][:3000]
            print(f"\n{preview}")
            if len(result["report"]) > 3000:
                print(f"\n... (完整报告共 {len(result['report'])} 字符，请查看保存的文件)")
        else:
            print("\n⚠️ 未能获取到分析报告")
            
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
