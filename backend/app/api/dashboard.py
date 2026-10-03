from fastapi import APIRouter
from app.services.analysis_service import analysis_service

router = APIRouter()

@router.get("/metrics")
def get_metrics():
    return analysis_service.get_dashboard_metrics()

@router.get("/health")
def get_health():
    metrics = analysis_service.get_dashboard_metrics()
    return {
        "status": "healthy",
        "health_score": metrics["health_score"],
        "privacy_status": metrics["privacy_status"],
        "raw_data_exposed": 0,
    }
@router.get("/recent-queries")
def get_recent_queries():
    import psycopg2
    import os
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/privdb')
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute('SELECT raw_query, execution_time_ms, timestamp FROM query_logs ORDER BY timestamp DESC LIMIT 5;')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        queries = []
        for r in rows:
            queries.append({
                "sql": r[0][:100] + '...' if len(r[0]) > 100 else r[0],
                "time_ms": float(r[1]),
                "timestamp": str(r[2])
            })
        return {"queries": queries}
    except Exception as e:
        return {"queries": [], "error": str(e)}
