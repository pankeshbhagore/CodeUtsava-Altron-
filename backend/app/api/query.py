from fastapi import APIRouter
from app.models.schemas import QueryAnalysisRequest
from app.services.analysis_service import analysis_service

router = APIRouter()


@router.post("/analyze")
def analyze_query(request: QueryAnalysisRequest):
    result = analysis_service.analyze_query(request.sql, request.execution_stats)
    return result


@router.post("/normalize")
def normalize_query(request: QueryAnalysisRequest):
    result = analysis_service.analyze_query(request.sql, request.execution_stats)
    return {
        "normalized_sql": result.get("normalized_sql", ""),
        "query_fingerprint": result.get("query_fingerprint", ""),
        "anonymized_sql": result.get("anonymized_sql", ""),
    }
