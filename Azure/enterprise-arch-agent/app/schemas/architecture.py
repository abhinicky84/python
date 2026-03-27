from __future__ import annotations

from pydantic import BaseModel, Field


class ArchitectureRequest(BaseModel):
    prompt: str = Field(..., min_length=10, description="Architecture use case or problem statement")


class AnalyzeResponse(BaseModel):
    result: str
    detected_domains: str
    suggested_azure_services: list[str]
    mermaid_diagram: str
    drawio_xml: str
    memory_record_id: str | None = None
    memory_backend: str | None = None
    prior_recommendations: list[str] = Field(default_factory=list)
    reusable_patterns: list[str] = Field(default_factory=list)


class ArchitectureAnalysis(BaseModel):
    detected_domains: str
    suggested_azure_services: list[str]
    integration_guidance: str


class MemoryRecord(BaseModel):
    id: str
    partition_key: str
    created_at: str
    version: str
    request_prompt: str
    result: str
    detected_domains: str
    suggested_azure_services: list[str]
    mermaid_diagram: str
    drawio_xml: str
    reusable_patterns: list[str]
    prior_recommendation_summary: str


class MemoryContext(BaseModel):
    backend: str = "none"
    prior_recommendations: list[str] = Field(default_factory=list)
    reusable_patterns: list[str] = Field(default_factory=list)
