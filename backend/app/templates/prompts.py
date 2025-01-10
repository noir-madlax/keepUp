# 基础对话提示模板
BASE_CHAT_PROMPT = """基于以下文章内容回答问题。

文章内容:
{article_content}

当前选中内容:
{mark_content}
"""

# 文章分析提示模板 暂未使用
ARTICLE_ANALYSIS_PROMPT = """请分析以下文章的主要观点和论据。

文章内容:
{article_content}

分析重点:
{focus_points}
"""

# 段落总结提示模板 暂未使用
SECTION_SUMMARY_PROMPT = """请总结以下段落的主要内容。

段落内容:
{section_content}

要求:
1. 保持简洁明了
2. 突出关键信息
3. 保留原文的核心观点
"""

# 根据不同的 mark_type 选择不同的提示模板
PROMPT_MAPPING = {
    'article': BASE_CHAT_PROMPT,
    'analysis': ARTICLE_ANALYSIS_PROMPT,
    'section': SECTION_SUMMARY_PROMPT
} 