from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryAnalysisRequest(BaseModel):
    sql: str
    execution_stats: Optional[Dict[str, Any]] = None


class RecommendationGenerateRequest(BaseModel):
    sql: str
    execution_stats: Optional[Dict[str, Any]] = None
    table_stats: Optional[Dict[str, Any]] = None


class PlanAnalysisRequest(BaseModel):
    plan_json: Optional[Any] = None
    plan_text: Optional[str] = None


class AssistantRequest(BaseModel):
    question: str
