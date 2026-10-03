from fastapi import APIRouter
from app.models.schemas import QueryAnalysisRequest
from app.services.analysis_service import analysis_service

router = APIRouter()

@router.post("/anonymize")
def anonymize_query(request: QueryAnalysisRequest):
    result = analysis_service.gateway.process(request.sql)
    return {
        "anonymized_sql": result.anonymized_sql,
        "is_safe": result.is_safe,
        "pii_detected": result.pii_scan_result.pii_found,
        "fields_masked": result.audit_entry.fields_masked,
        "anonymization_status": result.audit_entry.anonymization_status,
    }

@router.get("/audit")
def get_audit():
    return {"audit_entries": analysis_service.get_audit_trail()}

@router.get("/stats")
def get_stats():
    return analysis_service.get_privacy_stats()
