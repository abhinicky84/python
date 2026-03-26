from __future__ import annotations

from app.agents.enterprise_architecture import EnterpriseArchitectureAgent


def generate_architecture_response(user_input: str) -> tuple[str, str, list[str]]:
    response = EnterpriseArchitectureAgent().analyze(user_input)
    return response.result, response.detected_domains, response.suggested_azure_services
