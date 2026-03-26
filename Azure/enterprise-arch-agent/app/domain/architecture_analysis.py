from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchitectureContext:
    detected_domains: str
    suggested_azure_services: list[str]
    integration_guidance: str


def build_architecture_context(user_input: str) -> ArchitectureContext:
    return ArchitectureContext(
        detected_domains=classify_architecture_request(user_input),
        suggested_azure_services=suggest_azure_services(user_input),
        integration_guidance=recommend_integration_pattern(user_input),
    )


def classify_architecture_request(user_input: str) -> str:
    text = user_input.lower()
    tags: list[str] = []

    if "aem" in text:
        tags.append("Adobe Experience Manager")
    if "adobe commerce" in text:
        tags.append("eCommerce")
    if "sap" in text:
        tags.append("ERP")
    if "salesforce" in text:
        tags.append("CRM")
    if "api" in text or "apim" in text:
        tags.append("API Integration")
    if "global" in text or "multi-market" in text or "multi language" in text or "multi-language" in text:
        tags.append("Global Platform")
    if "healthcare" in text:
        tags.append("Healthcare Domain")
    if "retail" in text:
        tags.append("Retail Domain")
    if "bank" in text or "financial" in text:
        tags.append("Financial Services Domain")

    if not tags:
        tags.append("General Enterprise Architecture")

    return ", ".join(tags)


def suggest_azure_services(user_input: str) -> list[str]:
    services = [
        "Azure AI Foundry",
        "Azure Container Apps",
        "Azure Monitor",
    ]

    text = user_input.lower()

    if "api" in text or "integration" in text or "apim" in text:
        services.append("Azure API Management")
    if "event" in text or "async" in text or "messaging" in text:
        services.append("Azure Service Bus")
    if "identity" in text or "sso" in text or "auth" in text:
        services.append("Microsoft Entra ID")
    if "data" in text or "storage" in text:
        services.append("Azure Storage or Cosmos DB")
    if "analytics" in text or "reporting" in text:
        services.append("Azure Data Lake / Synapse / Fabric")
    if "private" in text or "network" in text or "secure" in text:
        services.append("Azure Private Link / VNets / Private Endpoints")
    if "kubernetes" in text or "aks" in text:
        services.append("Azure Kubernetes Service")

    seen: set[str] = set()
    deduped: list[str] = []
    for service in services:
        if service not in seen:
            seen.add(service)
            deduped.append(service)

    return deduped


def recommend_integration_pattern(user_input: str) -> str:
    text = user_input.lower()

    patterns = [
        "- Synchronous APIs for customer-facing real-time interactions via Azure API Management",
        "- Event-driven messaging for async downstream processing and resilience",
        "- Canonical business objects where multiple systems exchange the same entities",
        "- Idempotency, retries, dead-letter handling, and observability for all critical integrations",
    ]

    if "sap" in text:
        patterns.append("- Use API-led integration or middleware orchestration for SAP domain services")
    if "salesforce" in text:
        patterns.append("- Use event or API patterns for lead, account, case, and customer-profile synchronization")
    if "aem" in text:
        patterns.append("- Keep content delivery decoupled from transactional systems; integrate through well-defined APIs")

    return "\n".join(patterns)
