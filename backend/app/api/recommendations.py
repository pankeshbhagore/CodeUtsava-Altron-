from fastapi import APIRouter
from app.models.schemas import RecommendationGenerateRequest
from app.services.analysis_service import analysis_service

router = APIRouter()

@router.post("/generate")
def generate_recommendations(request: RecommendationGenerateRequest):
    recs = analysis_service.generate_recommendations(request.sql, request.execution_stats, request.table_stats)
    return {"recommendations": recs}

@router.get("/")
def get_all_recommendations():
    return {"recommendations": analysis_service.get_all_recommendations(), "simulations": list(analysis_service.simulations.values())}

@router.get("/{rec_id}")
def get_recommendation(rec_id: str):
    rec = analysis_service.get_recommendation(rec_id)
    if rec is None:
        return {"error": "Not found"}
    return rec

@router.post("/{rec_id}/simulate")
def simulate_recommendation(rec_id: str):
    return analysis_service.simulate_recommendation(rec_id)

@router.post("/{rec_id}/approve")
def approve_recommendation(rec_id: str):
    return analysis_service.approve_recommendation(rec_id)

@router.post("/{rec_id}/reject")
def reject_recommendation(rec_id: str):
    return analysis_service.reject_recommendation(rec_id)
