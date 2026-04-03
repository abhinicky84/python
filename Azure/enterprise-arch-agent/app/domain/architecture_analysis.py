from __future__ import annotations

from app.schemas.architecture import ArchitectureAnalysis


def build_architecture_context(user_input: str, cloud_provider: str | None = None) -> ArchitectureAnalysis:
    resolved_cloud = resolve_cloud_provider(user_input, cloud_provider)
    return ArchitectureAnalysis(
        cloud_provider=resolved_cloud,
        cloud_specific_guidance=build_cloud_specific_guidance(resolved_cloud, user_input),
        detected_domains=classify_architecture_request(user_input),
        tools_and_technologies=extract_tools_and_technologies(user_input),
        suggested_azure_services=[],
        integration_guidance=recommend_integration_pattern(user_input),
    )


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def classify_architecture_request(user_input: str) -> str:
    text = user_input.lower()
    tags: list[str] = []

    if _contains_any(text, ("aem", "adobe experience manager", "cms", "content management")):
        tags.append("Adobe Experience Manager")
    if _contains_any(text, ("adobe commerce", "commerce", "storefront", "checkout", "cart")):
        tags.append("eCommerce")
    if "sap" in text:
        tags.append("ERP")
    if "salesforce" in text:
        tags.append("CRM")
    if _contains_any(text, ("api", "apim", "integration", "integration layer")):
        tags.append("API Integration")
    if _contains_any(text, ("gateway", "api gateway")):
        tags.append("API Gateway")
    if _contains_any(text, ("microservice", "microservices", "micro-service")):
        tags.append("Microservices")
    if _contains_any(text, ("soa", "service-oriented", "service oriented", "shared service")):
        tags.append("Service-Oriented Architecture")
    if _contains_any(text, ("frontend", "front-end", "web", "mobile", "bff", "spa")):
        tags.append("Frontend Integration")
    if _contains_any(text, ("analytics", "reporting", "bi", "insights", "dashboard")):
        tags.append("Analytics & Insights")
    if _contains_any(text, ("personalization", "personalisation", "targeting", "recommendation", "next best action")):
        tags.append("Personalization")
    if _contains_any(text, ("seo", "search engine", "discoverability", "organic search")):
        tags.append("SEO / Discoverability")
    if _contains_any(text, ("martech", "marketing automation", "campaign", "journey orchestration", "cdp")):
        tags.append("MarTech")
    if _contains_any(text, ("loyalty", "rewards", "membership")):
        tags.append("Loyalty Platform")
    if _contains_any(text, ("search", "site search", "product search")):
        tags.append("Search Platform")
    if _contains_any(text, ("data platform", "lakehouse", "warehouse", "fabric", "databricks", "cdp")):
        tags.append("Data Platform")
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


def resolve_cloud_provider(user_input: str, selected_cloud: str | None = None, detected_cloud: str | None = None) -> str:
    selected_normalized = normalize_cloud_provider(selected_cloud)
    if selected_normalized:
        return selected_normalized

    inferred_from_text = normalize_cloud_provider(infer_cloud_provider_from_text(user_input))
    detected_normalized = normalize_cloud_provider(detected_cloud)

    if detected_normalized and detected_normalized != "Hybrid / Multi-cloud":
        return detected_normalized
    if inferred_from_text:
        return inferred_from_text
    if detected_normalized:
        return detected_normalized
    return "Azure"


def infer_cloud_provider_from_text(user_input: str) -> str | None:
    lowered = user_input.casefold()
    if "aws" in lowered or "amazon web services" in lowered or "amazon cloud" in lowered:
        return "AWS"
    if "gcp" in lowered or "google cloud" in lowered or "google cloud platform" in lowered:
        return "GCP"
    if "multi-cloud" in lowered or "multicloud" in lowered or "hybrid cloud" in lowered:
        return "Hybrid / Multi-cloud"
    if "azure" in lowered or "microsoft cloud" in lowered or "entra" in lowered or "cosmos db" in lowered or "azure api management" in lowered:
        return "Azure"
    return None


def normalize_cloud_provider(value: str | None) -> str | None:
    if not value:
        return None
    lowered = value.strip().casefold()
    if "google cloud platform" in lowered or lowered == "gcp" or "google cloud" in lowered:
        return "GCP"
    if lowered == "aws" or "amazon web services" in lowered or lowered.startswith("amazon aws") or "amazon cloud" in lowered:
        return "AWS"
    if lowered == "azure" or "microsoft azure" in lowered:
        return "Azure"
    if (
        lowered == "hybrid"
        or "multi-cloud" in lowered
        or "multicloud" in lowered
        or "hybrid / multi-cloud" in lowered
        or "hybrid cloud" in lowered
    ):
        return "Hybrid / Multi-cloud"
    return None


def extract_tools_and_technologies(user_input: str) -> list[str]:
    candidates = [
        "AEM",
        "Adobe Experience Manager",
        "Adobe Commerce",
        "SAP",
        "SAP S/4HANA",
        "Salesforce",
        "Azure API Management",
        "Azure AI Foundry",
        "Azure Container Apps",
        "Azure Kubernetes Service",
        "Azure Service Bus",
        "Azure Event Grid",
        "Azure AI Search",
        "Microsoft Entra ID",
        "Azure Front Door",
        "Azure Storage",
        "Cosmos DB",
        "Fabric",
        "Synapse",
        "Databricks",
        "Redis",
    ]
    lowered = user_input.casefold()
    found: list[str] = []
    for candidate in candidates:
        if candidate.casefold() in lowered and candidate not in found:
            found.append(candidate)
    return found


def build_cloud_specific_guidance(cloud_provider: str, user_input: str) -> list[str]:
    normalized = cloud_provider.casefold()
    guidance = [
        "Keep the recommendation aligned to the preferred cloud environment unless the request explicitly calls for hybrid or multi-cloud patterns.",
        "Use service names, security controls, integration services, and operational patterns that match the target cloud platform.",
    ]

    if normalized == "aws":
        guidance.extend(
            [
                "Favor AWS-native edge, API, container, messaging, security, and observability capabilities for the target-state design.",
                "Describe integrations and runtime decisions using AWS terminology such as API Gateway, CloudFront, EKS, App Runner, EventBridge, SQS/SNS, CloudWatch, Secrets Manager, and IAM Identity Center when relevant.",
            ]
        )
    elif normalized == "gcp":
        guidance.extend(
            [
                "Favor GCP-native edge, API, runtime, eventing, data, AI, security, and observability capabilities for the target-state design.",
                "Describe integrations and runtime decisions using GCP terminology such as Apigee, Cloud Load Balancing, Cloud Run, GKE, Pub/Sub, Eventarc, BigQuery, Vertex AI, Secret Manager, and Cloud Monitoring when relevant.",
            ]
        )
    elif normalized == "hybrid / multi-cloud":
        guidance.extend(
            [
                "Separate shared business capabilities from cloud-specific platform responsibilities and make handoff points explicit.",
                "Identify which integrations, security controls, data movement patterns, and operations remain shared versus cloud-specific.",
            ]
        )
    else:
        guidance.extend(
            [
                "Favor Azure-native edge, API, compute, messaging, security, data, and observability capabilities for the target-state design.",
                "Describe integrations and runtime decisions using Azure terminology such as API Management, Front Door, Container Apps or AKS, Service Bus, Event Grid, Key Vault, Entra ID, and Azure Monitor when relevant.",
            ]
        )

    if "aem" in user_input.casefold() or "adobe" in user_input.casefold():
        guidance.append("Keep Adobe platform integrations aligned with the selected cloud ingress, API, personalization, and analytics patterns rather than assuming a default vendor stack.")

    return guidance


def recommend_integration_pattern(user_input: str) -> str:
    text = user_input.lower()

    patterns = [
        "- Default flow should be channel to frontend to BFF or experience APIs to API management to domain services",
        "- Synchronous APIs for customer-facing real-time interactions via Azure API Management",
        "- Layer APIs into experience, process, and system APIs to keep channels decoupled from core systems",
        "- Event-driven messaging for async downstream processing and resilience",
        "- Canonical business objects where multiple systems exchange the same entities",
        "- Idempotency, retries, dead-letter handling, and observability for all critical integrations",
        "- Use domain-aligned services with clear bounded contexts to avoid tight coupling across platforms",
        "- Expose frontend-facing capabilities through BFF or experience APIs rather than direct channel-to-backend coupling",
        "- Feed analytics, personalization, and experimentation from shared event streams and curated data products",
        "- Treat SEO, discoverability, and content metadata as first-class integration concerns for digital experience platforms",
    ]

    if "sap" in text:
        patterns.append("- Use API-led integration or middleware orchestration for SAP domain services")
    if "salesforce" in text:
        patterns.append("- Use event or API patterns for lead, account, case, and customer-profile synchronization")
    if "aem" in text:
        patterns.append("- Keep content delivery decoupled from transactional systems; integrate through well-defined APIs")
    if _contains_any(text, ("commerce", "storefront", "cart", "checkout")):
        patterns.append("- Decouple storefront experiences from pricing, inventory, and order domains through stable APIs and events")
    if _contains_any(text, ("cms", "content", "aem")):
        patterns.append("- Separate content authoring, content delivery, and transactional experiences to keep CMS concerns isolated")
    if _contains_any(text, ("martech", "campaign", "journey orchestration", "cdp")):
        patterns.append("- Integrate martech platforms through event feeds and profile APIs instead of hardwiring them into core transactional flows")
    if _contains_any(text, ("loyalty", "rewards", "membership")):
        patterns.append("- Model loyalty as its own bounded capability with APIs for enrollment, tiering, balance, and redemption")
    if "microservice" in text or "micro-service" in text:
        patterns.append("- Prefer independently deployable microservices with contract-first APIs and asynchronous domain events")
    if "soa" in text or "service-oriented" in text or "service oriented" in text:
        patterns.append("- Reuse shared enterprise services selectively and avoid central orchestration becoming a bottleneck")
    if "seo" in text or "search" in text:
        patterns.append("- Publish structured content, taxonomy, and search metadata to support SEO and site search experiences")
    if "personalization" in text or "personalisation" in text:
        patterns.append("- Separate profile resolution, decisioning, and content delivery so personalization can evolve without channel rewrites")
    if _contains_any(text, ("analytics", "reporting", "data platform", "lakehouse", "warehouse")):
        patterns.append("- Capture business events once and route them to both operational integrations and downstream analytics products")

    return "\n".join(patterns)
