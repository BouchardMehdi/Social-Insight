from fastapi import APIRouter, Depends

from app.api.dependencies import get_nlp_analyzer, get_workspace_context
from app.schemas.auth import WorkspaceContext
from app.schemas.nlp import AnalyzeRequest, AnalyzeResponse
from app.services.nlp import NLPAnalyzer

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(
    payload: AnalyzeRequest,
    _: WorkspaceContext = Depends(get_workspace_context),
    analyzer: NLPAnalyzer = Depends(get_nlp_analyzer),
) -> AnalyzeResponse:
    return analyzer.analyze(payload.text)
