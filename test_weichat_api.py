import requests
import json

def get_wechat_article_detail(url, key, mode=2, verifycode=""):
    """
    调用极致了API获取微信文章详情
    
    Args:
        url (str): 微信文章链接
        key (str): API密钥
        mode (int): 模式 1-带图片标签纯文本 2-纯文字+富文本格式
        verifycode (str): 附加码
    
    Returns:
        dict: API响应结果
    """
    
    # API接口地址
    api_url = "https://www.dajiala.com/fbmain/monitor/v3/article_detail"
    
    # 请求头
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 请求数据
    data = {
        "url": url,
        "key": key,
        "mode": mode,
        "verifycode": verifycode
    }
    
    try:
        # 发送GET请求，但携带JSON数据
        response = requests.get(api_url, headers=headers, json=data)
        
        print(f"请求状态码: {response.status_code}")
        print(f"请求URL: {api_url}")
        print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析异常: {e}")
        print(f"响应内容: {response.text}")
        return None

def print_article_info(result):
    """
    打印文章信息
    """
    if not result:
        print("没有获取到文章数据")
        return
    
    print("\n" + "="*50)
    print("文章详情")
    print("="*50)
    
    # 基本信息
    print(f"状态码: {result.get('code', 'N/A')}")
    print(f"消费金额: {result.get('cost_money', 'N/A')}")
    print(f"剩余金额: {result.get('remain_money', 'N/A')}")
    
    if result.get('code') == 0:  # 成功
        print(f"\n文章标题: {result.get('title', 'N/A')}")
        print(f"公众号名称: {result.get('nick_name', 'N/A')}")
        print(f"公众号原始ID: {result.get('user_name', 'N/A')}")
        print(f"文章作者: {result.get('author', 'N/A')}")
        print(f"发布时间: {result.get('pubtime', 'N/A')}")
        print(f"创建时间: {result.get('create_time', 'N/A')}")
        print(f"文章摘要: {result.get('desc', 'N/A')}")
        print(f"是否原创: {get_copyright_status(result.get('copyright_stat'))}")
        print(f"IP地址: {result.get('ip_wording', 'N/A')}")
        print(f"文章类型: {get_item_show_type(result.get('item_show_type'))}")
        print(f"文章URL: {result.get('url', 'N/A')}")
        print(f"文章唯一ID: {result.get('hashid', 'N/A')}")
        
        # 内容预览（截取前500字符）
        content = result.get('content', '')
        if content:
            print(f"\n纯文本内容预览:")
            print("-" * 30)
            print(content[:500] + "..." if len(content) > 500 else content)
        
        # 富文本内容预览
        content_multi = result.get('content_multi_text', '')
        if content_multi:
            print(f"\n富文本内容长度: {len(content_multi)} 字符")
        
        # 图片信息
        pictures = result.get('picture_page_info_list', [])
        if pictures:
            print(f"\n文章包含 {len(pictures)} 张图片")
        
        # 视频信息
        videos = result.get('video_page_infos', [])
        if videos:
            print(f"文章包含 {len(videos)} 个视频")
            
    else:
        print(f"\n请求失败，错误码: {result.get('code')}")
        print(get_error_message(result.get('code')))

def get_copyright_status(status):
    """获取版权状态描述"""
    status_map = {
        0: "非原创",
        1: "原创", 
        2: "转载"
    }
    return status_map.get(status, f"未知({status})")

def get_item_show_type(show_type):
    """获取文章类型描述"""
    type_map = {
        0: "图文",
        5: "纯视频",
        7: "纯音乐", 
        8: "纯图片",
        10: "纯文字",
        11: "转载文章"
    }
    return type_map.get(show_type, f"未知({show_type})")

def get_error_message(code):
    """获取错误信息"""
    error_map = {
        101: "文章被删除或违规或公众号已迁移",
        105: "文章解析失败",
        106: "文章解析失败", 
        107: "解析失败，请重试"
    }
    return error_map.get(code, "未知错误")

def main():
    """主函数"""
    # 测试参数
    article_url = "https://mp.weixin.qq.com/s/0q1MQnke6Ss51wyPnITu5g"
    api_key = "JZLd5e11ee5efcfceaa"
    verify_code = "ffff"
    
    print("开始调用微信文章解析API...")
    print(f"文章链接: {article_url}")
    print(f"API密钥: {api_key}")
    print(f"附加码: {verify_code}")
    
    # 调用API获取文章详情
    result = get_wechat_article_detail(
        url=article_url,
        key=api_key,
        mode=2,  # 使用富文本格式
        verifycode=verify_code
    )
    
    # 打印结果
    print_article_info(result)
    
    # 如果成功，保存结果到文件
    if result and result.get('code') == 0:
        with open('article_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n完整结果已保存到 article_result.json 文件")

if __name__ == "__main__":
    main() 