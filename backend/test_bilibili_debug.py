#!/usr/bin/env python3
"""
B站字幕获取调试脚本
用于测试和诊断B站视频字幕获取问题
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.content_fetcher.bilibili import BilibilitFetcher

async def test_bilibili_debug(url: str):
    """测试B站视频内容获取"""
    print("="*60)
    print("B站字幕获取调试测试（支持重试机制）")
    print("="*60)
    print(f"测试URL: {url}")
    print(f"⚙️  配置: 最多重试5次，每次间隔20秒")
    print()
    
    fetcher = BilibilitFetcher()
    
    try:
        # 测试fetch方法
        print("🚀 开始测试完整获取流程...")
        import time
        start_time = time.time()
        
        content = await fetcher.fetch(url)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        if content:
            print(f"\n✅ 获取成功! (耗时: {elapsed:.1f} 秒)")
            print(f"📊 最终内容统计:")
            print(f"   - 总长度: {len(content)} 字符")
            
            # 简单分析内容质量
            lines = content.split('\n')
            print(f"   - 总行数: {len(lines)} 行")
            
            # 检查字幕质量
            if '字幕内容:' in content:
                subtitle_start = content.find('字幕内容:') + len('字幕内容:')
                subtitle_content = content[subtitle_start:].strip()
                print(f"   - 字幕长度: {len(subtitle_content)} 字符")
                
                # 使用内置质量检查
                if fetcher.is_high_quality_subtitle(subtitle_content):
                    print(f"   ✅ 字幕质量验证: 高质量字幕")
                else:
                    print(f"   ❌ 字幕质量验证: 低质量字幕")
                
                # 检查是否主要是音乐符号
                music_count = subtitle_content.count('♪')
                music_phrases = ['音乐', '♪', '♫', '♬', '♩']
                music_char_count = sum(subtitle_content.count(phrase) for phrase in music_phrases)
                
                print(f"   📊 质量指标:")
                print(f"      - 音乐符号: {music_count} 个")
                print(f"      - 音乐相关字符: {music_char_count} 个")
                print(f"      - 音乐字符占比: {music_char_count/len(subtitle_content)*100:.1f}%")
                    
                # 显示字幕开头
                preview_length = min(200, len(subtitle_content))
                print(f"   📖 字幕预览: {subtitle_content[:preview_length]}{'...' if len(subtitle_content) > preview_length else ''}")
            else:
                print(f"   ❌ 没有找到字幕内容")
                
        else:
            print(f"\n❌ 获取失败! (耗时: {elapsed:.1f} 秒)")
            
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {str(e)}")
        if "无法获取该视频的高质量字幕内容" in str(e):
            print("🚫 这是预期的行为：系统拒绝了低质量字幕，符合用户要求")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    # 默认测试URL
    test_urls = [
        "https://www.bilibili.com/video/BV1vwLnziEwZ",  # 小白测评的视频
    ]
    
    # 如果有命令行参数，使用参数中的URL
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    for url in test_urls:
        await test_bilibili_debug(url)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main()) 