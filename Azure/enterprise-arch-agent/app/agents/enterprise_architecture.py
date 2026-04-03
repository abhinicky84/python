from __future__ import annotations

import logging

from app.domain.architecture_analysis import build_architecture_context
from app.prompts.system import ARCHITECTURE_COVERAGE_CHECKLIST, SYSTEM_PROMPT
from app.schemas.architecture import AnalyzeResponse, ArchitectureAnalysis, MemoryContext
from app.services.azure_ai_project import AzureAIProjectService
from app.services.diagram_generator import DiagramGenerator
from app.services.memory_store import BaseMemoryStore, build_memory_store

logger = logging.getLogger(__name__)


class EnterpriseArchitectureAgent:
    def __init__(
        self,
        ai_project_service: AzureAIProjectService | None = None,
        diagram_generator: DiagramGenerator | None = None,
        memory_store: BaseMemoryStore | None = None,
    ) -> None:
        self.ai_project_service = ai_project_service or AzureAIProjectService()
        self.diagram_generator = diagram_generator or DiagramGenerator()
        self.memory_store = memory_store or build_memory_store()

    def analyze(self, user_input: str, cloud_provider: str | None = None) -> AnalyzeResponse:
        logger.info("Generating architecture response.")
        try:
            analysis = self.ai_project_service.detect_architecture_context(user_input, cloud_provider)
        except Exception as exc:
            logger.warning("LLM-based architecture detection failed, using fallback heuristics: %s", exc)
            analysis = build_architecture_context(user_input, cloud_provider)
        try:
            memory_context = self.memory_store.recall(user_input, analysis)
        except Exception as exc:
            logger.warning("Memory recall failed: %s", exc)
            memory_context = MemoryContext()
        enriched_prompt = self._build_enriched_prompt(user_input, analysis, memory_context)
        print(
            "\n===== FINAL PROMPT SENT TO LLM =====\n"
            f"{enriched_prompt}\n"
            "===== END FINAL PROMPT =====\n",
            flush=True,
        )
        response_text = self.ai_project_service.generate_response(
            prompt=enriched_prompt,
        )
        drawio_xml, pptx_base64, pptx_preview_svg = self.diagram_generator.generate(
            user_input=user_input,
            model_response=response_text,
            analysis=analysis,
        )
        response = AnalyzeResponse(
            result=response_text,
            cloud_provider=analysis.cloud_provider,
            detected_domains=analysis.detected_domains,
            tools_and_technologies=analysis.tools_and_technologies,
            suggested_azure_services=analysis.suggested_azure_services,
            drawio_xml=drawio_xml,
            pptx_base64=pptx_base64,
            pptx_preview_svg=pptx_preview_svg,
            memory_backend=memory_context.backend,
            prior_recommendations=memory_context.prior_recommendations,
            reusable_patterns=memory_context.reusable_patterns,
        )
        try:
            response.memory_record_id = self.memory_store.save(user_input, analysis, response)
        except Exception as exc:
            logger.warning("Memory persistence failed: %s", exc)
        return response

    def _build_enriched_prompt(
        self,
        user_input: str,
        analysis: ArchitectureAnalysis,
        memory_context,
    ) -> str:
        memory_section = "No prior memory available."
        if memory_context.prior_recommendations or memory_context.reusable_patterns:
            memory_section = f"""
Prior recommendations:
{chr(10).join(f"- {item}" for item in memory_context.prior_recommendations) or "- None"}

Reusable patterns from memory:
{chr(10).join(f"- {item}" for item in memory_context.reusable_patterns) or "- None"}
""".strip()
        return f"""
System guidance:
{SYSTEM_PROMPT}

Architecture coverage checklist:
{ARCHITECTURE_COVERAGE_CHECKLIST}

Preferred cloud environment:
{analysis.cloud_provider}

Cloud-specific guidance:
{chr(10).join(f"- {item}" for item in analysis.cloud_specific_guidance) if analysis.cloud_specific_guidance else "- None identified"}

Detected architecture domains:
{analysis.detected_domains}

Suggested cloud services:
{", ".join(analysis.suggested_azure_services) if analysis.suggested_azure_services else "None identified yet"}

Detected tools and technologies:
{", ".join(analysis.tools_and_technologies) if analysis.tools_and_technologies else "None identified"}

Recommended integration guidance:
{analysis.integration_guidance}

Agent memory:
{memory_section}

User request:
{user_input}
""".strip()
