from fastapi import APIRouter
from app.services.analysis_service import analysis_service

router = APIRouter()

@router.get("/drift")
def get_drift():
    return analysis_service.get_workload_drift()

@router.post("/analyze")
def analyze_workload():
    return analysis_service.get_workload_drift()
