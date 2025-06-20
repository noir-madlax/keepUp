#!/usr/bin/env python3
"""
手动测试 bgutil-ytdlp-pot-provider 插件
验证 PO Token 生成和 yt-dlp 集成
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_node_js():
    """测试 Node.js 环境"""
    print("=== 测试 Node.js 环境 ===")
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Node.js 版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js 不可用")
            return False
    except Exception as e:
        print(f"❌ Node.js 检测失败: {str(e)}")
        return False

def test_bgutil_package():
    """测试 bgutil 包安装"""
    print("\n=== 测试 bgutil 包安装 ===")
    try:
        result = subprocess.run(['pip3', 'show', 'bgutil-ytdlp-pot-provider'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ bgutil-ytdlp-pot-provider 包已安装")
            print(f"包信息:\n{result.stdout}")
            return True
        else:
            print("❌ bgutil-ytdlp-pot-provider 包未安装")
            return False
    except Exception as e:
        print(f"❌ 包检测失败: {str(e)}")
        return False

def test_yt_dlp_with_debug():
    """使用调试模式测试 yt-dlp"""
    print("\n=== 测试 yt-dlp 调试模式 ===")
    
    test_url = "https://www.youtube.com/watch?v=cI1SotLa7Wg"
    
    try:
        import yt_dlp
        
        # 使用详细调试配置
        opts = {
            'quiet': False,
            'verbose': True,
            'debug_printtraffic': True,
            'skip_download': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['mweb'],
                    'player_skip': ['configs'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
            }
        }
        
        print(f"测试 URL: {test_url}")
        print(f"yt-dlp 配置: {json.dumps(opts, indent=2)}")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            print("\n开始提取视频信息...")
            info = ydl.extract_info(test_url, download=False)
            
            if info:
                print("✅ 成功获取视频信息")
                print(f"标题: {info.get('title', 'N/A')}")
                print(f"作者: {info.get('uploader', 'N/A')}")
                print(f"时长: {info.get('duration', 'N/A')} 秒")
                
                # 检查响应中的关键字段
                print("\n=== 检查响应中的关键字段 ===")
                response_str = str(info)
                if 'po_token' in response_str.lower():
                    print("✅ 响应中包含 po_token")
                else:
                    print("⚠️ 响应中未发现 po_token")
                
                if 'visitor_data' in response_str.lower():
                    print("✅ 响应中包含 visitor_data")
                else:
                    print("⚠️ 响应中未发现 visitor_data")
                
                return True
            else:
                print("❌ 未获取到视频信息")
                return False
                
    except Exception as e:
        print(f"❌ yt-dlp 测试失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print(f"完整错误: {traceback.format_exc()}")
        return False

def test_yt_dlp_extractor_info():
    """测试 yt-dlp extractor 信息"""
    print("\n=== 测试 yt-dlp extractor 信息 ===")
    
    try:
        import yt_dlp
        
        opts = {'quiet': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            # 获取 YouTube extractor
            youtube_ie = ydl.get_info_extractor('Youtube')
            if youtube_ie:
                print(f"✅ YouTube extractor: {type(youtube_ie).__name__}")
                
                # 检查 extractor 的属性和方法
                methods = [method for method in dir(youtube_ie) if not method.startswith('_')]
                print(f"可用方法数量: {len(methods)}")
                
                # 检查关键方法
                key_methods = ['extract', 'suitable', 'working']
                for method in key_methods:
                    if hasattr(youtube_ie, method):
                        print(f"✅ 支持方法: {method}")
                    else:
                        print(f"❌ 不支持方法: {method}")
                
                # 检查 PO Token 相关属性
                po_token_attrs = [attr for attr in dir(youtube_ie) if 'token' in attr.lower()]
                if po_token_attrs:
                    print(f"✅ PO Token 相关属性: {po_token_attrs}")
                else:
                    print("⚠️ 未发现 PO Token 相关属性")
                
                return True
            else:
                print("❌ 无法获取 YouTube extractor")
                return False
                
    except Exception as e:
        print(f"❌ extractor 信息获取失败: {str(e)}")
        return False

def test_bgutil_direct():
    """尝试直接测试 bgutil 功能"""
    print("\n=== 尝试直接测试 bgutil 功能 ===")
    
    # 注意：bgutil-ytdlp-pot-provider 通常作为 yt-dlp 插件工作
    # 不一定有直接的 API 接口
    
    try:
        # 检查是否有 bgutil 相关的可执行文件或模块
        result = subprocess.run(['python3', '-c', 'import sys; print([p for p in sys.path if "bgutil" in p])'], 
                              capture_output=True, text=True, timeout=5)
        print(f"Python 路径中的 bgutil 相关路径: {result.stdout.strip()}")
        
        # 尝试查找 bgutil 相关的文件
        import site
        site_packages = site.getsitepackages()
        for path in site_packages:
            bgutil_path = Path(path) / 'bgutil_ytdlp_pot_provider'
            if bgutil_path.exists():
                print(f"✅ 找到 bgutil 包路径: {bgutil_path}")
                
                # 列出包内容
                files = list(bgutil_path.glob('*'))
                print(f"包内容: {[f.name for f in files]}")
                break
        else:
            print("⚠️ 未找到 bgutil 包路径")
        
        return True
        
    except Exception as e:
        print(f"❌ bgutil 直接测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("手动测试 bgutil-ytdlp-pot-provider 插件")
    print("=" * 60)
    
    # 测试基础环境
    node_ok = test_node_js()
    package_ok = test_bgutil_package()
    
    # 测试 yt-dlp extractor
    extractor_ok = test_yt_dlp_extractor_info()
    
    # 测试 bgutil 直接功能
    bgutil_ok = test_bgutil_direct()
    
    # 只有在基础环境 OK 的情况下才测试视频获取
    if node_ok and package_ok:
        print("\n" + "="*60)
        print("基础环境正常，开始测试视频获取...")
        video_ok = test_yt_dlp_with_debug()
    else:
        print("\n" + "="*60)
        print("基础环境不完整，跳过视频获取测试")
        video_ok = False
    
    print("\n" + "="*60)
    print("测试完成")
    
    if node_ok and package_ok and video_ok:
        print("🎉 所有测试通过，bgutil 插件工作正常")
    else:
        print("⚠️ 部分测试失败，需要检查配置")

if __name__ == "__main__":
    main() 