from __future__ import annotations

from app.agents.enterprise_architecture import EnterpriseArchitectureAgent


def generate_architecture_response(user_input: str, cloud_provider: str | None = None) -> tuple[str, str, list[str]]:
    response = EnterpriseArchitectureAgent().analyze(user_input, cloud_provider)
    return response.result, response.detected_domains, response.suggested_azure_services
