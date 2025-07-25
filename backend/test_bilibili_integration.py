#!/usr/bin/env python3
"""
B站视频集成测试脚本
测试URL解析和内容获取的完整流程
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.content_resolver import ContentResolver
from app.services.content_fetcher.service import ContentFetcherService
from app.utils.logger import logger

class BilibiliIntegrationTester:
    """B站视频集成测试器"""
    
    def __init__(self):
        self.resolver = ContentResolver()
        self.fetcher_service = ContentFetcherService()
        
    async def test_url_parsing(self, test_urls):
        """测试URL解析功能"""
        print("🔍 测试URL解析功能...")
        print("=" * 60)
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n测试 {i}: {url}")
            try:
                result = await self.resolver.resolve(url)
                if result:
                    platform, parsed_url, original_url = result
                    print(f"  ✅ 解析成功:")
                    print(f"     平台: {platform}")
                    print(f"     解析后URL: {parsed_url}")
                    print(f"     原始URL: {original_url}")
                else:
                    print(f"  ❌ 解析失败: 未找到合适的解析器")
            except Exception as e:
                print(f"  ❌ 解析异常: {str(e)}")
        
    async def test_content_fetching(self, test_url):
        """测试内容获取功能"""
        print(f"\n📥 测试内容获取功能...")
        print("=" * 60)
        
        try:
            # 先解析URL
            print(f"🔗 测试URL: {test_url}")
            resolve_result = await self.resolver.resolve(test_url)
            
            if not resolve_result:
                print("❌ URL解析失败，无法继续测试内容获取")
                return
            
            platform, parsed_url, original_url = resolve_result
            print(f"✅ URL解析成功: {platform} - {parsed_url}")
            
            # 获取视频信息
            print(f"\n📺 获取视频信息...")
            video_info = await self.fetcher_service.get_video_info(parsed_url)
            
            if video_info:
                print(f"✅ 视频信息获取成功:")
                print(f"   标题: {video_info.title}")
                print(f"   作者: {video_info.author.get('name', '未知')}")
                print(f"   平台: {video_info.author.get('platform', '未知')}")
                print(f"   频道: {video_info.article.channel if video_info.article else '未知'}")
                print(f"   字幕长度: {len(video_info.description)} 字符")
                if video_info.description:
                    preview = video_info.description[:200] + "..." if len(video_info.description) > 200 else video_info.description
                    print(f"   字幕预览: {preview}")
            else:
                print("❌ 视频信息获取失败")
                
            # 获取完整内容
            print(f"\n📄 获取完整内容...")
            content = await self.fetcher_service.fetch_content(parsed_url)
            
            if content:
                print(f"✅ 内容获取成功:")
                print(f"   内容长度: {len(content)} 字符")
                content_preview = content[:300] + "..." if len(content) > 300 else content
                print(f"   内容预览:\n{content_preview}")
            else:
                print("❌ 内容获取失败")
                
        except Exception as e:
            print(f"❌ 内容获取测试异常: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """主函数"""
    print("🚀 B站视频集成测试")
    print("=" * 80)
    
    tester = BilibiliIntegrationTester()
    
    # 测试用的URL列表
    test_urls = [
        "https://www.bilibili.com/video/BV1sWobYuEa6",          # 标准BV号
    ]
    
    # 测试URL解析
    await tester.test_url_parsing(test_urls)
    
    # 测试内容获取(使用第一个有效URL)
    await tester.test_content_fetching("https://www.bilibili.com/video/BV1sWobYuEa6")
    
    print(f"\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(main()) 