from io import BytesIO
import PyPDF2
from docx import Document

async def process_file_content(content: bytes, extension: str) -> str:
    """处理不同类型的文件内容
    
    Args:
        content: 文件二进制内容
        extension: 文件扩展名
        
    Returns:
        str: 提取的文本内容
    """
    try:
        if extension == 'pdf':
            return extract_pdf_content(content)
        elif extension in ['doc', 'docx']:
            return extract_docx_content(content)
        elif extension == 'txt':
            return content.decode('utf-8')
        else:
            return ''
    except Exception as e:
        logger.error(f"文件内容提取失败: {str(e)}")
        return ''

def extract_pdf_content(content: bytes) -> str:
    """从PDF提取文本"""
    pdf_file = BytesIO(content)
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'
    return text

def extract_docx_content(content: bytes) -> str:
    """从DOCX提取文本"""
    docx_file = BytesIO(content)
    doc = Document(docx_file)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs]) 