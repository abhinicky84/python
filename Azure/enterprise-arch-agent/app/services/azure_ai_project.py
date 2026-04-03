from __future__ import annotations

import json
import logging
import re

from azure.ai.projects import AIProjectClient
from azure.identity import get_bearer_token_provider
from openai import OpenAI

from app.core.auth import build_credential
from app.core.config import get_settings
from app.domain.architecture_analysis import build_cloud_specific_guidance, resolve_cloud_provider
from app.schemas.architecture import ArchitectureAnalysis, ArchitectureDetectionResponse

logger = logging.getLogger(__name__)


class AzureAIProjectService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_response(self, prompt: str) -> str:
        openai_client = self._build_project_openai_client()
        response = openai_client.responses.create(
            model=self.settings.model_deployment_name,
            input=prompt,
        )
        return response.output_text

    def detect_architecture_context(self, user_input: str, cloud_provider: str | None = None) -> ArchitectureAnalysis:
        requested_cloud = cloud_provider or "auto-detect"
        prompt = f"""
You are an enterprise architecture analyst.

Given the following user request, identify:
0. the preferred cloud environment
1. cloud-specific guidance for the target architecture
2. detected architecture domains
3. tools and technologies explicitly mentioned or strongly implied
4. suggested cloud services relevant to the scenario
5. concise integration guidance bullets

Return valid JSON only with this exact schema:
{{
  "cloud_provider": "...",
  "cloud_specific_guidance": ["...", "..."],
  "detected_domains": ["..."],
  "tools_and_technologies": ["..."],
  "suggested_azure_services": ["..."],
  "integration_guidance": ["...", "..."]
}}

Rules:
- Keep each list deduplicated.
- Allowed cloud_provider values: "Azure", "AWS", "GCP", "Hybrid / Multi-cloud".
- Respect the selected cloud if one is provided below.
- If no cloud is selected and the user request does not imply one, default cloud_provider to "Azure".
- Make cloud_specific_guidance specific to the selected or inferred cloud, technologies, and integration style in the user request.
- Do not return generic cloud guidance if the request clearly indicates a specific cloud or platform direction.
- The suggested cloud services must match the returned cloud_provider.
- Do not return Azure services for AWS or GCP scenarios.
- Do not return AWS services for Azure or GCP scenarios.
- Do not return GCP services for Azure or AWS scenarios.
- Keep detected domains business/architecture oriented.
- Include tools and technologies such as products, platforms, protocols, runtimes, and integration technologies.
- Include 5 to 10 practical services for the selected or inferred cloud when relevant.
- Keep integration guidance short and implementation-oriented.

Selected cloud:
{requested_cloud}

User request:
{user_input}
""".strip()
        openai_client = self._build_project_openai_client()
        response = openai_client.responses.create(
            model=self.settings.model_deployment_name,
            input=prompt,
        )
        payload_text = self._extract_json_payload(response.output_text)
        try:
            payload = ArchitectureDetectionResponse.model_validate(json.loads(payload_text))
        except Exception as exc:
            logger.warning("LLM architecture detection response was not valid JSON: %s", exc)
            raise ValueError("Architecture detection response could not be parsed.") from exc

        resolved_cloud = resolve_cloud_provider(
            user_input=user_input,
            selected_cloud=cloud_provider,
            detected_cloud=payload.cloud_provider or self._infer_cloud_from_services(payload.suggested_azure_services),
        )
        aligned_services = self._align_services_with_cloud(payload.suggested_azure_services, resolved_cloud)

        return ArchitectureAnalysis(
            cloud_provider=resolved_cloud,
            cloud_specific_guidance=payload.cloud_specific_guidance or build_cloud_specific_guidance(resolved_cloud, user_input),
            detected_domains=", ".join(payload.detected_domains) if payload.detected_domains else "General Enterprise Architecture",
            tools_and_technologies=payload.tools_and_technologies,
            suggested_azure_services=aligned_services,
            integration_guidance="\n".join(f"- {item}" for item in payload.integration_guidance),
        )

    def _extract_json_payload(self, value: str) -> str:
        cleaned = (value or "").strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        if cleaned.startswith("{") and cleaned.endswith("}"):
            return cleaned
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return match.group(0)
        return cleaned

    def _infer_cloud_from_services(self, services: list[str]) -> str | None:
        if not services:
            return None
        joined = " | ".join(service.casefold() for service in services)
        if any(token in joined for token in ("apigee", "google kubernetes engine", "pub/sub", "eventarc", "vertex ai", "bigquery", "cloud run", "cloud monitoring", "secret manager")):
            return "GCP"
        if any(token in joined for token in ("amazon api gateway", "amazon eks", "amazon eventbridge", "amazon cloudwatch", "aws app runner", "amazon bedrock", "amazon s3", "dynamodb")):
            return "AWS"
        if any(token in joined for token in ("azure api management", "azure kubernetes service", "azure monitor", "azure service bus", "azure event grid", "azure ai foundry", "microsoft entra")):
            return "Azure"
        return None

    def _align_services_with_cloud(self, services: list[str], cloud_provider: str) -> list[str]:
        if not services:
            return []

        normalized_cloud = cloud_provider.casefold()
        aligned: list[str] = []
        seen: set[str] = set()

        for service in services:
            translated = self._translate_service_for_cloud(service, normalized_cloud)
            if not translated:
                continue
            key = translated.casefold()
            if key in seen:
                continue
            seen.add(key)
            aligned.append(translated)

        return aligned

    def _translate_service_for_cloud(self, service: str, normalized_cloud: str) -> str | None:
        service_text = service.strip()
        lowered = service_text.casefold()

        if normalized_cloud == "azure":
            return service_text

        azure_to_gcp = {
            "azure api management": "Apigee",
            "azure front door": "Cloud Load Balancing",
            "azure front door / cdn": "Cloud Load Balancing + Cloud CDN",
            "azure application gateway": "Cloud Load Balancing",
            "azure kubernetes service": "Google Kubernetes Engine",
            "microsoft entra id": "Cloud Identity",
            "azure active directory": "Cloud Identity",
            "azure key vault": "Secret Manager",
            "azure monitor": "Cloud Monitoring",
            "azure log analytics": "Cloud Logging",
            "azure service bus": "Pub/Sub",
            "azure event grid": "Eventarc",
            "azure ai search": "Vertex AI Search",
            "azure storage": "Cloud Storage",
            "azure storage or cosmos db": "Cloud Storage or Firestore",
            "cosmos db": "Firestore",
            "azure cache for redis": "Memorystore for Redis",
            "azure private link / vnets / private endpoints": "VPC, Private Service Connect, Cloud NAT",
            "azure data lake / synapse / fabric": "BigQuery, Dataplex, Cloud Storage",
            "azure ai foundry": "Vertex AI",
            "azure container apps": "Cloud Run",
        }

        azure_to_aws = {
            "azure api management": "Amazon API Gateway",
            "azure front door": "Elastic Load Balancing + CloudFront",
            "azure front door / cdn": "Elastic Load Balancing + CloudFront",
            "azure application gateway": "Application Load Balancer",
            "azure kubernetes service": "Amazon EKS",
            "microsoft entra id": "AWS IAM Identity Center",
            "azure active directory": "AWS IAM Identity Center",
            "azure key vault": "AWS Secrets Manager",
            "azure monitor": "Amazon CloudWatch",
            "azure log analytics": "Amazon CloudWatch Logs",
            "azure service bus": "Amazon SQS / SNS",
            "azure event grid": "Amazon EventBridge",
            "azure ai search": "Amazon OpenSearch Service",
            "azure storage": "Amazon S3",
            "azure storage or cosmos db": "Amazon S3 or DynamoDB",
            "cosmos db": "Amazon DynamoDB",
            "azure cache for redis": "Amazon ElastiCache for Redis",
            "azure private link / vnets / private endpoints": "Amazon VPC, PrivateLink, NAT Gateway",
            "azure data lake / synapse / fabric": "Amazon S3, Redshift, Glue",
            "azure ai foundry": "Amazon Bedrock",
            "azure container apps": "AWS App Runner",
        }

        if normalized_cloud == "gcp":
            return azure_to_gcp.get(lowered, None if lowered.startswith("azure ") or lowered.startswith("microsoft ") else service_text)

        if normalized_cloud == "aws":
            return azure_to_aws.get(lowered, None if lowered.startswith("azure ") or lowered.startswith("microsoft ") else service_text)

        return service_text

    def _build_project_openai_client(self) -> OpenAI:
        self.settings.validate_runtime()
        credential = build_credential(self.settings)
        logger.info("Using Azure auth mode: %s", self.settings.azure_auth_mode)
        project = AIProjectClient(
            endpoint=self.settings.project_endpoint,
            credential=credential,
        )
        return self._build_openai_client(project, credential)

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
