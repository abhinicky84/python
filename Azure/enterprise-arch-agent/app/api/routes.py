from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse

from app.agents.enterprise_architecture import EnterpriseArchitectureAgent
from app.core.config import get_settings
from app.schemas.architecture import AnalyzeResponse, ArchitectureRequest
from app.ui import INDEX_HTML

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()
agent = EnterpriseArchitectureAgent()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML)


@router.get("/health")
def health() -> dict[str, str]:
    status_value = "ok"
    if not settings.project_endpoint or not settings.model_deployment_name:
        status_value = "degraded"
    return {"status": status_value, "environment": settings.app_env}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: ArchitectureRequest) -> AnalyzeResponse:
    try:
        return agent.analyze(req.prompt)
    except ValueError as exc:
        logger.warning("Request could not be processed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent configuration is incomplete or the request is invalid.",
        ) from exc
    except Exception as exc:
        logger.exception("Unhandled analyze error.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Architecture analysis failed.",
        ) from exc
