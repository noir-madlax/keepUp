#!/usr/bin/env python3
"""
平台对比测试脚本
对比YouTube和B站的处理流程，验证数据结构一致性
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.content_resolver import ContentResolver
from app.services.content_fetcher.service import ContentFetcherService

class PlatformComparisonTester:
    """平台对比测试器"""
    
    def __init__(self):
        self.resolver = ContentResolver()
        self.fetcher_service = ContentFetcherService()
        
    async def test_platform_workflow(self, platform_name: str, test_url: str):
        """测试单个平台的完整workflow"""
        print(f"\n🧪 测试 {platform_name} 平台处理流程")
        print("=" * 60)
        
        try:
            # 1. URL解析阶段
            print(f"1. URL解析: {test_url}")
            resolve_result = await self.resolver.resolve(test_url)
            
            if not resolve_result:
                print(f"   ❌ URL解析失败")
                return None
            
            platform, parsed_url, original_url = resolve_result
            print(f"   ✅ 平台识别: {platform}")
            print(f"   ✅ 标准化URL: {parsed_url}")
            
            # 2. 视频信息获取阶段
            print(f"\n2. 视频信息获取")
            video_info = await self.fetcher_service.get_video_info(parsed_url)
            
            if not video_info:
                print(f"   ❌ 视频信息获取失败")
                return None
            
            print(f"   ✅ 标题: {video_info.title}")
            print(f"   ✅ 作者: {video_info.author.get('name', '未知')}")
            print(f"   ✅ 平台: {video_info.author.get('platform', '未知')}")
            print(f"   ✅ 频道: {video_info.article.channel if video_info.article else '未知'}")
            
            # 3. 内容获取阶段
            print(f"\n3. 字幕内容获取")
            content = await self.fetcher_service.fetch_content(parsed_url)
            
            if not content:
                print(f"   ❌ 内容获取失败")
                return None
            
            print(f"   ✅ 内容长度: {len(content)} 字符")
            
            # 4. 数据结构验证
            print(f"\n4. 数据结构验证")
            self.validate_video_info_structure(video_info, platform_name)
            
            return {
                "platform": platform,
                "video_info": video_info,
                "content": content,
                "parsed_url": parsed_url
            }
            
        except Exception as e:
            print(f"   ❌ 处理异常: {str(e)}")
            return None
    
    def validate_video_info_structure(self, video_info, platform_name):
        """验证VideoInfo数据结构"""
        required_fields = ['title', 'description', 'author', 'article']
        
        for field in required_fields:
            if hasattr(video_info, field):
                value = getattr(video_info, field)
                if value is not None:
                    print(f"   ✅ {field}: 存在 ({'dict' if isinstance(value, dict) else type(value).__name__})")
                else:
                    print(f"   ⚠️ {field}: None")
            else:
                print(f"   ❌ {field}: 缺失")
        
        # 验证author字段结构
        if hasattr(video_info, 'author') and isinstance(video_info.author, dict):
            author_fields = ['name', 'icon', 'platform']
            for field in author_fields:
                if field in video_info.author:
                    print(f"     ✅ author.{field}: {video_info.author[field]}")
                else:
                    print(f"     ⚠️ author.{field}: 缺失")
        
        # 验证article字段结构
        if hasattr(video_info, 'article') and video_info.article:
            article_fields = ['title', 'content', 'channel', 'tags', 'original_link']
            for field in article_fields:
                if hasattr(video_info.article, field):
                    value = getattr(video_info.article, field)
                    print(f"     ✅ article.{field}: 存在 ({type(value).__name__})")
                else:
                    print(f"     ⚠️ article.{field}: 缺失")

async def main():
    """主函数"""
    print("🚀 平台处理流程对比测试")
    print("=" * 80)
    
    tester = PlatformComparisonTester()
    
    test_cases = [
        ("B站", "https://www.bilibili.com/video/BV1sWobYuEa6"),
        # ("YouTube", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),  # 如果需要测试YouTube
    ]
    
    results = {}
    
    for platform_name, test_url in test_cases:
        result = await tester.test_platform_workflow(platform_name, test_url)
        results[platform_name] = result
    
    # 对比分析
    print(f"\n📊 对比分析")
    print("=" * 60)
    
    for platform_name, result in results.items():
        if result:
            print(f"✅ {platform_name} 平台: 处理成功")
            print(f"   - 平台标识: {result['platform']}")
            print(f"   - 视频标题: {result['video_info'].title}")
            print(f"   - 作者信息: {result['video_info'].author.get('name')}")
            print(f"   - 频道标识: {result['video_info'].article.channel}")
            print(f"   - 内容长度: {len(result['content'])} 字符")
        else:
            print(f"❌ {platform_name} 平台: 处理失败")
    
    print(f"\n🎉 对比测试完成！")

if __name__ == "__main__":
    asyncio.run(main()) 