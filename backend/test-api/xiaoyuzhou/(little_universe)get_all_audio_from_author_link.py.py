import os
import re
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class PodcastDownloader:
    """下载小宇宙播客的所有单集音频（稳健选择器 + macOS 路径）"""

    def __init__(self):
        self.base_url = "https://www.xiaoyuzhoufm.com"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
            )
        }
        # 统一在 test-api 目录下输出
        self.base_dir = \
            "/Users/rigel/project/keepup-v2/backend/test-api"
        self.save_dir = os.path.join(self.base_dir, "output", "xiaoyuzhou_audio")

    def sanitize_filename(self, filename: str) -> str:
        """清理文件名中的特殊字符"""
        return re.sub(r"[\\/:*?\"<>|（）【】#&\s]", "_", filename)

    def get_episode_links(self, url: str) -> list[str]:
        """获取播客页中的所有单集链接（基于 /episode/ 路径匹配，更稳健）"""
        print("正在获取播客列表...")
        try:
            resp = requests.get(url, headers=self.headers, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            episodes: list[str] = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if isinstance(href, str) and href.startswith("/episode/"):
                    full_url = urljoin(self.base_url, href)
                    episodes.append(full_url)

            # 去重
            episodes = list(dict.fromkeys(episodes))
            print(f"找到 {len(episodes)} 个播客单集")
            return episodes
        except Exception as e:
            print(f"获取播客列表失败: {e}")
            return []

    def download_file(self, url: str, filename: str, total_size: int | None):
        """流式下载文件并显示进度条。total_size 可能为 None。"""
        with requests.get(url, headers=self.headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                with tqdm(
                    total=total_size or 0,
                    unit="B",
                    unit_scale=True,
                    desc=os.path.basename(filename),
                    disable=total_size is None,
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            f.write(chunk)
                            if total_size:
                                pbar.update(len(chunk))

    def process_episode(self, episode_url: str):
        """处理单个播客集：解析标题与音频直链并下载到本地"""
        try:
            resp = requests.get(episode_url, headers=self.headers, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            title_meta = soup.find("meta", property="og:title")
            if not title_meta:
                print(f"无法获取标题: {episode_url}")
                return
            title = self.sanitize_filename(title_meta.get("content", ""))

            audio_meta = soup.find("meta", property="og:audio")
            if not audio_meta:
                print(f"无法获取音频链接: {episode_url}")
                return
            audio_url = audio_meta.get("content", "")

            ext = ".m4a" if audio_url.endswith(".m4a") else ".mp3"
            filename = os.path.join(self.save_dir, f"{title}{ext}")

            if os.path.exists(filename):
                print(f"文件已存在，跳过: {title}")
                return

            # 获取文件大小（可能为空）
            try:
                head = requests.head(audio_url, headers=self.headers, timeout=15)
                file_size = int(head.headers.get("content-length", "0")) or None
            except Exception:
                file_size = None

            print(f"开始下载: {title}")
            self.download_file(audio_url, filename, file_size)
            print(f"下载完成: {title}")
        except Exception as e:
            print(f"下载失败 {episode_url}: {e}")

    def start_download(self, url: str):
        """开始下载流程"""
        os.makedirs(self.save_dir, exist_ok=True)

        episodes = self.get_episode_links(url)
        if not episodes:
            return

        with ThreadPoolExecutor(max_workers=3) as executor:
            list(executor.map(self.process_episode, episodes))


if __name__ == "__main__":
    downloader = PodcastDownloader()
    url = input("请输入小宇宙播客列表页面URL: ")
    downloader.start_download(url)
