import json
from fastapi import APIRouter, HTTPException
from app.models.request import ParseRequest
from app.models.coze import CozeResponse, CozeArticleContent, ArticleCreate
from app.services.coze import CozeService
from app.services.supabase import SupabaseService
from app.utils.logger import logger
from app.config import settings

router = APIRouter(prefix="")

async def process_coze_result(article_content: CozeArticleContent, request_id: int, url: str) -> None:
    """处理 Coze 返回结果并保存到数据库"""
    try:
        # 从背景信息中提取标题
        background_lines = article_content.key0_background.split('\n')
        title = next((line.replace('### 视频标题：', '') for line in background_lines if '视频标题：' in line), '')
        
        # 创建文章数据
        article_data = ArticleCreate(
            title=title,
            content=article_content.key5_summary,
            original_link=url,
            tags=["视频"],
            channel="YouTube"
        )
        
        # 保存文章
        article_result = await SupabaseService.create_article(article_data)
        
        # 准备小节数据
        sections = [
            {"section_type": "背景", "content": article_content.key0_background},
            {"section_type": "人物介绍", "content": article_content.key1_people},
            {"section_type": "为什么要读", "content": article_content.key2_why},
            {"section_type": "核心观点", "content": article_content.key3_core},
            {"section_type": "名词解释", "content": article_content.key4_word},
            {"section_type": "整体总结", "content": article_content.key5_summary},
            {"section_type": "分段提纲", "content": article_content.key6_part_title},
            {"section_type": "分段详述", "content": article_content.key7_part_detail},
            {"section_type": "QA环节", "content": article_content.key8_qa},
            {"section_type": "金句", "content": article_content.key9_golden},
            {"section_type": "未总结内容", "content": article_content.key10_exclude}
        ]
        
        # 保存小节
        await SupabaseService.create_article_sections(article_result['id'], sections)
        
        # 更新请求状态
        await SupabaseService.update_status(request_id, "processed")
        
    except Exception as e:
        logger.error(f"保存数据失败: {str(e)}", exc_info=True)
        await SupabaseService.update_status(request_id, "failed", str(e))
        raise

async def call_coze_and_parse(url: str, content: str) -> CozeArticleContent:
    """调用 Coze API 并解析结果"""
    try:
        if settings.USE_MOCK_COZE:
            logger.info("使用 mock 数据")
            # mock 数据
            mock_result = {
                "code": 0,
                "cost": "0",
                "data": "{\"key0_background\":\"## 背景\\n\\n### 视频标题：Tech Policy After the 2024 Election with Marc Andreessen and Ben Horowitz\\n...}",
                "debug_url": "https://www.coze.com/work_flow?execute_id=7437390534404161554&space_id=7436304106135814199&workflow_id=7437089946567114770",
                "msg": "Success",
                "token": 65006
            }
            coze_response = CozeResponse(**mock_result)
        else:
            logger.info("调用真实 Coze API")
            # 调用真实的 Coze API
            coze_service = CozeService()
            result = await coze_service.parse_content(url, content)
            coze_response = CozeResponse(**result)
            
        # 解析返回结果
        article_content_dict = json.loads(coze_response.data)
        article_content = CozeArticleContent(**article_content_dict)
        
        return article_content
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Coze API 调用失败: {str(e)}", exc_info=True)
        raise

@router.post("/parse")
async def parse_content(request: ParseRequest):
    try:
        logger.info(f"收到解析请求: ID={request.id}, URL={request.url}")
        
        # 调用 Coze API 并解析结果
        article_content = await call_coze_and_parse(request.url, request.content)
        
        # 处理结果并保存到数据库
        await process_coze_result(article_content, request.id, request.url)
        
        return {"success": True, "message": "解析完成"}
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        await SupabaseService.update_status(
            request.id, 
            "failed", 
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) 