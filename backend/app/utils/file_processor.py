from PyPDF2 import PdfReader
import docx
import re

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

async def process_file_content(content: bytes, file_extension: str) -> str:
    """处理文件内容
    
    Args:
        content: 文件内容
        file_extension: 文件扩展名
        
    Returns:
        str: 提取的文本内容
    """
    try:
        if file_extension == 'pdf':
            # 处理PDF文件
            from io import BytesIO
            pdf = PdfReader(BytesIO(content))
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
                
        elif file_extension in ['doc', 'docx']:
            # 处理Word文件
            from io import BytesIO
            doc = docx.Document(BytesIO(content))
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
        elif file_extension == 'txt':
            # 处理文本文件
            text = content.decode('utf-8', errors='ignore')
            
        else:
            raise ValueError(f"不支持的文件类型: {file_extension}")
        
        # 清理提取的文本
        cleaned_text = clean_text(text)
        
        if not cleaned_text:
            raise ValueError("文件内容为空")
            
        return cleaned_text
        
    except Exception as e:
        raise Exception(f"文件处理失败: {str(e)}") 