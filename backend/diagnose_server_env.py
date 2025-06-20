#!/usr/bin/env python3
"""
服务器环境诊断脚本
用于检查 YouTube 获取失败的原因
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    print("=== Python 环境 ===")
    print(f"Python 版本: {sys.version}")
    print(f"Python 可执行文件: {sys.executable}")
    print(f"Python 路径: {sys.path[:3]}...")  # 只显示前3个路径

def check_node_js():
    """检查 Node.js 环境"""
    print("\n=== Node.js 环境 ===")
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js 版本: {version}")
            
            # 检查版本是否 >= 18.0
            try:
                version_num = float(version[1:].split('.')[0])  # 去掉 'v' 前缀
                if version_num >= 18:
                    print("✅ Node.js 版本满足要求 (>= 18.0)")
                else:
                    print(f"❌ Node.js 版本过低，需要 >= 18.0，当前: {version}")
            except:
                print("⚠️ 无法解析 Node.js 版本号")
            
            return True
        else:
            print("❌ Node.js 不可用")
            print(f"错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Node.js 检查失败: {str(e)}")
        return False

def check_packages():
    """检查关键包安装"""
    print("\n=== Python 包检查 ===")
    
    packages = [
        'yt-dlp',
        'bgutil-ytdlp-pot-provider',
        'fastapi',
        'supabase'
    ]
    
    for package in packages:
        try:
            result = subprocess.run(['pip3', 'show', package], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # 提取版本信息
                version = "Unknown"
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        break
                print(f"✅ {package}: {version}")
            else:
                print(f"❌ {package}: 未安装")
        except Exception as e:
            print(f"❌ {package}: 检查失败 - {str(e)}")

def check_yt_dlp_plugins():
    """检查 yt-dlp 插件目录"""
    print("\n=== yt-dlp 插件检查 ===")
    
    try:
        import site
        site_packages = site.getsitepackages()
        print(f"site-packages 路径: {site_packages}")
        
        # 查找 yt_dlp_plugins 目录
        found_plugins = False
        for path in site_packages:
            plugins_path = Path(path) / 'yt_dlp_plugins'
            if plugins_path.exists():
                print(f"✅ 找到插件目录: {plugins_path}")
                plugins = list(plugins_path.glob('*'))
                print(f"插件内容: {[p.name for p in plugins]}")
                found_plugins = True
                
                # 检查 bgutil 相关插件
                bgutil_plugins = [p for p in plugins if 'bgutil' in p.name.lower()]
                if bgutil_plugins:
                    print(f"✅ 找到 bgutil 插件: {[p.name for p in bgutil_plugins]}")
                else:
                    print("⚠️ 未找到 bgutil 相关插件")
        
        if not found_plugins:
            print("❌ 未找到 yt_dlp_plugins 目录")
            
    except Exception as e:
        print(f"❌ 插件目录检查失败: {str(e)}")

def check_bgutil_package_detail():
    """详细检查 bgutil 包"""
    print("\n=== bgutil 包详细检查 ===")
    
    try:
        import bgutil_ytdlp_pot_provider
        print("✅ bgutil_ytdlp_pot_provider 模块可导入")
        
        # 检查模块属性
        if hasattr(bgutil_ytdlp_pot_provider, '__version__'):
            print(f"版本: {bgutil_ytdlp_pot_provider.__version__}")
        
        # 检查模块文件位置
        module_file = bgutil_ytdlp_pot_provider.__file__
        print(f"模块文件: {module_file}")
        
        # 检查模块目录内容
        module_dir = Path(module_file).parent
        files = list(module_dir.glob('*'))
        print(f"模块目录内容: {[f.name for f in files]}")
        
    except ImportError as e:
        print(f"❌ 无法导入 bgutil_ytdlp_pot_provider: {str(e)}")
    except Exception as e:
        print(f"❌ bgutil 包检查失败: {str(e)}")

def test_yt_dlp_basic():
    """基本 yt-dlp 测试"""
    print("\n=== yt-dlp 基本测试 ===")
    
    try:
        import yt_dlp
        print(f"✅ yt-dlp 版本: {yt_dlp.version.__version__}")
        
        # 检查 YouTube extractor
        opts = {'quiet': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            youtube_ie = ydl.get_info_extractor('Youtube')
            if youtube_ie:
                print(f"✅ YouTube extractor: {type(youtube_ie).__name__}")
                
                # 检查 PO Token 相关方法
                po_token_methods = [method for method in dir(youtube_ie) if 'token' in method.lower()]
                if po_token_methods:
                    print(f"✅ PO Token 方法: {po_token_methods}")
                else:
                    print("⚠️ 未找到 PO Token 相关方法")
            else:
                print("❌ 无法获取 YouTube extractor")
                
    except Exception as e:
        print(f"❌ yt-dlp 测试失败: {str(e)}")

def test_yt_dlp_with_bgutil():
    """测试 yt-dlp 与 bgutil 插件集成"""
    print("\n=== yt-dlp + bgutil 集成测试 ===")
    
    test_url = "https://www.youtube.com/watch?v=cI1SotLa7Wg"
    
    try:
        import yt_dlp
        
        # 使用详细模式测试
        opts = {
            'quiet': False,
            'verbose': True,
            'skip_download': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['mweb'],
                    'player_skip': ['configs'],
                }
            },
        }
        
        print(f"测试 URL: {test_url}")
        print("开始提取（这可能需要一些时间）...")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
            if info:
                print("✅ 成功获取视频信息")
                print(f"标题: {info.get('title', 'N/A')}")
                print(f"作者: {info.get('uploader', 'N/A')}")
                print(f"时长: {info.get('duration', 'N/A')} 秒")
                return True
            else:
                print("❌ 未获取到视频信息")
                return False
                
    except Exception as e:
        print(f"❌ 集成测试失败: {str(e)}")
        
        # 检查是否是 PO Token 相关错误
        error_msg = str(e)
        if "Failed to extract any player response" in error_msg:
            print("\n🚨 检测到 PO Token 相关错误！")
            print("可能的原因:")
            print("1. bgutil 插件未正确安装或加载")
            print("2. Node.js 版本不兼容")
            print("3. 网络连接问题")
            print("4. YouTube 政策变更")
        
        return False

def check_environment_variables():
    """检查环境变量"""
    print("\n=== 环境变量检查 ===")
    
    env_vars = [
        'PATH',
        'PYTHONPATH',
        'NODE_PATH',
        'HOME',
        'USER'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value[:100]}{'...' if len(value) > 100 else ''}")

def main():
    """主诊断函数"""
    print("YouTube 获取问题诊断脚本")
    print("=" * 60)
    
    # 基础环境检查
    check_python_version()
    node_ok = check_node_js()
    check_packages()
    check_yt_dlp_plugins()
    check_bgutil_package_detail()
    check_environment_variables()
    
    # 功能测试
    test_yt_dlp_basic()
    
    if node_ok:
        print("\n" + "="*60)
        print("开始集成测试...")
        success = test_yt_dlp_with_bgutil()
        
        if success:
            print("\n🎉 所有测试通过！YouTube 获取应该正常工作")
        else:
            print("\n⚠️ 集成测试失败，需要进一步调试")
    else:
        print("\n⚠️ Node.js 环境有问题，跳过集成测试")
    
    print("\n" + "="*60)
    print("诊断完成")
    print("\n如果问题仍然存在，请将此诊断输出发送给开发者")

if __name__ == "__main__":
    main() 