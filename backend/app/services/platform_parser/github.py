"""
GitHub 平台解析器

识别并解析所有 GitHub 链接，提取项目信息。
所有 GitHub 链接都会走 Deep Research 分析流程。
"""

import re
from typing import Optional, Tuple
from app.utils.logger import logger
from .base import PlatformParser


class GitHubParser(PlatformParser):
    """GitHub 项目解析器"""
    
    # GitHub URL 匹配模式
    GITHUB_PATTERNS = [
        r'github\.com/([^/]+)/([^/]+)',  # 匹配 github.com/owner/repo
        r'github\.com/([^/]+)/([^/]+)/tree/([^/]+)',  # 匹配带 branch/path
        r'github\.com/([^/]+)/([^/]+)/blob/([^/]+)',  # 匹配文件链接
    ]
    
    def can_handle(self, url: str) -> bool:
        """判断是否是 GitHub 链接"""
        url_lower = url.lower()
        return 'github.com' in url_lower
    
    async def parse(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        解析 GitHub URL
        
        Args:
            url: GitHub 项目 URL
            
        Returns:
            Optional[Tuple[str, str, str]]: (platform, parsed_url, original_url)
            - platform: "github"
            - parsed_url: 标准化后的 GitHub URL
            - original_url: 原始 URL
        """
        try:
            logger.info(f"[GitHubParser] 开始解析 GitHub URL: {url}")
            
            # 提取项目信息
            project_info = self._extract_project_info(url)
            
            if not project_info:
                logger.warning(f"[GitHubParser] 无法提取项目信息: {url}")
                return None
            
            owner, repo = project_info['owner'], project_info['repo']
            
            # 构建标准化 URL（保留原始 URL 用于分析）
            # parsed_url 使用原始 URL，因为我们需要分析完整路径
            parsed_url = url.strip()
            
            logger.info(f"[GitHubParser] 解析成功 - Owner: {owner}, Repo: {repo}")
            
            return ("github", parsed_url, url)
            
        except Exception as e:
            logger.error(f"[GitHubParser] 解析失败: {e}")
            return None
    
    def _extract_project_info(self, url: str) -> Optional[dict]:
        """
        从 URL 提取项目信息
        
        Returns:
            dict: {"owner": str, "repo": str, "path": str}
        """
        # 清理 URL
        url = url.strip()
        
        # 尝试匹配 GitHub URL
        for pattern in self.GITHUB_PATTERNS:
            match = re.search(pattern, url)
            if match:
                groups = match.groups()
                result = {
                    "owner": groups[0],
                    "repo": groups[1].split('?')[0].split('#')[0],  # 移除查询参数
                }
                # 提取额外路径信息（如分支、文件路径等）
                if len(groups) > 2:
                    result["branch"] = groups[2]
                
                return result
        
        return None
    
    @staticmethod
    def extract_project_name(url: str) -> str:
        """
        从 GitHub URL 提取项目名称，用于文章标题
        
        Args:
            url: GitHub URL
            
        Returns:
            str: 项目名称
        """
        try:
            # 提取 owner/repo
            match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
            if match:
                owner, repo = match.groups()
                repo = repo.split('?')[0].split('#')[0]
                
                # 如果 URL 包含特定路径，尝试提取更具体的名称
                if '/tree/' in url or '/blob/' in url:
                    # 提取路径中的最后一部分作为名称
                    parts = url.split('/')
                    if len(parts) > 7:  # github.com/owner/repo/tree/branch/path...
                        # 取最后一个有意义的路径部分
                        path_name = parts[-1] if parts[-1] else parts[-2]
                        if path_name and path_name not in ['tree', 'blob', 'main', 'master']:
                            return f"{path_name} (GitHub Agent 项目分析)"
                
                return f"{repo} (GitHub Agent 项目分析)"
            
            return "GitHub Agent 项目分析"
        except:
            return "GitHub Agent 项目分析"
