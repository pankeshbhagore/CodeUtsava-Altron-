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
    return {"recommendations": analysis_service.get_all_recommendations(), "simulations": list(analysis_service.simulations.values())[::-1]}

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
@router.get("/{rec_id}/export-gitops")
def export_gitops(rec_id: str):
    rec = analysis_service.get_recommendation(rec_id)
    if not rec:
        return {"error": "Recommendation not found"}
        
    import time
    version = str(int(time.time()))
    up_sql = rec.get("create_sql", "")
    down_sql = rec.get("rollback_sql", "")
    table = rec.get("table", "unknown")
    
    return {
        "flyway": {
            "up_filename": f"V{version}__optimize_{table}.sql",
            "up_content": up_sql,
            "down_filename": f"U{version}__optimize_{table}.sql",
            "down_content": down_sql
        },
        "liquibase": {
            "filename": f"db.changelog-{version}.xml",
            "content": f'''<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                   http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.3.xsd">
    <changeSet id="{version}-1" author="privdb-optimizer">
        <sql>{up_sql}</sql>
        <rollback>
            <sql>{down_sql}</sql>
        </rollback>
    </changeSet>
</databaseChangeLog>'''
        }
    }
