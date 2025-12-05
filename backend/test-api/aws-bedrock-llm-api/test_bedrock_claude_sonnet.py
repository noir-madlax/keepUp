"""
AWS Bedrock API 测试脚本
使用 anthropic.claude-sonnet-4-5-20250929-v1:0 模型对文章2096进行内容分析

参考生产环境的openrouter_service.py实现
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
# 使用inference profile ID来调用Claude Sonnet 4.5
# 参考: https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
REGION = os.getenv("AWS_BEDROCK_REGION", "us-east-2")
# 增加max_tokens以避免输出被截断，Claude Sonnet 4.5支持最大16384 output tokens
MAX_TOKENS = 16000

# 从环境变量获取AWS凭证
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BEDROCK_API_KEY = os.getenv("AWS_BEDROCK_API_KEY")

# Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase_client():
    """获取Supabase客户端"""
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_prompt_from_db():
    """从数据库获取summary_zh类型的prompt"""
    client = get_supabase_client()
    response = client.table("keep_prompt").select("*").eq("type", "summary_zh").execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["content"]
    return None


def get_article_content_from_db(article_id: int):
    """从数据库获取文章的原始字幕内容"""
    client = get_supabase_client()
    response = client.table("keep_article_requests").select("content").eq("article_id", article_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]["content"]
    return None


def call_bedrock_api(prompt: str, content: str) -> dict:
    """调用AWS Bedrock API
    
    Args:
        prompt: 提示词
        content: 需要总结的内容
        
    Returns:
        dict: API返回的响应
    """
    from botocore.config import Config
    
    # 配置超时时间（长文本需要更长的处理时间）
    config = Config(
        read_timeout=300,  # 5分钟读取超时
        connect_timeout=60,  # 1分钟连接超时
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
    # 参考生产环境openrouter_service.py的实现
    request_data = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": MAX_TOKENS,  # 增加到16000以避免输出被截断
        "temperature": 0.1,
        "messages": [
            {
                "role": "user",
                "content": f"Please follow my requirement to summary the content\n\n{prompt}\n\n{content}"
            }
        ]
    }
    
    print(f"正在调用AWS Bedrock API...")
    print(f"模型: {MODEL_ID}")
    print(f"区域: {REGION}")
    print(f"输入内容长度: {len(content)} 字符")
    
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
    print("=" * 60)
    print("AWS Bedrock API 测试 - Claude Sonnet 4.5")
    print("=" * 60)
    
    # 1. 获取prompt
    print("\n[1/4] 从数据库获取prompt...")
    prompt = get_prompt_from_db()
    if not prompt:
        print("错误: 未能获取prompt")
        return
    print(f"成功获取prompt，长度: {len(prompt)} 字符")
    
    # 2. 获取文章内容
    print(f"\n[2/4] 从数据库获取文章 {ARTICLE_ID} 的原始字幕...")
    content = get_article_content_from_db(ARTICLE_ID)
    if not content:
        print(f"错误: 未能获取文章 {ARTICLE_ID} 的内容")
        return
    print(f"成功获取文章内容，长度: {len(content)} 字符")
    
    # 保存输入内容
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_data = {
        "article_id": ARTICLE_ID,
        "model_id": MODEL_ID,
        "region": REGION,
        "max_tokens": MAX_TOKENS,
        "prompt_length": len(prompt),
        "content_length": len(content),
        "timestamp": timestamp
    }
    save_output(json.dumps(input_data, ensure_ascii=False, indent=2), f"input_{timestamp}.json")
    
    # 3. 调用API
    print(f"\n[3/4] 调用AWS Bedrock API...")
    print(f"配置: max_tokens={MAX_TOKENS}, temperature=0.1")
    start_time = datetime.now()
    
    try:
        response = call_bedrock_api(prompt, content)
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
            
            # 估算成本 (Claude Sonnet 4.5 定价: $3/M input, $15/M output)
            input_cost = (input_tokens / 1000000) * 3
            output_cost = (output_tokens / 1000000) * 15
            total_cost = input_cost + output_cost
            print(f"\n=== 估算成本 (USD) ===")
            print(f"输入成本: ${input_cost:.6f}")
            print(f"输出成本: ${output_cost:.6f}")
            print(f"总成本: ${total_cost:.6f}")
        
        # 检查是否被截断
        stop_reason = response.get('stop_reason', '')
        print(f"\n停止原因: {stop_reason}")
        if stop_reason == 'max_tokens':
            print("⚠️ 警告: 输出被截断! 需要增加max_tokens")
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
        save_output(json.dumps(error_data, ensure_ascii=False, indent=2), f"error_{timestamp}.json")
        return
    
    # 4. 保存输出
    print(f"\n[4/4] 保存输出结果...")
    
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
            "content": response.get('content', [])
        }
        save_output(json.dumps(response_with_meta, ensure_ascii=False, indent=2), f"response_{timestamp}.json")
        
        # 保存总结内容（markdown格式）
        save_output(output_text, f"summary_{timestamp}.md")
        
        print(f"\n输出内容长度: {len(output_text)} 字符")
        
        # 检查输出是否包含必要的section
        required_sections = ["## Root", "## Summary", "## Trending", "## Segmented Outline", "## Companies & Products", "## End"]
        print(f"\n=== Section检查 ===")
        for section in required_sections:
            if section in output_text:
                print(f"✅ {section}")
            else:
                print(f"❌ {section} - 缺失!")
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
    else:
        print("错误: 响应中未找到内容")
        save_output(json.dumps(response, ensure_ascii=False, indent=2), f"response_error_{timestamp}.json")


if __name__ == "__main__":
    main()
