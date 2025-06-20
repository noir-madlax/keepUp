#!/usr/bin/env python3
"""
YouTube PO Token 测试脚本
验证 bgutil-ytdlp-pot-provider 插件和配置是否正常工作
"""

import os
import sys
import asyncio
import requests
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.services.content_fetcher.youtube import YouTubeFetcher

async def test_bgutil_provider():
    """测试 bgutil provider 服务"""
    print("=== 测试 bgutil PO Token provider 服务 ===")
    
    # 检查环境变量
    bgutil_url = os.getenv('BGUTIL_PROVIDER_URL', 'http://localhost:4416')
    print(f"bgutil provider URL: {bgutil_url}")
    
    try:
        # 测试健康检查端点
        response = requests.get(f"{bgutil_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ bgutil provider 服务运行正常")
            
            # 尝试获取 PO Token（如果有相应端点）
            try:
                token_response = requests.post(f"{bgutil_url}/generate", 
                                             json={"client": "mweb"}, 
                                             timeout=10)
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    print(f"✅ 成功生成 PO Token: {token_data.get('poToken', 'N/A')[:20]}...")
                else:
                    print(f"⚠️ PO Token 生成失败: {token_response.status_code}")
            except Exception as e:
                print(f"⚠️ 无法测试 PO Token 生成: {str(e)}")
                
        else:
            print(f"❌ bgutil provider 服务响应异常: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 bgutil provider 服务")
        print("请确保服务已启动：")
        print("  Docker: docker run --name bgutil-provider -d -p 4416:4416 --init brainicism/bgutil-ytdlp-pot-provider")
        print("  或使用 docker-compose up bgutil-provider")
    except Exception as e:
        print(f"❌ bgutil provider 测试失败: {str(e)}")

async def test_youtube_fetcher():
    """测试 YouTube fetcher 配置"""
    print("\n=== 测试 YouTube Fetcher 配置 ===")
    
    print(f"代理配置: USE_PROXY={settings.USE_PROXY}, PROXY_URL={settings.PROXY_URL}")
    print(f"YouTube 调试: YOUTUBE_DEBUG={settings.YOUTUBE_DEBUG}")
    
    # 创建 fetcher 实例
    fetcher = YouTubeFetcher()
    
    # 测试配置生成
    opts = fetcher._get_ydl_opts()
    print(f"yt-dlp 配置选项:")
    print(f"  - 客户端: {opts.get('extractor_args', {}).get('youtube', {}).get('player_client', 'default')}")
    print(f"  - 代理: {opts.get('proxy', 'None')}")
    print(f"  - 安静模式: {opts.get('quiet', False)}")

async def test_youtube_video():
    """测试实际的 YouTube 视频获取"""
    print("\n=== 测试 YouTube 视频获取 ===")
    
    # 使用之前失败的测试 URL
    test_url = "https://www.youtube.com/watch?v=cI1SotLa7Wg"
    print(f"测试 URL: {test_url}")
    
    fetcher = YouTubeFetcher()
    
    try:
        print("开始获取视频信息...")
        video_info = await fetcher.get_video_info(test_url)
        
        if video_info:
            print("✅ 成功获取视频信息:")
            print(f"  - 标题: {video_info.title}")
            print(f"  - 作者: {video_info.author}")
            print(f"  - 时长: {video_info.duration} 秒")
            print(f"  - 观看次数: {video_info.views}")
        else:
            print("❌ 无法获取视频信息")
            
    except Exception as e:
        print(f"❌ 视频获取测试失败: {str(e)}")

async def main():
    """主测试函数"""
    print("YouTube PO Token 配置测试")
    print("=" * 50)
    
    # 测试 bgutil provider
    await test_bgutil_provider()
    
    # 测试 YouTube fetcher 配置
    await test_youtube_fetcher()
    
    # 测试实际视频获取
    await test_youtube_video()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 