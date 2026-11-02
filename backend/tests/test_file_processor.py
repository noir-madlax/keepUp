import asyncio
import os
import unittest
from io import BytesIO
from unittest.mock import patch

from ebooklib import epub

from app.utils import file_processor
from app.utils.file_processor import (
    MAX_UPLOAD_SIZE,
    SUPPORTED_EXTENSIONS,
    process_file_content,
)


def _build_epub(chapters, spine_order=None) -> bytes:
    """构造一个最小 EPUB：chapters 为 [(文件名, 标题, body_html)]"""
    book = epub.EpubBook()
    book.set_identifier('test-book')
    book.set_title('测试书')
    book.set_language('zh')

    items = []
    for file_name, title, body in chapters:
        item = epub.EpubHtml(title=title, file_name=file_name, lang='zh')
        item.content = f'<html><body>{body}</body></html>'
        book.add_item(item)
        items.append(item)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    ordered = [items[i] for i in spine_order] if spine_order else items
    book.spine = ['nav'] + ordered

    buffer = BytesIO()
    epub.write_epub(buffer, book)
    return buffer.getvalue()


def _run(coro):
    return asyncio.run(coro)


class FileProcessorTest(unittest.TestCase):
    def test_supported_extensions_and_limit(self):
        self.assertIn('epub', SUPPORTED_EXTENSIONS)
        self.assertIn('azw3', SUPPORTED_EXTENSIONS)
        self.assertEqual(MAX_UPLOAD_SIZE, 50 * 1024 * 1024)

    def test_epub_follows_spine_order(self):
        data = _build_epub(
            [('c1.xhtml', '一', '<p>第一章内容</p>'), ('c2.xhtml', '二', '<p>第二章内容</p>')],
            spine_order=[1, 0],
        )
        text = _run(process_file_content(data, 'epub'))
        self.assertLess(text.index('第二章内容'), text.index('第一章内容'))

    def test_epub_inline_tags_do_not_break_chinese(self):
        data = _build_epub([('c1.xhtml', '一', '<p>稳定币是<span>一种</span><a href="#">加密货币</a>。</p><p>下一段</p>')])
        text = _run(process_file_content(data, 'epub'))
        self.assertIn('稳定币是一种加密货币。', text)
        self.assertIn('下一段', text)
        # 两个段落之间应换行
        self.assertIn('。\n', text)

    def test_epub_drops_script_style_and_nav(self):
        data = _build_epub([('c1.xhtml', '一', '<style>.a{color:red}</style><script>var x=1</script><p>正文</p>')])
        text = _run(process_file_content(data, 'epub'))
        self.assertIn('正文', text)
        self.assertNotIn('color:red', text)
        self.assertNotIn('var x', text)

    def test_epub_without_text_raises(self):
        data = _build_epub([('c1.xhtml', '一', '<p>   </p>')])
        with self.assertRaises(Exception) as ctx:
            _run(process_file_content(data, 'epub'))
        self.assertIn('文件内容为空', str(ctx.exception))

    def test_invalid_epub_raises_friendly_error(self):
        with self.assertRaises(Exception) as ctx:
            _run(process_file_content(b'not an epub', 'epub'))
        self.assertIn('文件处理失败', str(ctx.exception))

    def test_azw3_kf8_reuses_epub_extraction(self):
        epub_bytes = _build_epub([('c1.xhtml', '一', '<p>来自AZW3的内容</p>')])

        def fake_extract(path):
            out_dir = os.path.dirname(path) + '_out'
            os.makedirs(out_dir, exist_ok=True)
            epub_path = os.path.join(out_dir, 'book.epub')
            with open(epub_path, 'wb') as f:
                f.write(epub_bytes)
            return out_dir, epub_path

        with patch('mobi.extract', side_effect=fake_extract):
            text = _run(process_file_content(b'fake azw3 bytes', 'azw3'))
        self.assertIn('来自AZW3的内容', text)

    def test_azw3_mobi6_html_fallback(self):
        def fake_extract(path):
            out_dir = os.path.dirname(path) + '_out'
            os.makedirs(out_dir, exist_ok=True)
            html_path = os.path.join(out_dir, 'book.html')
            with open(html_path, 'wb') as f:
                f.write('<html><body><p>老式MOBI正文</p></body></html>'.encode('utf-8'))
            return out_dir, html_path

        with patch('mobi.extract', side_effect=fake_extract):
            text = _run(process_file_content(b'fake mobi bytes', 'azw3'))
        self.assertIn('老式MOBI正文', text)

    def test_txt_and_unsupported(self):
        self.assertEqual(_run(process_file_content('你好'.encode('utf-8'), 'txt')), '你好')
        with self.assertRaises(Exception) as ctx:
            _run(process_file_content(b'x', 'exe'))
        self.assertIn('不支持的文件类型', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
