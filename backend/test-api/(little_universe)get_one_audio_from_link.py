import os
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def sanitize_filename(title: str) -> str:
    invalid_chars = [":", "\\", "/", "&", "(", ")", "#", "【", "】", " "]
    filename = title
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename


def get_audio_from_url(url: str) -> tuple[str, str]:
    """解析小宇宙单集页面，返回 (title, audio_url)。不进行本地下载。"""
    try:
        print(f"Fetching webpage: {url}")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title_meta = soup.find("meta", property="og:title")
        if not title_meta:
            raise RuntimeError("Title meta tag not found")
        title = title_meta.get("content", "")
        print(f"Found title: {title}")

        audio_meta = soup.find("meta", property="og:audio")
        if not audio_meta:
            raise RuntimeError("Audio meta tag not found")
        audio_url = audio_meta.get("content", "")
        print(f"Found audio URL: {audio_url}")

        return title, audio_url
    except Exception as e:
        print(f"Error processing URL: {e}")
        raise


if __name__ == "__main__":
    url = input("Please enter the URL of the podcast: ")
    title, audio = get_audio_from_url(url)
    print("Parsed:", sanitize_filename(title), audio)
