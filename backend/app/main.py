import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api import query, privacy, recommendations, dashboard, plan, workload, demo, assistant
from app.services.demo_service import demo_service

app = FastAPI(title="PrivDB Optimizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(privacy.router, prefix="/api/privacy", tags=["Privacy"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(plan.router, prefix="/api/plan", tags=["Plan"])
app.include_router(workload.router, prefix="/api/workload", tags=["Workload"])
app.include_router(demo.router, prefix="/api/demo", tags=["Demo"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["Assistant"])

@app.on_event("startup")
async def startup_event():
    # Initialize demo data on startup
    demo_service.init_demo_data()

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
