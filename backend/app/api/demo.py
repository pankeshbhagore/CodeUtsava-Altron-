from fastapi import APIRouter
from app.services.analysis_service import analysis_service
from app.services.demo_service import demo_service

router = APIRouter()

@router.post("/reset")
def reset_demo():
    # Reset the analysis service state
    analysis_service.recommendations.clear()
    analysis_service.simulations.clear()
    analysis_service.audit_log.clear()
    analysis_service.queries_analyzed = 0
    analysis_service.recent_queries.clear()
    return {"status": "reset", "message": "Demo state has been reset"}

@router.get("/slow-queries")
def get_slow_queries():
    return {"queries": demo_service.get_slow_queries()}

@router.get("/explain-plans")
def get_explain_plans():
    return {"plans": demo_service.get_explain_plans()}

@router.post("/analyze-all")
def analyze_all_demo():
    results = []
    for q in demo_service.get_slow_queries():
        try:
            result = analysis_service.analyze_query(q["sql"])
            results.append({
                "query": q["description"],
                "anonymized_sql": result.get("anonymized_sql", ""),
                "recommendations_count": len(result.get("recommendations", [])),
            })
        except Exception as e:
            results.append({"query": q.get("description", "unknown"), "error": str(e)})
    return {"analyzed": len(results), "results": results}
