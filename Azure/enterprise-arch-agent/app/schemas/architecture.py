from __future__ import annotations

from pydantic import BaseModel, Field


class ArchitectureRequest(BaseModel):
    prompt: str = Field(..., min_length=10, description="Architecture use case or problem statement")
    cloud_provider: str | None = Field(default=None, description="Preferred cloud platform")


class AnalyzeResponse(BaseModel):
    result: str
    cloud_provider: str
    detected_domains: str
    tools_and_technologies: list[str] = Field(default_factory=list)
    suggested_azure_services: list[str]
    drawio_xml: str
    pptx_base64: str
    pptx_preview_svg: str
    memory_record_id: str | None = None
    memory_backend: str | None = None
    prior_recommendations: list[str] = Field(default_factory=list)
    reusable_patterns: list[str] = Field(default_factory=list)


class ArchitectureAnalysis(BaseModel):
    cloud_provider: str
    cloud_specific_guidance: list[str] = Field(default_factory=list)
    detected_domains: str
    tools_and_technologies: list[str] = Field(default_factory=list)
    suggested_azure_services: list[str]
    integration_guidance: str


class MemoryRecord(BaseModel):
    id: str
    partition_key: str
    created_at: str
    version: str
    request_prompt: str
    cloud_provider: str | None = None
    result: str
    detected_domains: str
    tools_and_technologies: list[str] = Field(default_factory=list)
    suggested_azure_services: list[str]
    drawio_xml: str
    pptx_base64: str | None = None
    reusable_patterns: list[str]
    prior_recommendation_summary: str


class ArchitectureDetectionResponse(BaseModel):
    cloud_provider: str | None = None
    cloud_specific_guidance: list[str] = Field(default_factory=list)
    detected_domains: list[str] = Field(default_factory=list)
    tools_and_technologies: list[str] = Field(default_factory=list)
    suggested_azure_services: list[str] = Field(default_factory=list)
    integration_guidance: list[str] = Field(default_factory=list)


class MemoryContext(BaseModel):
    backend: str = "none"
    prior_recommendations: list[str] = Field(default_factory=list)
    reusable_patterns: list[str] = Field(default_factory=list)
