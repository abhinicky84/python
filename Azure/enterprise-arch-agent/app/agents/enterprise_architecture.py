from __future__ import annotations

import logging

from app.domain.architecture_analysis import build_architecture_context
from app.prompts.system import SYSTEM_PROMPT
from app.schemas.architecture import AnalyzeResponse, ArchitectureAnalysis
from app.services.azure_ai_project import AzureAIProjectService

logger = logging.getLogger(__name__)


class EnterpriseArchitectureAgent:
    def __init__(self, ai_project_service: AzureAIProjectService | None = None) -> None:
        self.ai_project_service = ai_project_service or AzureAIProjectService()

    def analyze(self, user_input: str) -> AnalyzeResponse:
        logger.info("Generating architecture response.")
        analysis = build_architecture_context(user_input)
        response_text = self.ai_project_service.generate_response(
            prompt=self._build_enriched_prompt(user_input, analysis),
        )
        return AnalyzeResponse(
            result=response_text,
            detected_domains=analysis.detected_domains,
            suggested_azure_services=analysis.suggested_azure_services,
        )

    def _build_enriched_prompt(self, user_input: str, analysis: ArchitectureAnalysis) -> str:
        return f"""
System guidance:
{SYSTEM_PROMPT}

Detected architecture domains:
{analysis.detected_domains}

Suggested Azure services:
{", ".join(analysis.suggested_azure_services)}

Recommended integration guidance:
{analysis.integration_guidance}

User request:
{user_input}
""".strip()
