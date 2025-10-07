"""
企业相关API端点
提供企业信息处理、搜索、分析等功能
"""

from infrastructure.utils.datetime_utils import now_utc
import logging
from typing import Dict, Any
import json
from infrastructure.database.repositories.cache_repository import CompanyCacheRepository



from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from api.v1.schemas.company import (
    CompanyRequest,
    CompanyResponse,
    ProgressiveCompanyRequest,
    ProgressiveStageData,
    UpdateCompanyRequest,
    UpdateCompanyResponse,
    ChainLeaderUpdateRequest,
    ChainLeaderUpdateResponse,
    ErrorResponse
)
from api.v1.dependencies import (
    get_enterprise_service,
    get_request_context
)
from domain.services.enterprise_service import EnterpriseService

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/company", tags=["company"])

@router.get("/config")
async def get_company_config():
    """
    返回前端所需的公司相关配置（包括缓存开关）
    """
    try:
        from config.settings import get_settings
        s = get_settings()
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "status": "success",
                "data": {
                    "cache_enabled": getattr(s, "cache", None).enabled if getattr(s, "cache", None) else True
                },
                "timestamp": now_utc()
            })
        )
    except Exception as e:
        logger.error(f"获取公司配置失败: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({
                "status": "error",
                "message": "服务器内部错误"
            })
        )

@router.post("/cache/purge")
async def purge_company_cache(
    request: Dict[str, str]
):
    """
    清理指定公司名的缓存（按标准化键）
    请求体: {"company_name": "青岛啤酒股份有限公司"}
    """
    try:
        company_name = (request.get("company_name") or "").strip()
        if not company_name:
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder({
                    "status": "error",
                    "message": "company_name不能为空"
                })
            )

        from infrastructure.utils.text_processor import company_name_extractor
        cache_key = company_name_extractor.normalize_company_name(company_name)
        cache_repo = CompanyCacheRepository()
        ok = cache_repo.purge_cache(cache_key)

        return JSONResponse(
            status_code=200 if ok else 500,
            content=jsonable_encoder({
                "status": "success" if ok else "error",
                "message": "缓存已删除" if ok else "删除缓存失败",
                "data": {
                    "company_name": company_name,
                    "cache_key": cache_key
                }
            })
        )
    except Exception as e:
        logger.error(f"缓存清理异常: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({
                "status": "error",
                "message": "服务器内部错误"
            })
        )


@router.post("/process", response_model=CompanyResponse)
async def process_company_info(
    request: CompanyRequest,
    background_tasks: BackgroundTasks,
    enterprise_service: EnterpriseService = Depends(get_enterprise_service),
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    处理企业信息查询请求

    接收用户输入的企业查询文本，返回完整的企业信息分析结果
    """
    request_logger = request_context["request_logger"]
    request_id = request_context["request_id"]

    try:
        logger.info(f"[{request_id}] 开始处理企业信息查询: {request.input_text[:50]}...")

        # 调用企业服务处理查询
        result = enterprise_service.process_company_info(request.input_text)

        if result.get("status") == "error":
            logger.error(f"[{request_id}] 企业信息处理失败: {result.get('message')}")
            background_tasks.add_task(request_logger.log_request_end, 400)

            error_payload = CompanyResponse(
                status="error",
                message=result.get("message", "企业信息处理失败"),
                data=None,
                timestamp=now_utc()
            )
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder(error_payload)
            )

        # 构建成功响应
        response_payload = CompanyResponse(
            status="success",
            message="企业信息处理完成",
            data=result.get("data"),
            timestamp=now_utc()
        )

        logger.info(f"[{request_id}] 企业信息处理完成: {result.get('data', {}).get('company_name', 'Unknown')}")
        background_tasks.add_task(request_logger.log_request_end, 200)

        return response_payload

    except Exception as e:
        logger.error(f"[{request_id}] 企业信息处理异常: {str(e)}", exc_info=True)
        background_tasks.add_task(request_logger.log_request_end, 500)

        error_payload = ErrorResponse(
            message="服务器内部错误",
            error_code="INTERNAL_ERROR",
            timestamp=now_utc()
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(error_payload)
        )


@router.post("/process/progressive", response_model=ProgressiveStageData)
async def process_company_progressive(
    request: ProgressiveCompanyRequest,
    background_tasks: BackgroundTasks,
    enterprise_service: EnterpriseService = Depends(get_enterprise_service),
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    渐进式企业信息处理

    提供分阶段的企业信息处理，适用于需要实时反馈的场景
    """
    request_logger = request_context["request_logger"]
    request_id = request_context["request_id"]

    try:
        logger.info(f"[{request_id}] 开始渐进式企业信息处理: {request.input_text[:50]}...")

        # 阶段1: 提取公司名称
        stage_data = {
            "stage": 1,
            "status": "processing",
            "message": "正在提取公司名称...",
            "data": {},
            "timestamp": now_utc()
        }

        name_extraction_result = enterprise_service.search_service.extract_company_name_from_input(request.input_text)

        if name_extraction_result['status'] == 'error':
            stage_data["status"] = "error"
            stage_data["message"] = f"公司名称提取失败: {name_extraction_result.get('message', '未知错误')}"
            stage_data["timestamp"] = now_utc()
            background_tasks.add_task(request_logger.log_request_end, 400)
            return ProgressiveStageData(**stage_data)

        company_name = name_extraction_result['name']
        stage_data["data"]["company_name"] = company_name
        stage_data["message"] = f"成功提取公司名称: {company_name}"
        stage_data["timestamp"] = now_utc()

        # 阶段1.5：缓存命中检查（三个月内有效，缓存键标准化）；支持禁用
        if not getattr(request, "disable_cache", False):
            try:
                from infrastructure.utils.text_processor import company_name_extractor
                cache_repo = CompanyCacheRepository()
                cache_key = company_name_extractor.normalize_company_name(company_name or "")
                cache_row = cache_repo.get_valid_cache(cache_key)
                if cache_row and cache_row.get("payload"):
                    cached_final = json.loads(cache_row["payload"])
                    stage_data["stage"] = 4
                    stage_data["status"] = "completed"
                    stage_data["message"] = "命中缓存，直接返回结果"
                    stage_data["data"]["final_result"] = cached_final
                    stage_data["timestamp"] = now_utc()
                    background_tasks.add_task(request_logger.log_request_end, 200)
                    return ProgressiveStageData(**stage_data)
            except Exception as e:
                logger.error(f"缓存查询失败: {e}")

        # 阶段2: 搜索本地数据库
        stage_data["stage"] = 2
        stage_data["status"] = "processing"
        stage_data["message"] = "正在搜索本地数据库..."
        stage_data["timestamp"] = now_utc()

        local_search_result = enterprise_service.search_local_database(company_name)
        stage_data["data"]["local_result"] = local_search_result

        if local_search_result['found']:
            stage_data["message"] = f"在本地数据库中找到企业信息"
        else:
            stage_data["message"] = "本地数据库中未找到企业信息，将使用网络搜索"
        stage_data["timestamp"] = now_utc()

        # 阶段3: 轻量化完整处理（避免长时间阻塞）
        stage_data["stage"] = 3
        stage_data["status"] = "processing"
        stage_data["message"] = "正在执行轻量化企业信息处理..."
        stage_data["timestamp"] = now_utc()

        # 快速路径：仅进行公司名清洗与核心名提取，避免任何外部耗时调用
        try:
            from infrastructure.utils.text_processor import company_name_extractor
            import re
            raw_name = stage_data["data"].get("company_name", company_name)
            nn = company_name_extractor.normalize_company_name(raw_name or "")
            nn = nn.replace("企业信息-电话-公司地址-品牌网", "")
            nn = nn.replace("企业信息", "").replace("电话", "").replace("公司地址", "").replace("品牌网", "")
            nn = re.sub(r"[-—·|]+", " ", nn).strip()
            core = company_name_extractor.extract_company_name(nn)
            if isinstance(core, dict) and core.get("name"):
                core_name = core["name"].strip()
            else:
                core_name = (core or nn or raw_name).strip()
            quick_summary = f"企业名称：{core_name}。当前为快速路径结果，详细信息待后续阶段补充。"
            final_data = {
                "company_name": core_name,
                "summary": quick_summary,
                "details": {
                    "name": core_name,
                    "district_name": "",
                    "address": "",
                    "industry": "",
                    "industry_brain": "",
                    "chain_status": "",
                    "industry_chain": "",
                    "revenue_info": "暂无营收数据",
                    "company_status": "暂无排名信息",
                    "data_source": "quick_path"
                },
                "news": {"summary": "暂无最新商业资讯", "references": []}
            }

            # 如果本地数据库命中，融合本地数据
            try:
                lr = stage_data["data"].get("local_result")
                if lr and lr.get("found") and isinstance(lr.get("data"), dict):
                    db = lr["data"]
                    # 名称（仅在非空时覆盖），确保最终不为空
                    db_name = db.get("customer_name")
                    if db_name:
                        final_data["company_name"] = db_name
                    if not final_data["company_name"]:
                        final_data["company_name"] = core_name
                    final_data["details"]["name"] = final_data["company_name"]
                    # 地址（仅在非空时覆盖）
                    db_addr = db.get("address")
                    if db_addr:
                        final_data["details"]["address"] = db_addr
                    # 行业与区域（仅在非空时覆盖）
                    db_industry = db.get("industry_name")
                    if db_industry:
                        final_data["details"]["industry"] = db_industry
                    db_region = db.get("district_name")
                    if db_region:
                        final_data["details"]["district_name"] = db_region
                    # 行业脑（如有）
                    db_brain = db.get("brain_name")
                    if db_brain:
                        final_data["details"]["industry_brain"] = db_brain
                    # 链主状态（根据链主ID）
                    if db.get("chain_leader_id"):
                        final_data["details"]["chain_status"] = "链主"
                        # 标注所属产业链（如有）：优先 chain_type，其次 industry_name
                        cn = (db.get("chain_type") or db.get("industry_name") or "")
                        if cn:
                            final_data["details"]["industry_chain"] = cn
                        # 若仍为空，尝试通过链主ID查询行业名称（从链主企业表）
                        if not final_data["details"].get("industry_chain"):
                            try:
                                from infrastructure.database.repositories.enterprise_repository import EnterpriseRepository
                                er = EnterpriseRepository()
                                ent = er.find_by_id(int(db.get("chain_leader_id")))
                                if ent and getattr(ent, "industry_name", None):
                                    final_data["details"]["industry_chain"] = ent.industry_name
                            except Exception:
                                pass
                        # 若依旧为空，且存在链主企业名称，则通过名称再查一次行业名称
                        if not final_data["details"].get("industry_chain"):
                            try:
                                from infrastructure.database.repositories.enterprise_repository import EnterpriseRepository as _ER
                                _er = _ER()
                                cname = (db.get("chain_leader_name") or "").strip()
                                if cname:
                                    ent2 = _er.find_by_name(cname)
                                    if ent2 and getattr(ent2, "industry_name", None):
                                        final_data["details"]["industry_chain"] = ent2.industry_name
                            except Exception:
                                pass
                    # 若地址存在但区域为空，直接从地址中提取地区（市/区）
                    try:
                        if final_data["details"].get("address") and not final_data["details"].get("district_name"):
                            addr = final_data["details"]["address"]
                            # 简单中文地址解析：仅提取“市”
                            import re
                            m_city = re.search(r'([\u4e00-\u9fa5]{2,10})市', addr)
                            if m_city:
                                final_data["details"]["district_name"] = m_city.group(0)
                    except Exception:
                        pass
                    # 数据源标记
                    final_data["details"]["data_source"] = "local_db"
                    # 兜底修正摘要与默认字段
                    if not final_data.get("summary"):
                        final_data["summary"] = f"企业名称：{final_data['company_name']}。当前为快速路径结果，详细信息待后续阶段补充。"
                    if not final_data["details"].get("revenue_info"):
                        final_data["details"]["revenue_info"] = "暂无营收数据"
                    if not final_data["details"].get("company_status"):
                        final_data["details"]["company_status"] = "暂无排名信息"
                    if not stage_data.get("message"):
                        stage_data["message"] = "在本地数据库命中企业并完成轻量化处理"
            except Exception as e:
                logger.error(f"融合本地数据失败: {e}")

            # 联网搜索补全：在启用联网测试时，尽量填充缺失字段
            try:
                if getattr(request, "enable_network", True):
                    from infrastructure.utils.text_processor import search_result_processor, company_name_extractor
                    norm = company_name_extractor.normalize_company_name(final_data["details"].get("name", ""))
                    ns = enterprise_service.search_service.search_company_info(norm)
                    if ns.get("status") == "success":
                        data = ns.get("data", {}) or {}
                        parsed = search_result_processor.extract_company_info_from_search_results({"data": data})
                        # 地址
                        addr = (parsed.get("address") or parsed.get("details", {}).get("address") or "").strip()
                        if addr and not final_data["details"].get("address"):
                            final_data["details"]["address"] = addr
                        # 行业
                        ind = (parsed.get("industry") or parsed.get("details", {}).get("industry") or "").strip()
                        if ind and not final_data["details"].get("industry"):
                            final_data["details"]["industry"] = ind
                        # 区域
                        reg = (parsed.get("region") or parsed.get("details", {}).get("region") or "").strip()
                        if reg and not final_data["details"].get("district_name"):
                            final_data["details"]["district_name"] = reg
                        # 若仍未有区域，但有地址，尝试从地址仅提取“市”
                        try:
                            if final_data["details"].get("address") and not final_data["details"].get("district_name"):
                                a = final_data["details"]["address"]
                                m_city = re.search(r'([\u4e00-\u9fa5]{2,10})市', a)
                                if m_city:
                                    final_data["details"]["district_name"] = m_city.group(0)
                        except Exception:
                            pass
                        # 若仍未有区域，尝试从描述中仅提取“市”
                        try:
                            if not final_data["details"].get("district_name"):
                                desc = (data.get("description") or "").strip()
                                if desc:
                                    m_city = re.search(r'([\u4e00-\u9fa5]{2,10})市', desc)
                                    if m_city:
                                        final_data["details"]["district_name"] = m_city.group(0)
                        except Exception:
                            pass
                        stage_data["data"]["network_result"] = {"status": "success", "data": data}
                        # 近三年营收与企业地位（联网获取）
                        try:
                            from infrastructure.external.revenue_service import get_company_revenue_info
                            rev = get_company_revenue_info(final_data["details"].get("name", ""))
                            if rev:
                                final_data["details"]["revenue_info"] = rev or final_data["details"].get("revenue_info") or ""
                        except Exception as _:
                            # 保持降级，不阻塞流程
                            pass
                        try:
                            from infrastructure.external.ranking_service import get_company_ranking_status
                            rank = get_company_ranking_status(final_data["details"].get("name", ""), final_data["details"].get("industry", ""))
                            if rank:
                                final_data["details"]["company_status"] = rank or final_data["details"].get("company_status") or ""
                        except Exception as _:
                            pass
                        # 企业商业资讯（联网获取）：填充 news.summary 与 news.references
                        try:
                            from domain.services.analysis_service import AnalysisService
                            _as = AnalysisService()
                            _news = _as.get_company_news(final_data["details"].get("name", ""))
                            final_data["news"] = {
                                "summary": (_news or {}).get("summary", "暂无最新商业资讯"),
                                "references": (_news or {}).get("references", [])
                            }
                            # 兜底：若没有新闻或仅占位，则直接用搜索结果构建参考资料
                            try:
                                needs_fallback = False
                                if not final_data["news"]["references"]:
                                    needs_fallback = True
                                if (final_data["news"]["summary"] or "").strip() in ("", "暂无最新商业资讯"):
                                    needs_fallback = True
                                if needs_fallback:
                                    from infrastructure.external.bocha_client import search_web
                                    q = f"{final_data['details'].get('name','')} 最新 动态 新闻 资讯 公告"
                                    sr = search_web(q, count=6, summary=False) or {}
                                    items = (sr.get('results') or sr.get('data') or [])
                                    refs = []
                                    for it in items:
                                        title = (it.get('title') or it.get('name') or '').strip()
                                        url = (it.get('url') or it.get('link') or '').strip()
                                        snippet = (it.get('snippet') or it.get('summary') or '').strip()
                                        if url:
                                            refs.append({
                                                "title": title or url,
                                                "url": url,
                                                "source": it.get('source') or it.get('site') or '',
                                                "snippet": snippet
                                            })
                                    if refs:
                                        final_data["news"]["references"] = refs
                                        final_data["news"]["summary"] = f"为您找到 {len(refs)} 条相关新闻，详见下方参考资料。"
                            except Exception:
                                # 搜索兜底失败亦不阻塞
                                pass
                        except Exception:
                            # 保持降级，不阻塞流程
                            pass
            except Exception as e:
                logger.error(f"联网搜索补全失败: {e}")

            # 轻量行业推断：若行业仍为空，基于名称与地址进行推断
            try:
                if not final_data["details"].get("industry"):
                    from infrastructure.utils.text_processor import get_company_industry
                    inferred = get_company_industry(final_data["details"].get("name", ""), final_data["details"].get("address", ""))
                    if inferred:
                        final_data["details"]["industry"] = inferred
            except Exception as e:
                logger.error(f"行业推断失败: {e}")

            # 写入缓存（TTL=90天，缓存键标准化 + schema_version）；支持禁用
            if not getattr(request, "disable_cache", False):
                try:
                    from infrastructure.utils.text_processor import company_name_extractor
                    cache_repo = CompanyCacheRepository()
                    cache_key = company_name_extractor.normalize_company_name(final_data.get("company_name", ""))
                    final_data.setdefault("schema_version", "v1")
                    cache_repo.upsert_cache(cache_key, json.dumps(final_data), ttl_days=90)
                except Exception as e:
                    logger.error(f"写入缓存失败: {e}")

            # 在最终返回前规范化城市名称，修正“市市”等重复后缀
            try:
                import re as _re
                dn = (final_data.get("details", {}).get("district_name") or "").strip()
                if dn:
                    dn = _re.sub(r'(市)+$', '市', dn)
                    final_data["details"]["district_name"] = dn.strip()
            except Exception:
                pass

            # 行业大脑补全：仅本地匹配（brain_name / brain_id），未命中则显示“本城市暂无相关产业大脑”
            try:
                details = final_data.get("details", {})
                if details is not None and not (details.get("industry_brain") or "").strip():
                    # 1) 本地 brain_name
                    brain_name_local = None
                    local_payload = stage_data.get("data", {}).get("local_result", {})
                    if local_payload and local_payload.get("found") and isinstance(local_payload.get("data"), dict):
                        brain_name_local = local_payload["data"].get("brain_name") or None

                    brain_name = (brain_name_local or "").strip() if brain_name_local else ""

                    # 2) 通过 brain_id → 名称映射（仍属本地数据）
                    if not brain_name and local_payload and isinstance(local_payload.get("data"), dict):
                        brain_id = local_payload["data"].get("brain_id")
                        if brain_id:
                            try:
                                from infrastructure.database.queries import get_industry_brain_by_id
                                brain_obj = get_industry_brain_by_id(int(brain_id))
                                if isinstance(brain_obj, dict):
                                    brain_name = (brain_obj.get("brain_name") or brain_obj.get("name") or "").strip()
                            except Exception:
                                pass

                    # 仅本地匹配：未命中则设置为“本城市暂无相关产业大脑”
                    if brain_name:
                        final_data["details"]["industry_brain"] = brain_name
                    else:
                        final_data["details"]["industry_brain"] = "本城市暂无相关产业大脑"
            except Exception:
                pass

            # 最终阶段
            stage_data["stage"] = 4
            stage_data["status"] = "completed"
            stage_data["message"] = "企业信息轻量化处理完成（快速路径）"
            stage_data["data"]["final_result"] = final_data
            stage_data["timestamp"] = now_utc()
        except Exception as e:
            stage_data["status"] = "error"
            stage_data["message"] = f"快速路径异常: {str(e)}"
            stage_data["timestamp"] = now_utc()
            background_tasks.add_task(request_logger.log_request_end, 500)
            return ProgressiveStageData(**stage_data)

        logger.info(f"[{request_id}] 渐进式企业信息处理完成: {company_name}")
        background_tasks.add_task(request_logger.log_request_end, 200)

        return ProgressiveStageData(**stage_data)

    except Exception as e:
        logger.error(f"[{request_id}] 渐进式企业信息处理异常: {str(e)}", exc_info=True)
        background_tasks.add_task(request_logger.log_request_end, 500)

        error_stage = ProgressiveStageData(
            stage=1,
            status="error",
            message="服务器内部错误",
            data={},
            timestamp=now_utc()
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(error_stage)
        )


@router.post("/update", response_model=UpdateCompanyResponse)
async def update_company_info(
    request: UpdateCompanyRequest,
    background_tasks: BackgroundTasks,
    enterprise_service: EnterpriseService = Depends(get_enterprise_service),
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    更新企业信息

    允许更新本地数据库中的企业信息
    """
    request_logger = request_context["request_logger"]
    request_id = request_context["request_id"]

    try:
        logger.info(f"[{request_id}] 开始更新企业信息: Customer ID {request.customer_id}")

        # 调用企业服务更新信息
        result = enterprise_service.update_company_info(request.customer_id, request.updates)

        if result.get("status") == "error":
            logger.error(f"[{request_id}] 企业信息更新失败: {result.get('message')}")
            background_tasks.add_task(request_logger.log_request_end, 400)

            error_payload = UpdateCompanyResponse(
                status="error",
                message=result.get("message", "企业信息更新失败"),
                data=None,
                timestamp=now_utc()
            )
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder(error_payload)
            )

        # 构建成功响应
        response_data = UpdateCompanyResponse(
            status="success",
            message="企业信息更新完成",
            data=result.get("data"),
            timestamp=now_utc()
        )

        logger.info(f"[{request_id}] 企业信息更新完成: Customer ID {request.customer_id}")
        background_tasks.add_task(request_logger.log_request_end, 200)

        return response_data

    except Exception as e:
        logger.error(f"[{request_id}] 企业信息更新异常: {str(e)}", exc_info=True)
        background_tasks.add_task(request_logger.log_request_end, 500)

        error_payload = UpdateCompanyResponse(
            status="error",
            message="服务器内部错误",
            data=None,
            timestamp=now_utc()
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(error_payload)
        )


@router.post("/chain-leader/update", response_model=ChainLeaderUpdateResponse)
async def update_chain_leader_info(
    request: ChainLeaderUpdateRequest,
    background_tasks: BackgroundTasks,
    enterprise_service: EnterpriseService = Depends(get_enterprise_service),
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    更新链主企业信息

    专门用于更新链主企业的相关信息
    """
    request_logger = request_context["request_logger"]
    request_id = request_context["request_id"]

    try:
        logger.info(f"[{request_id}] 开始更新链主企业信息: {request.company_name}")

        # 调用企业服务更新链主信息
        result = enterprise_service.update_chain_leader_info(request.company_name, request.updates)

        if result.get("status") == "error":
            logger.error(f"[{request_id}] 链主企业信息更新失败: {result.get('message')}")
            background_tasks.add_task(request_logger.log_request_end, 400)

            error_payload = ChainLeaderUpdateResponse(
                status="error",
                message=result.get("message", "链主企业信息更新失败"),
                data=None,
                timestamp=now_utc()
            )
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder(error_payload)
            )

        # 构建成功响应
        response_data = ChainLeaderUpdateResponse(
            status="success",
            message="链主企业信息更新完成",
            data=result.get("data"),
            timestamp=now_utc()
        )

        logger.info(f"[{request_id}] 链主企业信息更新完成: {request.company_name}")
        background_tasks.add_task(request_logger.log_request_end, 200)

        return response_data

    except Exception as e:
        logger.error(f"[{request_id}] 链主企业信息更新异常: {str(e)}", exc_info=True)
        background_tasks.add_task(request_logger.log_request_end, 500)

        error_payload = ChainLeaderUpdateResponse(
            status="error",
            message="服务器内部错误",
            data=None,
            timestamp=now_utc()
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(error_payload)
        )


@router.get("/search", response_model=CompanyResponse)
async def search_company(
    q: str,
    background_tasks: BackgroundTasks,
    enterprise_service: EnterpriseService = Depends(get_enterprise_service),
    request_context: Dict[str, Any] = Depends(get_request_context)
):
    """
    企业搜索接口

    根据关键词搜索企业信息
    """
    request_logger = request_context["request_logger"]
    request_id = request_context["request_id"]

    try:
        logger.info(f"[{request_id}] 开始企业搜索: {q}")

        if not q or not q.strip():
            background_tasks.add_task(request_logger.log_request_end, 400)
            error_payload = CompanyResponse(
                status="error",
                message="搜索关键词不能为空",
                data=None,
                timestamp=now_utc()
            )
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder(error_payload)
            )

        # 调用企业服务进行搜索
        result = enterprise_service.process_company_info(q.strip())

        if result.get("status") == "error":
            logger.error(f"[{request_id}] 企业搜索失败: {result.get('message')}")
            background_tasks.add_task(request_logger.log_request_end, 400)

            error_payload = CompanyResponse(
                status="error",
                message=result.get("message", "企业搜索失败"),
                data=None,
                timestamp=now_utc()
            )
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder(error_payload)
            )

        # 构建成功响应
        response_data = CompanyResponse(
            status="success",
            message="企业搜索完成",
            data=result.get("data"),
            timestamp=now_utc()
        )

        logger.info(f"[{request_id}] 企业搜索完成: {result.get('data', {}).get('company_name', 'Unknown')}")
        background_tasks.add_task(request_logger.log_request_end, 200)

        return jsonable_encoder(response_data)

    except Exception as e:
        logger.error(f"[{request_id}] 企业搜索异常: {str(e)}", exc_info=True)
        background_tasks.add_task(request_logger.log_request_end, 500)

        error_payload = ErrorResponse(
            message="服务器内部错误",
            error_code="INTERNAL_ERROR",
            timestamp=now_utc()
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(error_payload)
        )
