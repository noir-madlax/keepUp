import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.request import ParseRequest
from app.models.coze import CozeResponse, CozeArticleContent, ArticleCreate
from app.services.coze import CozeService
from app.repositories.supabase import SupabaseService
from app.utils.logger import logger
from app.config import settings
from app.services.content_polisher import ContentPolisherService
from app.services.content_detailer import ContentDetailerService
from app.utils.decorators import retry_decorator
router = APIRouter(prefix="")

# 添加请求模型
class PolishRequest(BaseModel):
    article_id: int
    language: str
    content: Optional[str] = None

class DetailRequest(BaseModel):
    article_id: int
    language: str
    content: Optional[str] = None

async def process_coze_result(coze_response: CozeResponse, request_id: int, url: str, article: ArticleCreate, language: str) -> None:
    """处理 Coze 返回结果并保存到数据库"""
    try:


        # 解析返回结果
        article_content_dict = json.loads(coze_response.data)
        article_content = CozeArticleContent(**article_content_dict)

        # 从背景信息中提取标题
        background_lines = article_content.key0_background.split('\n')
        title = next((line.replace('### 视频标题：', '') for line in background_lines if '视频标题：' in line), '')
        
        # 准备小节数据 - 确保每个小节都有语言标识
        sections = []
        
        # 定义所有可能的小节
        section_mappings = [
            ("背景", article_content.key0_background),
            # ("总结", article_content.key2_why),
            ("分段提纲", article_content.key6_part_title),
            ("结构图", article_content.key11_map),
            ("要点总结", article_content.key19_Takeaways),
            ("思维导图", article_content.key17_xmind),
            ("人物介绍", article_content.key1_people),
            ("核心观点", article_content.key3_core),
            ("名词解释", article_content.key4_word),
            ("总结", article_content.key5_summary),
            ("QA环节", article_content.key8_qa),
            ("金句", article_content.key9_golden),
            ("未总结内容", article_content.key10_exclude),
            ("彩蛋", article_content.key18_EasterEgg),
            ("分段详述", article_content.key7_part_detail),
            ("典型案例", article_content.key20_case)
        ]
        
        # 只添加有内容的小节
        for section_type, content in section_mappings:
            if content and content.strip():  # 检查内容是否为空或只包含空白字符
                sections.append({
                    "section_type": section_type,
                    "content": content,
                    "language": language
                })
        
        # 保存小节
        if sections:  # 只在有小节时保存
            await SupabaseService.create_article_sections(article['id'], sections)
        
    except Exception as e:
        logger.error(f"保存数据失败: {str(e)}", exc_info=True)
        await SupabaseService.update_status(request_id, "failed", str(e))
        raise

@retry_decorator()
async def call_coze_and_parse(url: str, content: str, chapters: str, workflow_id: str,request_id: int) -> CozeArticleContent:
    """调用 Coze API 并解析结果"""

    coze_response = None

    try:
        if settings.USE_MOCK_COZE:
            logger.info("使用 mock 数据")
            # mock 数据
            mock_result = {
                "code": 0,
                "cost": "0",
                "data": "{\"key0_background\":\"## 背景\\n\\n### 视频标题：Tech Policy After the 2024 Election with Marc Andreessen and Ben Horowitz\\n### 主要内容：马克·安德森和本·霍洛维茨讨论2024年美国大选后的科技政策展望\\n### 视频网站：YouTube\\n### 视频频道：a16z\\n### 视频日期：2024年1月\\n### 视频类型：访谈、深度见解\\n### 视频时长：58分钟（约13000字）\\n### 视频参与人：Marc Andreessen, Ben Horowitz\\n#### 识别视中的语音发言者：支持\\n#### 视频链接：https://www.youtube.com/watch?v=g4jWb-0nj44\",\"key10_exclude\":\"本总结涵盖了视频的主要内容,包括核心观点、重要话题和关键讨论。视频中可能还包含一些具体的政策细节、个人轶事或技术细节未被完全涵盖。建议对特定领域感兴趣的观众可以观看完整视频以获取更多信息。总结覆盖率约为85-90%。\\n\\n原视频链接: https://www.youtube.com/watch?v=g4jWb-0nj44\\n```\",\"key1_people\":\"Marc Andreessen和Ben Horowitz是知名风险投资公司Andreessen Horowitz (a16z)的联合创始人。他们在科技行业有着深厚的背景和广泛的影响力。Marc以创立Netscape浏览器而闻名,Ben则曾是成功的科技企业家和经营者。两人在硅谷和科技政策领域都有很高的声誉。\",\"key2_why\":\"这个视频提供了对2024年美国大选后科技政策可能走向的深刻洞察。对于以下人群来说,这个视频有重要意义:\\n\\n1. 行业趋势观察者:了解美国科技政策的潜在变化如何影响全球科技格局。\\n\\n2. AI工程师:了解新政府对AI发展和监管的态度,为技术发展方向提供指导。\\n\\n3. AI产品经理:洞悉政策变化可能带来的新机遇和挑战,调整产品策略。\\n\\n4. Marketing专业人员:了解政策变化可能对科技产品推广和市场策略的影响。\\n\\n5. 财务和投资专家:评估政策变化对科技公司估值和投资环境的潜在影响。\\n\\n(Marc Andreessen: 我们必须赢。在金融科技、加密货币、AI、生物科技、国防科技等领域,我们必须建立最好的技术,解决最紧迫的问题。)\",\"key3_core\":\"1. 科技政策是一级重要议题,关系到美国的国家实力和全球地位。(Marc Andreessen: 科技政策是一个一级重要的议题,和其他任何政治议题一样重要或更重要。)\\n\\n2. 新政府对科技行业更加开放,愿意与行业对话。(Ben Horowitz: 这届政府最好的消息是,他们愿意开放对话,愿意讨论这些问题。)\\n\\n3. 加密货币和金融科技行业有望迎来更友好的政策环境。(Marc Andreessen: 看看已经发生的变化,真是令人震惊。每个加密项目的价值都上涨了。)\\n\\n4. AI政策需要平衡创新和监管,避免过度限制。(Ben Horowitz: 我们需要赢得AI竞赛,但也要确保它不会违反现有法律。)\\n\\n5. 国防科技,特别是无人机技术,将成为未来军事实力的关键。(Marc Andreessen: 无人机技术是自马镫发明以来最重要的军事技术进步。)\",\"key4_word\":\"1. 加密货币(Cryptocurrency): 基于区块技术的数字或虚拟货币。(Marc Andreessen: 加密货币为创作者提供了一种新的商业模式,让他们能够获得98%而不是2%的收入。)\\n\\n2. 金融科技(Fintech): 利用科技创新来提供金融服务的行业。(Ben Horowitz: 金融科技公司遭受了严重的打压,但现在有望重新起飞。)\\n\\n3. AI(人工智能): 模拟人类智能的计算机系统。(Marc Andreessen: AI政策需要从\\\"我们必须赢\\\"的角度出发,而不是过度限制。)\\n\\n4. 国防科技: 应用于军事和国防领域的先进技术。(Ben Horowitz: 无人机技术正在彻底改变战争的性质。)\\n\\n5. CHIPS Act: 美国政府推出的支持半导体产业的法案。(Marc Andreessen: CHIPS Act承诺的资金大部分还没有发放出去。)\",\"key5_summary\":\"这次访谈主要讨论2024年美国大选后可能出现的科技政策变化。Marc和Ben认为,新政府对科技行业更加开放,这可能带来一系列积极变化。他们特别强调了加密货币、金融科技、AI和国防科技等领域的政策前景。两位嘉宾认为,科技政策对美国的全球竞争力至关重要,呼吁政府采取更有利于创新的态度,同时平衡监管需求。他们还讨论了能源政策、芯片制造等相关议题,强调了这些领域与科技发的密切关系。\",\"key6_part_title\":\"1. 0:00-10:00 介绍过去四年科技政策的问题\\n   - 讨论了过去政府对加密货币和金融科技行业的打压\\n   - 批评了\\\"去银行化\\\"等做法对创新的阻碍\\n\\n2. 10:00-20:00 分析新政府可能带来的变化\\n   - 预期加密货币和金融科技行业将迎来更友好的政策环境\\n   - 讨论了新政府可能采取的开放态度\\n\\n3. 20:00-30:00 探讨AI政策的挑战\\n   - 强调了AI在国家竞争中的重要性\\n   - 讨论了如何平衡创新和监管\\n\\n4. 30:00-40:00 分析国防科技,特别是无人机技术的重要性\\n   - 讨论了无人机技术对现代战争的革命性影响\\n   - 强调了美国在这一领域需要加快步伐\\n\\n5. 40:00-50:00 探讨能源政策与科技发展的系\\n   - 分析了能源政策对AI发展的影响\\n   - 讨论了核能等清洁能源技术的潜力\\n\\n6. 50:00-58:00 总结和展望\\n   - 重申科技政策对美国未来的关键作用\\n   - 呼吁新政府采取更积极的科技政策立场\",\"key7_part_detail\":\"\",\"key8_qa\":\"Q1: 为什么Marc和Ben认为科技政策是一级重要的议题?\\nA1: 他们认为科技政策直接关系到美国的国家实力、经济竞争力和全球地位。技术领先对于维持美国在经济、军事等方面的优势至关重要。\\n\\nQ2: 新政府对科技行业的态度有何不同?\\nA2: 根据Marc和Ben的观点,新政府似乎更愿意与科技行业对话,采取更开放的态度。这可能会带来更有利于创新的政策环境。\\n\\nQ3: 在加密货币和金融科技领域,可能会有什么变化?\\nA3: 他们预期这些领域将迎来更友好的政策环境。过去的一些限制性措施可能会被放松,有利于行创新和发展。\\n\\nQ4: 关于AI政策,Marc和Ben有什么看法?\\nA4: 他们强调需要平衡创新和监管。认为政策应该从\\\"我们必须赢\\\"的角度出发,避免过度限制阻碍美国在AI领域的竞争力。\\n\\nQ5: 为什么他们特别强调了国防科技,尤其是无人机技术?\\nA5: 他们认为无人机技术正在彻底改变现代战争的性质,是自马镫发明以来最重要的军事技术进步。美国需要在这一领域保持领先以维护国家安全。\",\"key9_golden\":\"1. \\\"我们必须赢。在金融科技、加密货币、AI、生物科技、国防科技等领域,我们必须建立最好的技术,解决最紧迫的问题。\\\" - Marc Andreessen (3:25)\\n\\n2. \\\"科技政策是一个一级重要的议题,和其他任何政治议题一样重要或更重要。\\\" - Marc Andreessen (15:40)\\n\\n3. \\\"如果你通过技术镜头看20世纪,美国在三个方面取得了胜利:技术、经济和军事。这三者是相互关联的。\\\" - Ben Horowitz (25:10)\\n\\n4. \\\"无人机技术是自马镫发明以来最重要的军事技术进步。\\\" - Marc Andreessen (42:30)\\n\\n5. \\\"我们需要让建设者去建设。这不仅会推动AI发展,还会推动许多其他领域。\\\" - Ben Horowitz (50:15)\",\"video_author_name\":\"：a16z\",\"video_date\":\"\",\"video_link\":\"https://www.youtube.com/watch?v=g4jWb-0nj44\",\"video_original_content\":\"暂无\"}",
                "debug_url": "https://www.coze.com/work_flow?execute_id=7437390534404161554&space_id=7436304106135814199&workflow_id=7437089946567114770",
                "msg": "Success",
                "token": 65006
            }
            coze_response = CozeResponse(**mock_result)
        else:
            logger.info("调用真实 Coze API")
            # 调用真实的 Coze API
            coze_service = CozeService()
            result = await coze_service.parse_content(url, content, chapters, workflow_id)
            coze_response = CozeResponse(**result)
            

        # 验证响应数据
        if coze_response is None:
            raise ValueError("未能获取到 Coze 响应")
        
        article_content_dict = json.loads(coze_response.data)
        article_content = CozeArticleContent(**article_content_dict)
        if not article_content.key2_why:
            logger.error(f"解析结果中缺少总结: {article_content_dict}")
            raise ValueError("解析结果中缺少总结")
        
        return coze_response
        
    except json.JSONDecodeError | ValueError as e:
        logger.error(f"JSON 解析失败: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"Coze API 调用失败: {str(e)}", exc_info=True)
        raise e
    finally:
        # 首先将 CozeResponse 转换为字典，再更新到数据库
        coze_response_dict = {
            "code": coze_response.code,
            "cost": coze_response.cost,
            "data": coze_response.data,
            "debug_url": coze_response.debug_url,
            "msg": coze_response.msg,
            "token": coze_response.token
        }
        await SupabaseService.update_parsed_content(request_id, coze_response_dict)

@router.post("/parse")
async def parse_content(request: ParseRequest):
    try:
        logger.info(f"收到解析请求: ID={request.id}, URL={request.url}")
        
        # 调用 Coze API 并解析结果
        coze_response = await call_coze_and_parse(request.url, request.content, request.chapters, request.workflow_id)
        
        # 处理结果并保存到数据库
        await process_coze_result(coze_response, request.id, request.url, request.article, request.language)
        
        return {"success": True, "message": "解析完成"}
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        await SupabaseService.update_status(
            request.id, 
            "failed", 
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) 

@router.post("/polish")
async def debug_save_polished(request: PolishRequest):
    """调试接口: 直接保存润色内容
    
    Args:
        request: 包含 article_id, language 和可选的 content 的请求对象
    """
    try:
        logger.info(f"调试接口 - 开始处理: article_id={request.article_id}, language={request.language}")
        
        if not request.content:
            # 1. 获取文章URL
            client = SupabaseService.get_client()
            article_result = client.table("keep_articles").select("original_link").eq("id", request.article_id).single().execute()
            
            if not article_result.data:
                raise HTTPException(status_code=404, detail=f"未找到文章: {request.article_id}")
                
            url = article_result.data.get("original_link")
            if not url:
                raise HTTPException(status_code=400, detail="文章缺少原始链接")
            
            # 2. 通过URL获取请求记录
            request_result = client.table("keep_article_requests").select("content").eq("url", url).single().execute()
            
            if not request_result.data:
                raise HTTPException(status_code=404, detail=f"未找到对应的请求记录: {url}")
                
            content = request_result.data.get("content")
            if not content:
                raise HTTPException(status_code=400, detail="请求记录缺少内容")
        else:
            content = request.content
        
        logger.info(f"获取到原文内容,长度: {len(content)}")
        
        # 保存润色内容
        await ContentPolisherService.process_article_content(
            article_id=request.article_id,
            original_content=content,
            language=request.language,
            workflow_id=settings.COZE_POLISH_WORKFLOW_ID_EN
        )
        
        return {
            "success": True,
            "message": "内容保存成功",
            "data": {
                "article_id": request.article_id,
                "language": request.language,
                "content_length": len(content)
            }
        }
        
    except Exception as e:
        error_msg = f"Failed to save polished content: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg) 
    

@router.post("/detail")
async def debug_save_detail(request: DetailRequest):
    """调试接口: 直接保存分段详述内容
    
    Args:
        request: 包含 article_id, language 和可选的 content 的请求对象
    """
    try:
        logger.info(f"调试接口 - 开始处理: article_id={request.article_id}, language={request.language}")
        
        if not request.content:
            # 1. 获取文章URL
            client = SupabaseService.get_client()
            article_result = client.table("keep_articles").select("original_link").eq("id", request.article_id).single().execute()
            
            if not article_result.data:
                raise HTTPException(status_code=404, detail=f"未找到文章: {request.article_id}")
                
            url = article_result.data.get("original_link")
            if not url:
                raise HTTPException(status_code=400, detail="文章缺少原始链接")
            
            # 2. 通过URL获取请求记录
            request_result = client.table("keep_article_requests").select("chapters").eq("url", url).single().execute()
            
            if not request_result.data:
                raise HTTPException(status_code=404, detail=f"未找到对应的请求记录: {url}")
                
            content = request_result.data.get("chapters")
            if not content:
                raise HTTPException(status_code=400, detail="请求记录缺少章节信息")
        else:
            content = request.content
        
        logger.info(f"获取到原文内容,长度: {len(content)}")
        
        # 保存分段详述内容
        await ContentDetailerService.process_article_content(
            article_id=request.article_id,
            chapters=request_result.data.get("chapters"),
            language=request.language,
            workflow_id=settings.COZE_DETAILED_WORKFLOW_ID_EN
        )
        
        return {
            "success": True,
            "message": "内容保存成功",
            "data": {
                "article_id": request.article_id,
                "language": request.language,
                "content_length": len(content)
            }
        }
        
    except Exception as e:
        error_msg = f"Failed to save detailed content: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg) 
    

@router.get("/polish/parse/{request_id}")
async def test_polish_content(request_id: int):
    """测试解析润色内容
    
    Args:
        request_id: 请求ID
        
    Returns:
        str: 解析后的内容
    """
    try:
        logger.info(f"开始测试解析润色内容: request_id={request_id}")
        
        # 从数据库获取润色内容
        article_request = await SupabaseService.get_article_request(request_id)
        if not article_request:
            raise HTTPException(status_code=404, detail="未找到请求记录")
            
        # 获取英文润色内容
        polished_content_en = article_request.get("polished_content_en")
        if not polished_content_en:
            raise HTTPException(status_code=404, detail="未找到英文润色内容")

        # 将JSON字符串解析为Python对象
        try:
            polished_content_array = json.loads(polished_content_en)
            if not isinstance(polished_content_array, list):
                polished_content_array = [polished_content_array]
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"润色内容JSON解析失败: {str(e)}")
    

        # 解析润色内容
        parsed_content = await ContentPolisherService.parse_polished_content(
            polished_content_array
        )
        
        return {
            "success": True,
            "content": parsed_content
        }
        
    except Exception as e:
        logger.error(f"测试解析润色内容失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

    