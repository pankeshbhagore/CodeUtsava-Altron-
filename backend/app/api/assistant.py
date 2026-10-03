from fastapi import APIRouter
from app.models.schemas import AssistantRequest
from app.services.analysis_service import analysis_service

router = APIRouter()

@router.post("/ask")
def ask_assistant(request: AssistantRequest):
    return analysis_service.ask_assistant(request.question)
