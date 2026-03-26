from __future__ import annotations

from pydantic import BaseModel, Field


class ArchitectureRequest(BaseModel):
    prompt: str = Field(..., min_length=10, description="Architecture use case or problem statement")


class AnalyzeResponse(BaseModel):
    result: str
    detected_domains: str
    suggested_azure_services: list[str]


class ArchitectureAnalysis(BaseModel):
    detected_domains: str
    suggested_azure_services: list[str]
    integration_guidance: str
