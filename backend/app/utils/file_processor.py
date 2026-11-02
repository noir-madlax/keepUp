import asyncio
import os
import re
import shutil
import tempfile
from io import BytesIO

import docx
from PyPDF2 import PdfReader

# 上传文件支持的扩展名（前端 accept / 校验需与此保持一致）
SUPPORTED_EXTENSIONS = ('pdf', 'doc', 'docx', 'txt', 'epub', 'azw3')

# 上传文件大小上限（字节）
MAX_UPLOAD_SIZE = 50 * 1024 * 1024

# 解析 EPUB 时视为"块级"的标签，块结束处补换行，避免中文被行内标签（span/a 等）切断
_BLOCK_TAGS = [
    'p', 'div', 'section', 'article', 'li', 'tr', 'blockquote',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'dt', 'dd', 'figcaption',
]


def clean_text(text: str) -> str:
    """清理文本中的特殊字符

    Args:
        text: 原始文本

    Returns:
        str: 清理后的文本
    """
    # 移除null字符
    text = text.replace('\x00', '')

    # 移除控制字符，但保留换行和制表符
    text = ''.join(char for char in text if char == '\n' or char == '\t' or (ord(char) >= 32 and ord(char) != 127))

    # 规范化换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 移除多余的空行
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()


def _html_to_text(html_bytes: bytes) -> str:
    """把一个 (X)HTML 章节转成纯文本，保留段落换行，丢弃脚本/样式/图片"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_bytes, 'lxml')
    for tag in soup(['script', 'style', 'head', 'img', 'svg']):
        tag.decompose()
    for br in soup.find_all('br'):
        br.replace_with('\n')
    for tag in soup.find_all(_BLOCK_TAGS):
        tag.append('\n')
    return soup.get_text()


def _is_nav(item) -> bool:
    """是否为目录导航页（EPUB3 nav），其内容只有目录，不属于正文"""
    from ebooklib import epub

    return isinstance(item, epub.EpubNav) or 'nav' in (getattr(item, 'properties', None) or [])


def _extract_epub(source) -> str:
    """提取 EPUB 正文文本（按 spine 阅读顺序）

    Args:
        source: 文件路径或 BytesIO
    """
    from ebooklib import ITEM_DOCUMENT, epub

    book = epub.read_epub(source, options={'ignore_ncx': True})

    chapters = []
    seen = set()
    for idref, _linear in book.spine:
        item = book.get_item_with_id(idref)
        if item is None or item.get_type() != ITEM_DOCUMENT or item.get_id() in seen or _is_nav(item):
            continue
        seen.add(item.get_id())
        chapters.append(_html_to_text(item.get_content()))

    # 个别 EPUB 的 spine 不完整，兜底按文档顺序补齐未出现的章节
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        if item.get_id() in seen or _is_nav(item):
            continue
        seen.add(item.get_id())
        chapters.append(_html_to_text(item.get_content()))

    return '\n\n'.join(chapters)


def _extract_azw3(content: bytes) -> str:
    """提取 AZW3(KF8)/MOBI 正文文本

    mobi 库会把 KF8 解包为标准 EPUB，MOBI6 解包为 HTML；这里复用对应的提取逻辑。
    """
    import mobi

    tmp_dir = tempfile.mkdtemp(prefix='keepup_azw3_')
    try:
        src_path = os.path.join(tmp_dir, 'book.azw3')
        with open(src_path, 'wb') as f:
            f.write(content)

        extracted_dir, extracted_path = mobi.extract(src_path)
        try:
            if extracted_path.lower().endswith('.epub'):
                return _extract_epub(extracted_path)
            with open(extracted_path, 'rb') as f:
                return _html_to_text(f.read())
        finally:
            shutil.rmtree(extracted_dir, ignore_errors=True)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _extract_text(content: bytes, file_extension: str) -> str:
    """同步提取文本（CPU 密集，需放到线程中执行）"""
    if file_extension == 'pdf':
        pdf = PdfReader(BytesIO(content))
        return '\n'.join((page.extract_text() or '') for page in pdf.pages)

    if file_extension in ('doc', 'docx'):
        document = docx.Document(BytesIO(content))
        return '\n'.join(paragraph.text for paragraph in document.paragraphs)

    if file_extension == 'txt':
        return content.decode('utf-8', errors='ignore')

    if file_extension == 'epub':
        return _extract_epub(BytesIO(content))

    if file_extension == 'azw3':
        return _extract_azw3(content)

    raise ValueError(f"不支持的文件类型: {file_extension}")


async def process_file_content(content: bytes, file_extension: str) -> str:
    """处理文件内容

    Args:
        content: 文件内容
        file_extension: 文件扩展名

    Returns:
        str: 提取的文本内容
    """
    try:
        # 大文件解析耗时较长，放入线程池避免阻塞事件循环
        text = await asyncio.to_thread(_extract_text, content, file_extension)

        cleaned_text = clean_text(text)

        if not cleaned_text:
            raise ValueError("文件内容为空")

        return cleaned_text

    except Exception as e:
        raise Exception(f"文件处理失败: {str(e)}")
