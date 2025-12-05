"""
AWS Bedrock API 测试脚本 - Claude Haiku 4.5
模拟生产环境的Chat Elaborate功能，对比Gemini 2.5 Flash

测试目标：评估是否可以用AWS的Haiku 4.5替代生产的Gemini Flash模型
"""

import boto3
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 添加backend到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 加载环境变量
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
load_dotenv(env_path)

# 配置
ARTICLE_ID = 2096
# 使用inference profile ID来调用Claude Haiku 4.5
# 参考: https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = os.getenv("AWS_BEDROCK_REGION", "us-east-2")
MAX_TOKENS = 4096  # Chat场景不需要太长的输出

# 从环境变量获取AWS凭证
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# 生产环境使用的BASE_CHAT_PROMPT模板
BASE_CHAT_PROMPT = """基于以下文章内容回答问题。

文章内容:
{article_content}

当前选中内容:
{mark_content}

**必须注意**回答问题的要求如下：

# 角色
你是一个视频、播客内容总结的问答专家。你必须根据原文中的内容进行回答，不能加入文章中没有的内容。
# 注意
当用户提问后，需要先理解用户提出的问题，然后明白用户「选中的内容」和文章整篇内容的关系然后再回答用户问题。
# 内容要求
专业性：首先最重要的要求是对于专业领域的词汇和内容，使用原词汇，确保专业性和精确表达。
富有启发性或深度：其次是要点需要带有启发性或深刻的见解，能够引发读者的思考或进一步的探索。
简洁明了：关键要点是简短而直接的，能够在几句话内传达文章的核心信息。
集中精华：提炼内容中最重要的观点或结论，不包含冗长的细节，旨在抓住读者的注意力并确保其理解文章的核心内容。
总结文章的主旨：反映了文章的整体观点，帮助读者抓住文章的主要方向或论点。
# 质量控制
回答的内容要遵循信息一致性与引用准确性原则，不要加入材料内未提及的信息，如果无法得出回答，就回复：抱歉！原内容中未提及问题相关内容，我无法回答。
覆盖度，评估提取的内容是否全面。易读性，语言清晰简洁。
# 输出格式要求
回答内容要求使用用户使用的语言，或者是用户指定的语言。语气轻松口语化，不要过于书面语言，有交谈感。回答内容长度不超过1500字。
"""

# 模拟生产环境的用户消息（来自截图中的Elaborate请求）
USER_MESSAGE = """能源效率的巨大提升将使AI无处不在


Please elaborate this content in detail, including more specific examples."""

# 选中的内容（mark_content）
MARK_CONTENT = "能源效率的巨大提升将使AI无处不在"


def get_supabase_client():
    """获取Supabase客户端"""
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_article_content_from_db(article_id: int):
    """从数据库获取文章的原始字幕内容"""
    client = get_supabase_client()
    response = client.table("keep_article_requests").select("content").eq("article_id", article_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["content"]
    return None


def call_bedrock_haiku_api(system_prompt: str, user_message: str) -> dict:
    """调用AWS Bedrock Haiku 4.5 API
    
    Args:
        system_prompt: 系统提示词（包含文章内容和选中内容）
        user_message: 用户消息
        
    Returns:
        dict: API返回的响应
    """
    from botocore.config import Config
    
    # 配置超时时间
    config = Config(
        read_timeout=120,  # 2分钟读取超时（Chat场景应该更快）
        connect_timeout=30,
        retries={'max_attempts': 3}
    )
    
    # 创建Bedrock客户端
    bedrock_client = boto3.client(
        'bedrock-runtime',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=config
    )
    
    # 构建请求数据 - 使用Messages API格式
    # 模拟生产环境的消息结构
    request_data = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": MAX_TOKENS,
        "temperature": 0.1,
        "system": system_prompt,  # 使用system字段传递系统提示
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    
    print(f"正在调用AWS Bedrock Haiku 4.5 API...")
    print(f"模型: {MODEL_ID}")
    print(f"区域: {REGION}")
    print(f"System Prompt长度: {len(system_prompt)} 字符")
    print(f"User Message: {user_message[:100]}...")
    
    # 调用Bedrock API
    response = bedrock_client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_data),
        contentType="application/json"
    )
    
    # 解析响应
    response_body = response['body'].read()
    response_data = json.loads(response_body)
    
    return response_data


def save_output(content: str, filename: str):
    """保存输出到文件"""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"输出已保存到: {filepath}")
    return filepath


def main():
    """主函数"""
    print("=" * 70)
    print("AWS Bedrock API 测试 - Claude Haiku 4.5 (Chat Elaborate)")
    print("对比目标: 生产环境的 Gemini 2.5 Flash")
    print("=" * 70)
    
    # 1. 获取文章内容
    print(f"\n[1/3] 从数据库获取文章 {ARTICLE_ID} 的原始字幕...")
    article_content = get_article_content_from_db(ARTICLE_ID)
    if not article_content:
        print(f"错误: 未能获取文章 {ARTICLE_ID} 的内容")
        return
    print(f"成功获取文章内容，长度: {len(article_content)} 字符")
    
    # 2. 构建System Prompt（模拟生产环境）
    system_prompt = BASE_CHAT_PROMPT.format(
        article_content=article_content,
        mark_content=MARK_CONTENT
    )
    
    # 保存输入内容
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_data = {
        "article_id": ARTICLE_ID,
        "model_id": MODEL_ID,
        "region": REGION,
        "max_tokens": MAX_TOKENS,
        "mark_content": MARK_CONTENT,
        "user_message": USER_MESSAGE,
        "system_prompt_length": len(system_prompt),
        "article_content_length": len(article_content),
        "timestamp": timestamp,
        "comparison_target": "google/gemini-2.5-flash (via OpenRouter)"
    }
    save_output(json.dumps(input_data, ensure_ascii=False, indent=2), f"haiku_input_{timestamp}.json")
    
    # 3. 调用API
    print(f"\n[2/3] 调用AWS Bedrock Haiku 4.5 API...")
    print(f"配置: max_tokens={MAX_TOKENS}, temperature=0.1")
    start_time = datetime.now()
    
    try:
        response = call_bedrock_haiku_api(system_prompt, USER_MESSAGE)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("API调用成功!")
        print(f"耗时: {duration:.2f} 秒")
        
        # 记录详细的token使用情况
        usage = response.get('usage', {})
        if usage:
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
            cache_creation = usage.get('cache_creation_input_tokens', 0)
            cache_read = usage.get('cache_read_input_tokens', 0)
            
            print(f"\n=== Token使用详情 ===")
            print(f"输入tokens: {input_tokens}")
            print(f"输出tokens: {output_tokens}")
            print(f"缓存创建tokens: {cache_creation}")
            print(f"缓存读取tokens: {cache_read}")
            print(f"总tokens: {input_tokens + output_tokens}")
            
            # 估算成本 (Claude Haiku 4.5 定价: $0.80/M input, $4/M output)
            input_cost = (input_tokens / 1000000) * 0.80
            output_cost = (output_tokens / 1000000) * 4
            total_cost = input_cost + output_cost
            print(f"\n=== 估算成本 (USD) ===")
            print(f"输入成本: ${input_cost:.6f}")
            print(f"输出成本: ${output_cost:.6f}")
            print(f"总成本: ${total_cost:.6f}")
            
            # 与Gemini Flash对比（估算）
            # Gemini 2.5 Flash 定价约: $0.075/M input, $0.30/M output
            gemini_input_cost = (input_tokens / 1000000) * 0.075
            gemini_output_cost = (output_tokens / 1000000) * 0.30
            gemini_total_cost = gemini_input_cost + gemini_output_cost
            print(f"\n=== Gemini 2.5 Flash 估算成本对比 (USD) ===")
            print(f"Gemini输入成本: ${gemini_input_cost:.6f}")
            print(f"Gemini输出成本: ${gemini_output_cost:.6f}")
            print(f"Gemini总成本: ${gemini_total_cost:.6f}")
            print(f"成本比率 (Haiku/Gemini): {total_cost/gemini_total_cost:.2f}x")
        
        # 检查是否被截断
        stop_reason = response.get('stop_reason', '')
        print(f"\n停止原因: {stop_reason}")
        if stop_reason == 'max_tokens':
            print("⚠️ 警告: 输出被截断!")
        elif stop_reason == 'end_turn':
            print("✅ 输出完整，正常结束")
        
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        # 保存错误信息
        error_data = {
            "error": str(e),
            "timestamp": timestamp,
            "model_id": MODEL_ID,
            "region": REGION,
            "max_tokens": MAX_TOKENS
        }
        save_output(json.dumps(error_data, ensure_ascii=False, indent=2), f"haiku_error_{timestamp}.json")
        return
    
    # 4. 保存输出
    print(f"\n[3/3] 保存输出结果...")
    
    # 提取响应内容
    if 'content' in response and response['content']:
        output_text = response['content'][0].get('text', '')
        
        # 保存完整响应（包含所有元数据）
        response_with_meta = {
            "model": response.get('model', MODEL_ID),
            "id": response.get('id', ''),
            "type": response.get('type', ''),
            "role": response.get('role', ''),
            "stop_reason": response.get('stop_reason', ''),
            "stop_sequence": response.get('stop_sequence'),
            "usage": response.get('usage', {}),
            "duration_seconds": duration,
            "timestamp": timestamp,
            "content_length": len(output_text),
            "content": response.get('content', []),
            "comparison_info": {
                "target_model": "google/gemini-2.5-flash",
                "test_scenario": "Chat Elaborate",
                "mark_content": MARK_CONTENT,
                "user_message": USER_MESSAGE
            }
        }
        save_output(json.dumps(response_with_meta, ensure_ascii=False, indent=2), f"haiku_response_{timestamp}.json")
        
        # 保存回复内容（markdown格式）
        save_output(output_text, f"haiku_chat_output_{timestamp}.md")
        
        print(f"\n输出内容长度: {len(output_text)} 字符")
        
        # 打印回复内容预览
        print(f"\n=== 回复内容预览 ===")
        preview = output_text[:500] + "..." if len(output_text) > 500 else output_text
        print(preview)
        
        print("\n" + "=" * 70)
        print("测试完成!")
        print("=" * 70)
        
        # 打印对比总结
        print(f"\n=== 对比总结 ===")
        print(f"模型: Claude Haiku 4.5 vs Gemini 2.5 Flash")
        print(f"响应时间: {duration:.2f}秒")
        print(f"输出长度: {len(output_text)} 字符")
        if usage:
            print(f"Token消耗: 输入{input_tokens} + 输出{output_tokens} = {input_tokens + output_tokens}")
            print(f"估算成本: Haiku ${total_cost:.6f} vs Gemini ${gemini_total_cost:.6f}")
        
    else:
        print("错误: 响应中未找到内容")
        save_output(json.dumps(response, ensure_ascii=False, indent=2), f"haiku_response_error_{timestamp}.json")


if __name__ == "__main__":
    main()
