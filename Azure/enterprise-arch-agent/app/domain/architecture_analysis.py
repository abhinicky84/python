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


def suggest_azure_services(user_input: str) -> list[str]:
    services = [
        "Azure AI Foundry",
        "Azure Container Apps",
        "Azure Monitor",
        "Microsoft Entra ID",
        "Azure API Management",
    ]

    text = user_input.lower()

    if _contains_any(text, ("gateway", "api gateway", "integration", "event", "async", "messaging")):
        services.append("Azure API Management")
    if _contains_any(text, ("microservice", "microservices", "micro-service", "service mesh")):
        services.append("Azure Container Apps")
    if _contains_any(text, ("event", "async", "messaging", "pub/sub", "webhook")):
        services.append("Azure Service Bus")
        services.append("Azure Event Grid")
    if _contains_any(text, ("identity", "sso", "auth")):
        services.append("Microsoft Entra ID")
    if _contains_any(text, ("frontend", "front-end", "web", "mobile", "cdn", "edge", "spa")):
        services.append("Azure Front Door / CDN")
    if _contains_any(text, ("data", "storage", "operational store", "profile", "session")):
        services.append("Azure Storage or Cosmos DB")
    if _contains_any(text, ("analytics", "reporting", "bi", "dashboard", "data platform", "lakehouse", "warehouse", "fabric")):
        services.append("Azure Data Lake / Synapse / Fabric")
    if _contains_any(text, ("personalization", "personalisation", "targeting", "recommendation", "loyalty", "campaign", "cdp")):
        services.append("Azure Cache for Redis")
        services.append("Azure Data Lake / Synapse / Fabric")
    if _contains_any(text, ("seo", "search", "discoverability", "metadata", "catalog")):
        services.append("Azure AI Search")
    if _contains_any(text, ("private", "network", "secure", "vnet", "private endpoint")):
        services.append("Azure Private Link / VNets / Private Endpoints")
    if _contains_any(text, ("kubernetes", "aks")):
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
