#!/usr/bin/env python3
"""
YouTube PO Token 测试脚本 - Script 模式
验证 bgutil-ytdlp-pot-provider 插件的 Script 模式是否正常工作
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import settings
from app.services.content_fetcher.youtube import YouTubeFetcher

async def test_nodejs_availability():
    """测试 Node.js 可用性"""
    print("=== 测试 Node.js 环境 ===")
    
    try:
        # 检查 Node.js 版本
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            node_version = result.stdout.strip()
            print(f"✅ Node.js 可用: {node_version}")
            
            # 检查 npm 版本
            npm_result = subprocess.run(['npm', '--version'], 
                                      capture_output=True, text=True, timeout=5)
            if npm_result.returncode == 0:
                npm_version = npm_result.stdout.strip()
                print(f"✅ npm 可用: {npm_version}")
            else:
                print("⚠️ npm 不可用，但 Node.js 足够运行 bgutil")
                
        else:
            print("❌ Node.js 不可用")
            print("请安装 Node.js (>=18.0) 来支持 PO Token 生成")
            print("下载地址: https://nodejs.org/")
            return False
            
    except FileNotFoundError:
        print("❌ Node.js 未安装")
        print("请安装 Node.js (>=18.0) 来支持 PO Token 生成")
        print("下载地址: https://nodejs.org/")
        return False
    except Exception as e:
        print(f"❌ Node.js 检测失败: {str(e)}")
        return False
        
    return True

async def test_bgutil_plugin():
    """测试 bgutil-ytdlp-pot-provider 插件"""
    print("\n=== 测试 bgutil-ytdlp-pot-provider 插件 ===")
    
    try:
        # 检查是否已安装 bgutil 插件
        import subprocess
        result = subprocess.run(['pip3', 'list'], 
                              capture_output=True, text=True, timeout=5)
        
        if 'bgutil-ytdlp-pot-provider' in result.stdout:
            print("✅ bgutil-ytdlp-pot-provider 插件已安装")
            
            # 获取版本信息
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'bgutil-ytdlp-pot-provider' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        version = parts[1]
                        print(f"   版本: {version}")
                    break
            
            # bgutil 插件是作为 yt-dlp 的扩展工作的，不需要直接导入
            print("   插件将在 yt-dlp 运行时自动加载")
            
        else:
            print("❌ bgutil-ytdlp-pot-provider 插件未安装")
            print("请运行: pip install bgutil-ytdlp-pot-provider")
            return False
            
    except Exception as e:
        print(f"❌ bgutil 插件检测失败: {str(e)}")
        return False
        
    return True

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
    print(f"  - User-Agent: {opts.get('http_headers', {}).get('User-Agent', 'default')[:50]}...")

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

async def test_environment_setup():
    """测试环境设置建议"""
    print("\n=== 环境设置建议 ===")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 在虚拟环境中运行")
    else:
        print("⚠️ 建议在虚拟环境中运行")
    
    # 检查 Python 版本
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python 版本可能过低: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查 yt-dlp 版本
    try:
        import yt_dlp
        print(f"✅ yt-dlp 版本: {yt_dlp.version.__version__}")
    except Exception as e:
        print(f"❌ yt-dlp 检测失败: {str(e)}")

async def main():
    """主测试函数"""
    print("YouTube PO Token 配置测试 - Script 模式")
    print("=" * 60)
    
    # 测试环境设置
    await test_environment_setup()
    
    # 测试 Node.js 可用性
    nodejs_ok = await test_nodejs_availability()
    
    # 测试 bgutil 插件
    plugin_ok = await test_bgutil_plugin()
    
    # 测试 YouTube fetcher 配置
    await test_youtube_fetcher()
    
    # 只有在基础环境 OK 的情况下才测试视频获取
    if nodejs_ok and plugin_ok:
        await test_youtube_video()
    else:
        print("\n⚠️ 基础环境不完整，跳过视频获取测试")
        print("请先解决上述问题后再次运行测试")
    
    print("\n" + "=" * 60)
    print("测试完成")
    
    if nodejs_ok and plugin_ok:
        print("\n🎉 环境配置正常，可以开始使用 YouTube 视频获取功能")
    else:
        print("\n⚠️ 需要完成环境配置才能正常使用 YouTube 功能")

if __name__ == "__main__":
    asyncio.run(main()) 