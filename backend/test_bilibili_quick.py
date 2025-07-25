#!/usr/bin/env python3
"""
B站字幕快速测试脚本
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.content_fetcher.bilibili import BilibilitFetcher

async def quick_test(url: str):
    """快速测试B站字幕获取"""
    print(f"🧪 快速测试: {url}")
    
    fetcher = BilibilitFetcher()
    
    try:
        import time
        start = time.time()
        
        content = await fetcher.fetch(url)
        
        elapsed = time.time() - start
        
        if content and '字幕内容:' in content:
            subtitle_start = content.find('字幕内容:') + len('字幕内容:')
            subtitle_content = content[subtitle_start:].strip()
            
            is_quality = fetcher.is_high_quality_subtitle(subtitle_content)
            status = "✅ 高质量" if is_quality else "❌ 低质量"
            
            print(f"结果: {status} | 字符数: {len(subtitle_content)} | 耗时: {elapsed:.1f}s")
            return True
        else:
            print(f"结果: ❌ 无字幕内容 | 耗时: {elapsed:.1f}s")
            return False
            
    except Exception as e:
        print(f"结果: ❌ 异常 - {str(e)}")
        return False

async def main():
    """主函数"""
    test_urls = [
        "https://www.bilibili.com/video/BV1vwLnziEwZ",  # 测试视频
    ]
    
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    print("🚀 B站字幕获取快速测试")
    print("=" * 50)
    
    success_count = 0
    for i, url in enumerate(test_urls, 1):
        if await quick_test(url):
            success_count += 1
        if i < len(test_urls):
            print()
    
    print("=" * 50)
    print(f"📊 测试完成: {success_count}/{len(test_urls)} 成功")

if __name__ == "__main__":
    asyncio.run(main()) 