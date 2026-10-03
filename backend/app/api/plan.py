from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import PlanAnalysisRequest
from app.services.analysis_service import analysis_service
from database.connection import get_db_connection, release_db_connection
import json

router = APIRouter()

class PlanGenerateRequest(BaseModel):
    sql: str

@router.post("/generate")
def generate_plan(request: PlanGenerateRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN (FORMAT JSON) {request.sql}")
        plan_json = cursor.fetchone()[0]
        release_db_connection(conn)
        return {"plan_json": plan_json}
    except Exception as e:
        return {"error": str(e)}

@router.post("/analyze")
def analyze_plan(request: PlanAnalysisRequest):
    if request.plan_json:
        return analysis_service.analyze_plan(request.plan_json)
    return {"error": "Please provide plan_json"}
