from __future__ import annotations

import logging

from azure.ai.projects import AIProjectClient
from azure.identity import get_bearer_token_provider
from openai import OpenAI

from app.core.auth import build_credential
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AzureAIProjectService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_response(self, prompt: str) -> str:
        self.settings.validate_runtime()
        credential = build_credential(self.settings)
        logger.info("Using Azure auth mode: %s", self.settings.azure_auth_mode)
        project = AIProjectClient(
            endpoint=self.settings.project_endpoint,
            credential=credential,
        )
        openai_client = self._build_openai_client(project, credential)
        response = openai_client.responses.create(
            model=self.settings.model_deployment_name,
            input=prompt,
        )
        return response.output_text

    def _build_openai_client(self, project: AIProjectClient, credential) -> OpenAI:
        get_openai_client = getattr(project, "get_openai_client", None)
        if callable(get_openai_client):
            return get_openai_client()

        logger.warning(
            "AIProjectClient.get_openai_client() is unavailable in the installed azure-ai-projects package. "
            "Falling back to a direct OpenAI client."
        )
        token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")
        base_url = f"{self.settings.project_endpoint.rstrip('/')}/openai/v1/"
        access_token = token_provider()
        return OpenAI(
            base_url=base_url,
            api_key=access_token,
        )
