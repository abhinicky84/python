from __future__ import annotations

from dataclasses import dataclass
import re
from xml.sax.saxutils import escape

from app.schemas.architecture import ArchitectureAnalysis


@dataclass(frozen=True)
class DiagramNode:
    key: str
    label: str
    category: str


@dataclass(frozen=True)
class DiagramEdge:
    source: str
    target: str
    label: str
    style: str = "solid"


class DiagramGenerator:
    CATEGORY_ORDER = [
        "channels",
        "experience",
        "identity",
        "integration",
        "applications",
        "systems",
        "data",
        "observability",
    ]

    CATEGORY_LABELS = {
        "channels": "User Channels",
        "experience": "Experience Layer",
        "identity": "Security & Identity",
        "integration": "Integration Layer",
        "applications": "Application Services",
        "systems": "Enterprise Platforms",
        "data": "Data & Analytics",
        "observability": "Observability",
    }

    CATEGORY_STYLES = {
        "channels": "fill:#fef3c7,stroke:#d97706,color:#111827",
        "experience": "fill:#dbeafe,stroke:#2563eb,color:#111827",
        "identity": "fill:#ede9fe,stroke:#7c3aed,color:#111827",
        "integration": "fill:#dcfce7,stroke:#16a34a,color:#111827",
        "applications": "fill:#fae8ff,stroke:#c026d3,color:#111827",
        "systems": "fill:#fee2e2,stroke:#dc2626,color:#111827",
        "data": "fill:#cffafe,stroke:#0891b2,color:#111827",
        "observability": "fill:#e5e7eb,stroke:#4b5563,color:#111827",
    }

    DRAWIO_LANE_STYLES = {
        "channels": "swimlane;html=1;rounded=1;fillColor=#fef3c7;strokeColor=#d97706;fontStyle=1;",
        "experience": "swimlane;html=1;rounded=1;fillColor=#dbeafe;strokeColor=#2563eb;fontStyle=1;",
        "identity": "swimlane;html=1;rounded=1;fillColor=#ede9fe;strokeColor=#7c3aed;fontStyle=1;",
        "integration": "swimlane;html=1;rounded=1;fillColor=#dcfce7;strokeColor=#16a34a;fontStyle=1;",
        "applications": "swimlane;html=1;rounded=1;fillColor=#fae8ff;strokeColor=#c026d3;fontStyle=1;",
        "systems": "swimlane;html=1;rounded=1;fillColor=#fee2e2;strokeColor=#dc2626;fontStyle=1;",
        "data": "swimlane;html=1;rounded=1;fillColor=#cffafe;strokeColor=#0891b2;fontStyle=1;",
        "observability": "swimlane;html=1;rounded=1;fillColor=#e5e7eb;strokeColor=#4b5563;fontStyle=1;",
    }

    DRAWIO_NODE_STYLES = {
        "channels": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff7d6;strokeColor=#d97706;shadow=1;spacing=10;fontStyle=1;",
        "experience": "rounded=1;whiteSpace=wrap;html=1;fillColor=#edf5ff;strokeColor=#2563eb;shadow=1;spacing=10;fontStyle=1;",
        "identity": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f3ff;strokeColor=#7c3aed;shadow=1;spacing=10;fontStyle=1;",
        "integration": "rounded=1;whiteSpace=wrap;html=1;fillColor=#eafcf0;strokeColor=#16a34a;fontStyle=1;shadow=1;spacing=10;",
        "applications": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fdf0ff;strokeColor=#c026d3;shadow=1;spacing=10;fontStyle=1;",
        "systems": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff1f2;strokeColor=#dc2626;shadow=1;spacing=10;fontStyle=1;",
        "data": "rounded=1;whiteSpace=wrap;html=1;fillColor=#ecfeff;strokeColor=#0891b2;shadow=1;spacing=10;fontStyle=1;",
        "observability": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f3f4f6;strokeColor=#4b5563;shadow=1;spacing=10;fontStyle=1;",
    }

    DRAWIO_NODE_DETAILS = {
        "users": ["Customers", "Employees", "B2B teams"],
        "partners": ["Suppliers", "Agencies", "Distributors"],
        "web": ["Web", "Mobile", "Portal entry points"],
        "frontend": ["Presentation APIs", "BFF", "Session handling"],
        "aem": ["Content fragments", "Experience fragments", "Authoring", "Workflows", "DAM integration", "Publishing"],
        "aem_assets": ["Asset repository", "Metadata", "Renditions", "Governance", "Search", "Distribution"],
        "portal": ["Content orchestration", "Digital touchpoints"],
        "commerce": ["Catalog", "Pricing", "Cart", "Checkout", "Promotions", "Inventory"],
        "edge": ["Caching", "Acceleration", "Global routing"],
        "personalization": ["Segmentation", "Decisioning", "Recommendations", "Targeting", "A/B testing", "Next best action"],
        "target": ["Offers", "Targeting", "Experiments", "Personalized content"],
        "dynamic_media": ["Image delivery", "Video", "Renditions", "Media optimization"],
        "seo": ["Structured metadata", "Sitemaps", "Discoverability"],
        "entra": ["SSO", "OAuth / OIDC", "Role-based access"],
        "network": ["Private Link", "VNet isolation", "Ingress controls"],
        "edge_api": ["WAF-aligned rules", "Rate limiting", "Edge validation"],
        "api_gateway": ["North-south APIs", "Contract mediation", "Traffic shaping"],
        "apim": ["Policies", "Developer access", "Security enforcement"],
        "orchestration": ["Process flows", "Transformation", "System coordination"],
        "service_bus": ["Queues", "Topics", "Reliable delivery"],
        "event_grid": ["Event distribution", "Webhook fan-out", "Notifications"],
        "domain_services": ["Core business logic", "Composable domains", "Reusable APIs"],
        "microservices": ["Bounded contexts", "Independent release", "Domain autonomy"],
        "container_apps": ["Scalable runtime", "Revision rollout", "Service endpoints"],
        "aks": ["Kubernetes runtime", "Platform controls", "Advanced workloads"],
        "shared_services": ["Common capabilities", "Enterprise reuse", "Shared policies"],
        "service_mesh": ["mTLS", "East-west controls", "Traffic governance"],
        "ai_foundry": ["Prompt flows", "Model access", "AI orchestration"],
        "sap": ["Order management", "Product master", "Pricing", "Inventory", "Finance", "Fulfillment"],
        "sap_cpi": ["Integration flows", "Mappings", "Adapters", "B2B/EDI"],
        "sap_btp": ["Extension apps", "Workflows", "Event mesh", "Data services"],
        "fiori": ["UX apps", "Launchpad", "Role-based access", "Approvals"],
        "salesforce": ["CRM", "Service workflows", "Customer engagement"],
        "martech": ["Campaigns", "Journeys", "Audience activation"],
        "loyalty": ["Rewards", "Membership", "Offers"],
        "search_platform": ["Site search", "Faceting", "Relevance tuning"],
        "data_platform": ["Lakehouse", "BI", "Data products"],
        "lob": ["Back-office apps", "Operational systems", "Legacy integration"],
        "operational_data": ["Transactional store", "Low-latency access", "Operational views"],
        "canonical_data": ["Shared business schema", "Event contracts", "Master data exchange"],
        "customer_profile": ["Unified profile", "Segmentation", "Activation context"],
        "search_index": ["Indexing", "Search feeds", "SEO publishing"],
        "analytics": ["Reporting", "Insights", "Decision support"],
        "adobe_analytics": ["Traffic analytics", "Conversion", "Customer journeys", "Dashboards"],
        "aep": ["Profile unification", "Schemas", "Datasets", "Activation"],
        "rt_cdp": ["Audience building", "Real-time profiles", "Activation", "Consent"],
        "azure_cloud": ["App services", "Integration", "Data platform", "Identity"],
        "aws_cloud": ["Storage", "CDN", "Compute", "Messaging"],
        "gcp_cloud": ["Analytics", "AI/ML", "Storage", "Data processing"],
        "monitor": ["Metrics", "Tracing", "Alerting"],
        "governance": ["Audit trail", "Compliance", "Operational guardrails"],
    }

    DRAWIO_PRIMARY_EDGE_LABELS = {
        ("users", "web"),
        ("web", "frontend"),
        ("frontend", "apim"),
        ("entra", "apim"),
        ("apim", "orchestration"),
        ("orchestration", "domain_services"),
        ("service_bus", "microservices"),
        ("domain_services", "canonical_data"),
        ("canonical_data", "analytics"),
        ("analytics", "personalization"),
        ("personalization", "customer_profile"),
        ("canonical_data", "search_index"),
    }

    DRAWIO_LAYOUT_HINTS = {
        "users": (0, 0),
        "partners": (0, 1),
        "web": (1, 0),
        "edge": (1, 0),
        "frontend": (2, 0),
        "entra": (2, 0),
        "network": (1, 0),
        "aem": (3, 0),
        "portal": (3, 0),
        "commerce": (4, 0),
        "seo": (4, 1),
        "personalization": (5, 0),
        "edge_api": (1, 0),
        "api_gateway": (2, 0),
        "apim": (3, 0),
        "orchestration": (4, 0),
        "service_bus": (5, 0),
        "event_grid": (5, 1),
        "domain_services": (4, 0),
        "container_apps": (4, 1),
        "microservices": (5, 0),
        "aks": (5, 1),
        "shared_services": (6, 0),
        "service_mesh": (6, 1),
        "ai_foundry": (6, 0),
        "sap": (4, 0),
        "lob": (4, 1),
        "salesforce": (5, 0),
        "martech": (6, 0),
        "loyalty": (6, 1),
        "search_platform": (7, 0),
        "data_platform": (7, 1),
        "operational_data": (4, 0),
        "canonical_data": (5, 0),
        "customer_profile": (6, 0),
        "search_index": (6, 1),
        "analytics": (7, 0),
        "monitor": (5, 0),
        "governance": (6, 0),
    }

    def generate(self, user_input: str, model_response: str, analysis: ArchitectureAnalysis) -> tuple[str, str]:
        nodes = self._build_nodes(user_input, model_response, analysis)
        edges = self._build_edges(nodes)
        return self._build_mermaid(nodes, edges), self._build_drawio_xml(nodes, edges)

    def _build_nodes(
        self,
        user_input: str,
        model_response: str,
        analysis: ArchitectureAnalysis,
    ) -> list[DiagramNode]:
        text = f"{user_input}\n{model_response}"
        nodes: list[DiagramNode] = []

        self._add_node(nodes, "users", "Business Users", "channels")
        self._add_node(nodes, "web", "Web / Mobile Channels", "channels")
        if self._mentions_any(text, ["partner", "dealer", "vendor", "portal"]):
            self._add_node(nodes, "partners", "Partner / External Channels", "channels")

        self._add_node(nodes, "frontend", "Frontend Apps / BFF", "experience")
        if self._mentions_any(text, ["aem", "content", "cms", "experience"]):
            self._add_node(nodes, "aem", "AEM", "experience")
        if self._mentions_any(text, ["aem assets", "assets", "dam"]):
            self._add_node(nodes, "aem_assets", "AEM Assets", "experience")
        if self._mentions_any(text, ["adobe commerce", "commerce", "storefront", "cart", "checkout"]):
            self._add_node(nodes, "commerce", "Adobe Commerce", "experience")
        if self._mentions_any(text, ["cdn", "edge", "front door"]):
            self._add_node(nodes, "edge", "Edge Delivery / CDN", "experience")
        if self._mentions_any(text, ["personalization", "personalisation", "targeting", "recommendation"]):
            self._add_node(nodes, "personalization", "Personalization Engine", "experience")
        if self._mentions_any(text, ["adobe target", "target"]):
            self._add_node(nodes, "target", "Adobe Target", "experience")
        if self._mentions_any(text, ["dynamic media", "adobe dynamic media"]):
            self._add_node(nodes, "dynamic_media", "Adobe Dynamic Media", "experience")
        if self._mentions_any(text, ["seo", "search engine", "discoverability", "metadata"]):
            self._add_node(nodes, "seo", "SEO / Metadata Services", "experience")
        if not any(node.key == "aem" for node in nodes):
            self._add_node(nodes, "portal", "Digital Experience Portal", "experience")

        self._add_node(nodes, "entra", "Microsoft Entra ID", "identity")
        if self._mentions_any(text, ["private", "network", "private endpoint", "private link", "vnet", "secure"]):
            self._add_node(nodes, "network", "Private Network Boundary", "identity")

        self._add_node(nodes, "apim", "Azure API Management", "integration")
        self._add_node(nodes, "api_gateway", "API Gateway", "integration")
        if self._mentions_any(text, ["api gateway", "gateway", "edge api"]):
            self._add_node(nodes, "edge_api", "Edge API Policies", "integration")
        if self._mentions_any(text, ["event", "async", "messaging", "queue", "service bus"]):
            self._add_node(nodes, "service_bus", "Azure Service Bus", "integration")
        if self._mentions_any(text, ["event grid", "pub/sub", "webhook"]):
            self._add_node(nodes, "event_grid", "Azure Event Grid", "integration")
        self._add_node(nodes, "orchestration", "Integration Orchestration", "integration")

        if self._contains_service(analysis, "Azure Container Apps"):
            self._add_node(nodes, "container_apps", "Azure Container Apps", "applications")
        if self._contains_service(analysis, "Azure Kubernetes Service"):
            self._add_node(nodes, "aks", "Azure Kubernetes Service", "applications")
        self._add_node(nodes, "domain_services", "Domain Services", "applications")
        self._add_node(nodes, "microservices", "Microservices", "applications")
        if self._mentions_any(text, ["microservice", "micro-service", "bounded context"]):
            self._add_node(nodes, "service_mesh", "Service-to-Service Policies", "applications")
        if self._mentions_any(text, ["soa", "service-oriented", "service oriented", "shared service"]):
            self._add_node(nodes, "shared_services", "Shared Enterprise Services", "applications")
        if self._contains_service(analysis, "Azure AI Foundry"):
            self._add_node(nodes, "ai_foundry", "Azure AI Foundry", "applications")

        if self._mentions_any(text, ["sap"]):
            self._add_node(nodes, "sap", self._extract_sap_label(text), "systems")
        if self._mentions_any(text, ["cpi", "sap cpi", "cloud platform integration"]):
            self._add_node(nodes, "sap_cpi", "SAP CPI", "systems")
        if self._mentions_any(text, ["btp", "sap btp", "business technology platform"]):
            self._add_node(nodes, "sap_btp", "SAP BTP", "systems")
        if self._mentions_any(text, ["fiori", "sap fiori"]):
            self._add_node(nodes, "fiori", "SAP Fiori", "systems")
        if self._mentions_any(text, ["salesforce"]):
            self._add_node(nodes, "salesforce", "Salesforce", "systems")
        if self._mentions_any(text, ["martech", "campaign", "journey orchestration", "marketing automation"]):
            self._add_node(nodes, "martech", "MarTech Platform", "systems")
        if self._mentions_any(text, ["loyalty", "rewards", "membership"]):
            self._add_node(nodes, "loyalty", "Loyalty Platform", "systems")
        if self._mentions_any(text, ["search", "site search", "product search", "seo"]):
            self._add_node(nodes, "search_platform", "Search Platform", "systems")
        if self._mentions_any(text, ["data platform", "lakehouse", "warehouse", "fabric", "databricks"]):
            self._add_node(nodes, "data_platform", "Enterprise Data Platform", "systems")
        if self._mentions_any(text, ["erp", "crm", "backend", "line of business"]) and len(
            [node for node in nodes if node.category == "systems"]
        ) < 2:
            self._add_node(nodes, "lob", "Line-of-Business Systems", "systems")

        if self._contains_any_service(analysis, ["Azure Storage or Cosmos DB", "Azure Storage", "Cosmos DB"]):
            self._add_node(nodes, "operational_data", "Operational Data Store", "data")
        self._add_node(nodes, "canonical_data", "Canonical Data Model", "data")
        if self._contains_any_service(analysis, ["Azure Data Lake / Synapse / Fabric", "Synapse", "Fabric"]):
            self._add_node(nodes, "analytics", "Analytics & Reporting", "data")
        if self._mentions_any(text, ["personalization", "personalisation", "customer profile", "cdp"]):
            self._add_node(nodes, "customer_profile", "Customer Profile / CDP", "data")
        if self._mentions_any(text, ["adobe analytics"]):
            self._add_node(nodes, "adobe_analytics", "Adobe Analytics", "data")
        if self._mentions_any(text, ["aep", "adobe experience platform"]):
            self._add_node(nodes, "aep", "Adobe Experience Platform", "data")
        if self._mentions_any(text, ["rt-cdp", "rtcdp", "real-time cdp"]):
            self._add_node(nodes, "rt_cdp", "Adobe RT-CDP", "data")
        if self._mentions_any(text, ["azure"]):
            self._add_node(nodes, "azure_cloud", "Azure Platform", "data")
        if self._mentions_any(text, ["aws"]):
            self._add_node(nodes, "aws_cloud", "AWS Services", "data")
        if self._mentions_any(text, ["gcp", "google cloud"]):
            self._add_node(nodes, "gcp_cloud", "GCP Services", "data")
        if self._contains_service(analysis, "Azure AI Search") or self._mentions_any(text, ["seo", "search", "discoverability"]):
            self._add_node(nodes, "search_index", "Search / SEO Index", "data")

        self._add_node(nodes, "monitor", "Azure Monitor", "observability")
        self._add_node(nodes, "governance", "Audit / Governance", "observability")

        return nodes

    def _build_edges(self, nodes: list[DiagramNode]) -> list[DiagramEdge]:
        node_map = {node.key: node for node in nodes}
        edges: list[DiagramEdge] = []

        def connect(source: str, target: str, label: str, style: str = "solid") -> None:
            if source in node_map and target in node_map:
                edge = DiagramEdge(source=source, target=target, label=label, style=style)
                if edge not in edges:
                    edges.append(edge)

        connect("users", "web", "Journeys")
        connect("partners", "web", "Partner Access")

        for experience in self._node_keys(nodes, "experience"):
            connect("web", experience, "UX / Content")
            connect("partners", experience, "Partner Experience")
            connect(experience, "entra", "SSO / Session")
            connect(experience, "apim", "Experience APIs")

        connect("web", "edge", "Global Delivery")
        connect("web", "frontend", "Channel Requests")
        connect("edge", "frontend", "Edge Routing")
        connect("aem_assets", "aem", "Asset Supply")
        connect("frontend", "apim", "BFF / App APIs")
        connect("frontend", "api_gateway", "Northbound APIs")
        connect("seo", "aem", "Structured Metadata")
        connect("seo", "search_index", "SEO Feeds")
        connect("personalization", "frontend", "Targeted Content")
        connect("target", "personalization", "Offer Decisions")
        connect("dynamic_media", "frontend", "Optimized Media")
        connect("personalization", "customer_profile", "Profile Decisions")

        connect("entra", "apim", "AuthN / Tokens")
        connect("network", "apim", "Private Access")
        connect("api_gateway", "apim", "North-South Policies")
        connect("edge_api", "api_gateway", "Edge Controls")
        connect("apim", "orchestration", "Policy / Routing")
        connect("event_grid", "orchestration", "Events / Notifications")
        connect("orchestration", "domain_services", "Service Composition")
        connect("orchestration", "microservices", "Domain APIs")
        connect("orchestration", "shared_services", "Shared Services")
        connect("orchestration", "service_bus", "Events")
        connect("service_bus", "domain_services", "Async Commands")
        connect("service_bus", "microservices", "Domain Events")
        connect("domain_services", "container_apps", "Runtime")
        connect("domain_services", "aks", "Runtime")
        connect("domain_services", "ai_foundry", "AI Enrichment")
        connect("domain_services", "operational_data", "Transactional Data")
        connect("domain_services", "canonical_data", "Canonical Events")
        connect("microservices", "container_apps", "Service Runtime")
        connect("microservices", "operational_data", "Service Data")
        connect("microservices", "canonical_data", "Business Events")
        connect("service_mesh", "microservices", "East-West Controls")
        connect("service_bus", "canonical_data", "Event Stream")

        for system in self._node_keys(nodes, "systems"):
            connect("orchestration", system, "API / Event Integration")
            connect(system, "canonical_data", "Master Data")

        connect("sap_btp", "sap", "Extensions")
        connect("sap_cpi", "sap", "Process Integration")
        connect("fiori", "sap", "Business UX")

        connect("operational_data", "analytics", "Batch / CDC")
        connect("canonical_data", "analytics", "Analytics Feed")
        connect("customer_profile", "analytics", "Customer Insights")
        connect("adobe_analytics", "analytics", "Digital Insights")
        connect("aep", "customer_profile", "Unified Profiles")
        connect("rt_cdp", "customer_profile", "Audience Activation")
        connect("canonical_data", "customer_profile", "Profile Inputs")
        connect("canonical_data", "search_index", "Searchable Content")
        connect("analytics", "web", "Insights / Reporting")
        connect("analytics", "personalization", "Segments / Models")
        connect("azure_cloud", "analytics", "Cloud Data Services")
        connect("aws_cloud", "search_index", "Cloud Support")
        connect("gcp_cloud", "analytics", "ML / Analytics")

        for observable in (
            "apim",
            "api_gateway",
            "orchestration",
            "domain_services",
            "microservices",
            "service_bus",
            "event_grid",
            "container_apps",
            "aks",
            "frontend",
        ):
            connect(observable, "monitor", "Telemetry", style="dashed")
        for governed in ("entra", "apim", "api_gateway", "canonical_data", "analytics", "customer_profile", "search_index"):
            connect(governed, "governance", "Audit", style="dashed")

        return edges

    def _build_mermaid(self, nodes: list[DiagramNode], edges: list[DiagramEdge]) -> str:
        lines = ["flowchart LR"]

        for category in self.CATEGORY_ORDER:
            category_nodes = [node for node in nodes if node.category == category]
            if not category_nodes:
                continue
            lines.append(f'    subgraph {category}["{self.CATEGORY_LABELS[category]}"]')
            for node in category_nodes:
                lines.append(f'        {node.key}["{self._escape_mermaid(node.label)}"]')
            lines.append("    end")

        for edge in edges:
            connector = "-->" if edge.style == "solid" else "-.->"
            lines.append(f"    {edge.source} {connector}|{self._escape_mermaid(edge.label)}| {edge.target}")

        for category, style in self.CATEGORY_STYLES.items():
            lines.append(f"    style {category} {style}")

        return "\n".join(lines)

    def _build_drawio_xml(self, nodes: list[DiagramNode], edges: list[DiagramEdge]) -> str:
        node_map = {node.key: node for node in nodes}
        display_keys = [key for key in self._drawio_display_node_keys() if key in node_map]
        page_width = 2700
        page_height = 1450

        lines = [
            '<mxfile host="app.diagrams.net">',
            '  <diagram id="enterprise-architecture" name="Enterprise Architecture">',
            f'    <mxGraphModel dx="1800" dy="1080" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_width}" pageHeight="{page_height}" math="0" shadow="0">',
            "      <root>",
            '        <mxCell id="0" />',
            '        <mxCell id="1" parent="0" />',
            '        <mxCell id="diagram-title" value="Enterprise Architecture Overview" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=24;fontStyle=1;fontColor=#0f172a;" vertex="1" parent="1">',
            '          <mxGeometry x="40" y="24" width="520" height="34" as="geometry" />',
            '        </mxCell>',
            '        <mxCell id="diagram-subtitle" value="Clean solution view with primary user journeys and integration flows" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=12;fontColor=#64748b;" vertex="1" parent="1">',
            '          <mxGeometry x="40" y="54" width="640" height="22" as="geometry" />',
            '        </mxCell>',
        ]

        for heading, x, y in self._drawio_section_headings():
            heading_id = self._drawio_safe_id(heading)
            lines.extend(
                [
                    f'        <mxCell id="heading-{heading_id}" value="{escape(heading)}" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=14;fontStyle=1;fontColor=#334155;" vertex="1" parent="1">',
                    f'          <mxGeometry x="{x}" y="{y}" width="220" height="24" as="geometry" />',
                    "        </mxCell>",
                ]
            )

        node_ids: dict[str, str] = {}
        for key in display_keys:
            node = node_map[key]
            x, y, width, height = self._drawio_node_geometry(key)

            if key in {"users", "partners"}:
                cell_id = f"node-{key}"
                node_ids[key] = cell_id
                lines.extend(
                    [
                        f'        <mxCell id="{cell_id}" value="" style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;fillColor=#ffffff;strokeColor=#475569;strokeWidth=1.5;" vertex="1" parent="1">',
                        f'          <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry" />',
                        "        </mxCell>",
                        f'        <mxCell id="{cell_id}-label" value="{escape(node.label)}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;whiteSpace=wrap;fontSize=12;fontStyle=1;fontColor=#0f172a;" vertex="1" parent="1">',
                        f'          <mxGeometry x="{x - 28}" y="{y + height + 8}" width="{width + 56}" height="20" as="geometry" />',
                        "        </mxCell>",
                    ]
                )
                continue

            group_id = f"group-{key}"
            body_id = f"node-{key}"
            node_ids[key] = body_id
            lines.extend(self._build_drawio_grouped_node(group_id, body_id, node, x, y, width, height))

        edge_index = 1
        for source, target, label, style in self._drawio_edge_specs(node_ids):
            edge_style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
                "html=1;endArrow=block;strokeWidth=1.6;"
            )
            edge_style += "dashed=1;strokeColor=#94a3b8;" if style == "dashed" else "strokeColor=#475569;"
            edge_style += self._drawio_edge_anchor_style(source, target, node_ids)
            value = escape(label) if label else ""
            if value:
                edge_style += "fontSize=11;fontColor=#334155;labelBackgroundColor=#ffffff;"
            lines.extend(
                [
                    f'        <mxCell id="edge-{edge_index}" value="{value}" style="{edge_style}" edge="1" parent="1" source="{source}" target="{target}">',
                    '          <mxGeometry relative="1" as="geometry" />',
                    "        </mxCell>",
                ]
            )
            edge_index += 1

        lines.extend(
            [
                "      </root>",
                "    </mxGraphModel>",
                "  </diagram>",
                "</mxfile>",
            ]
        )
        return "\n".join(lines)

    def _add_node(self, nodes: list[DiagramNode], key: str, label: str, category: str) -> None:
        if any(node.key == key for node in nodes):
            return
        nodes.append(DiagramNode(key=key, label=label, category=category))

    def _node_keys(self, nodes: list[DiagramNode], category: str) -> list[str]:
        return [node.key for node in nodes if node.category == category]

    def _contains_service(self, analysis: ArchitectureAnalysis, service_name: str) -> bool:
        return any(service_name in service for service in analysis.suggested_azure_services)

    def _contains_any_service(self, analysis: ArchitectureAnalysis, service_names: list[str]) -> bool:
        return any(name in service for service in analysis.suggested_azure_services for name in service_names)

    def _mentions_any(self, text: str, terms: list[str]) -> bool:
        lowered = text.casefold()
        return any(term.casefold() in lowered for term in terms)

    def _extract_sap_label(self, text: str) -> str:
        match = re.search(r"\bSAP(?:\s+[A-Za-z0-9/.-]+)?\b", text, flags=re.IGNORECASE)
        if not match:
            return "SAP"
        label = re.sub(r"\s+", " ", match.group(0)).strip()
        return label.upper() if label.casefold() == "sap" else label.replace("Sap", "SAP")

    def _escape_mermaid(self, text: str) -> str:
        return text.replace('"', "'")

    def _build_drawio_node_value(self, node: DiagramNode) -> str:
        details = self.DRAWIO_NODE_DETAILS.get(node.key, [])
        if not details:
            return node.label

        detail_html = "".join(
            f"<div style='font-size:11px;color:#475569;line-height:1.35;'>{escape(detail)}</div>" for detail in details[:3]
        )
        return (
            f"<div style='font-size:15px;font-weight:700;color:#0f172a;line-height:1.25;margin-bottom:6px;'>"
            f"{escape(node.label)}"
            "</div>"
            f"{detail_html}"
        )

    def _should_label_drawio_edge(self, edge: DiagramEdge) -> bool:
        return (edge.source, edge.target) in self.DRAWIO_PRIMARY_EDGE_LABELS

    def _build_drawio_compact_value(self, node: DiagramNode) -> str:
        details = self.DRAWIO_NODE_DETAILS.get(node.key, [])
        subtitle = " | ".join(details[:2])
        if not subtitle:
            return f"<div style='font-size:15px;font-weight:700;color:#0f172a;'>{escape(node.label)}</div>"
        return (
            f"<div style='font-size:15px;font-weight:700;color:#0f172a;line-height:1.2;margin-bottom:6px;'>{escape(node.label)}</div>"
            f"<div style='font-size:11px;color:#64748b;line-height:1.3;'>{escape(subtitle)}</div>"
        )

    def _drawio_display_node_keys(self) -> list[str]:
        return [
            "users",
            "partners",
            "web",
            "edge",
            "frontend",
            "aem",
            "aem_assets",
            "commerce",
            "personalization",
            "target",
            "dynamic_media",
            "entra",
            "network",
            "apim",
            "orchestration",
            "service_bus",
            "domain_services",
            "microservices",
            "ai_foundry",
            "sap",
            "sap_cpi",
            "sap_btp",
            "fiori",
            "salesforce",
            "martech",
            "canonical_data",
            "customer_profile",
            "search_index",
            "analytics",
            "adobe_analytics",
            "aep",
            "rt_cdp",
            "azure_cloud",
            "aws_cloud",
            "gcp_cloud",
            "monitor",
            "governance",
        ]

    def _drawio_section_headings(self) -> list[tuple[str, int, int]]:
        return [
            ("Users", 40, 108),
            ("Channels", 210, 108),
            ("Experience", 430, 108),
            ("Security", 980, 108),
            ("Integration", 1230, 108),
            ("Applications", 1760, 108),
            ("Enterprise Systems", 2060, 108),
            ("Data & Insights", 1280, 700),
            ("Operations", 1870, 610),
        ]

    def _drawio_node_geometry(self, key: str) -> tuple[int, int, int, int]:
        positions = {
            "users": (60, 170, 42, 80),
            "partners": (60, 340, 42, 80),
            "web": (190, 210, 190, 96),
            "edge": (430, 110, 210, 132),
            "frontend": (430, 300, 210, 132),
            "aem": (700, 80, 250, 188),
            "aem_assets": (700, 300, 250, 150),
            "commerce": (700, 500, 250, 168),
            "personalization": (700, 720, 250, 168),
            "target": (990, 500, 180, 132),
            "dynamic_media": (990, 300, 180, 132),
            "entra": (980, 90, 190, 114),
            "network": (980, 230, 190, 96),
            "apim": (1230, 90, 220, 132),
            "orchestration": (1490, 90, 230, 132),
            "service_bus": (1490, 280, 230, 114),
            "domain_services": (1760, 90, 240, 132),
            "microservices": (1760, 280, 240, 132),
            "ai_foundry": (1760, 470, 240, 114),
            "sap": (2060, 70, 250, 188),
            "sap_cpi": (2060, 290, 220, 114),
            "sap_btp": (2060, 430, 220, 114),
            "fiori": (2060, 570, 220, 114),
            "salesforce": (2330, 290, 200, 114),
            "martech": (2330, 430, 200, 114),
            "canonical_data": (1280, 760, 240, 114),
            "customer_profile": (1560, 760, 240, 114),
            "search_index": (1840, 760, 240, 114),
            "analytics": (2120, 760, 240, 114),
            "adobe_analytics": (1280, 920, 220, 114),
            "aep": (1540, 920, 220, 114),
            "rt_cdp": (1800, 920, 220, 114),
            "azure_cloud": (2060, 920, 220, 114),
            "aws_cloud": (2320, 1080, 200, 114),
            "gcp_cloud": (2320, 920, 200, 114),
            "monitor": (2120, 1110, 180, 78),
            "governance": (2120, 1210, 180, 78),
        }
        return positions.get(key, (210, 230, 200, 76))

    def _drawio_edge_specs(self, node_ids: dict[str, str]) -> list[tuple[str, str, str, str]]:
        preferred_edges = [
            ("users", "web", "User journeys", "solid"),
            ("partners", "web", "Partner access", "solid"),
            ("web", "frontend", "Channel requests", "solid"),
            ("edge", "frontend", "Accelerated delivery", "solid"),
            ("aem", "frontend", "Content delivery", "solid"),
            ("aem_assets", "aem", "Asset supply", "solid"),
            ("commerce", "frontend", "Commerce services", "solid"),
            ("personalization", "frontend", "Personalized experiences", "solid"),
            ("target", "personalization", "Targeting decisions", "solid"),
            ("dynamic_media", "frontend", "Dynamic media", "solid"),
            ("frontend", "entra", "Login / session", "solid"),
            ("entra", "apim", "Identity tokens", "solid"),
            ("frontend", "apim", "Experience APIs", "solid"),
            ("apim", "orchestration", "Managed integration", "solid"),
            ("orchestration", "service_bus", "Events", "solid"),
            ("orchestration", "domain_services", "Business orchestration", "solid"),
            ("service_bus", "microservices", "Async events", "solid"),
            ("domain_services", "sap", "ERP integration", "solid"),
            ("sap_cpi", "sap", "SAP integration", "solid"),
            ("sap_btp", "sap", "Extensions", "solid"),
            ("fiori", "sap", "User experience", "solid"),
            ("domain_services", "salesforce", "CRM integration", "solid"),
            ("domain_services", "martech", "Campaign activation", "solid"),
            ("domain_services", "canonical_data", "Business events", "solid"),
            ("canonical_data", "customer_profile", "Profile inputs", "solid"),
            ("canonical_data", "search_index", "Content indexing", "solid"),
            ("canonical_data", "analytics", "Analytics feed", "solid"),
            ("adobe_analytics", "analytics", "Adobe metrics", "solid"),
            ("aep", "customer_profile", "Experience profiles", "solid"),
            ("rt_cdp", "customer_profile", "Audience activation", "solid"),
            ("azure_cloud", "analytics", "Azure data platform", "solid"),
            ("gcp_cloud", "analytics", "GCP analytics", "solid"),
            ("analytics", "personalization", "Segments / models", "solid"),
            ("apim", "monitor", "Telemetry", "dashed"),
            ("canonical_data", "governance", "Audit", "dashed"),
        ]

        result: list[tuple[str, str, str, str]] = []
        for source_key, target_key, label, style in preferred_edges:
            if source_key in node_ids and target_key in node_ids:
                result.append((node_ids[source_key], node_ids[target_key], label, style))
        return result

    def _build_drawio_grouped_node(
        self,
        group_id: str,
        body_id: str,
        node: DiagramNode,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> list[str]:
        lines = [
            f'        <mxCell id="{group_id}" value="" style="group" vertex="1" connectable="0" parent="1">',
            f'          <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry" />',
            "        </mxCell>",
        ]

        header_height = 42
        details = self.DRAWIO_NODE_DETAILS.get(node.key, [])
        body_style = self._drawio_group_body_style(node.category)
        tile_style = self._drawio_group_tile_style(node.category)

        lines.extend(
            [
                f'        <mxCell id="{body_id}" value="" style="{body_style}" vertex="1" parent="{group_id}">',
                f'          <mxGeometry x="0" y="0" width="{width}" height="{height}" as="geometry" />',
                "        </mxCell>",
                f'        <mxCell id="{body_id}-title" value="{escape(node.label)}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=16;fontStyle=1;fontColor=#0f172a;" vertex="1" parent="{group_id}">',
                f'          <mxGeometry x="16" y="10" width="{width - 32}" height="24" as="geometry" />',
                "        </mxCell>",
            ]
        )

        if not details:
            return lines

        tile_gap = 10
        tile_y_start = header_height
        tile_width = (width - 30) / 2
        tile_height = 28
        max_rows = max(1, int((height - tile_y_start - 10 + 8) // (tile_height + 8)))
        max_tiles = max_rows * 2
        details = details[:max_tiles]

        for index, detail in enumerate(details):
            col = index % 2
            row = index // 2
            tile_x = 10 + (col * (tile_width + tile_gap))
            tile_y = tile_y_start + (row * (tile_height + 8))
            lines.extend(
                [
                    f'        <mxCell id="{body_id}-detail-{index}" value="{escape(detail)}" style="{tile_style}" vertex="1" parent="{group_id}">',
                    f'          <mxGeometry x="{tile_x}" y="{tile_y}" width="{tile_width}" height="{tile_height}" as="geometry" />',
                    "        </mxCell>",
                ]
            )

        return lines

    def _drawio_group_body_style(self, category: str) -> str:
        category_styles = {
            "channels": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f2f2f2;strokeColor=#cbd5e1;shadow=0;",
            "experience": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;shadow=0;",
            "identity": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;shadow=0;",
            "integration": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;shadow=0;",
            "applications": "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;shadow=0;",
            "systems": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;shadow=0;",
            "data": "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;shadow=0;",
            "observability": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;shadow=0;",
        }
        return category_styles[category]

    def _drawio_group_tile_style(self, category: str) -> str:
        tile_styles = {
            "channels": "rounded=1;whiteSpace=wrap;html=1;fillColor=#d8d8d8;strokeColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#111827;",
            "experience": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fee599;strokeColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#111827;",
            "identity": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fee599;strokeColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#111827;",
            "integration": "rounded=1;whiteSpace=wrap;html=1;fillColor=#9fc5f8;strokeColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#111827;",
            "applications": "rounded=1;whiteSpace=wrap;html=1;fillColor=#b6d7a8;strokeColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#111827;",
            "systems": "rounded=1;whiteSpace=wrap;html=1;fillColor=#ea9999;strokeColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#111827;",
            "data": "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5a6bd;strokeColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#111827;",
            "observability": "rounded=1;whiteSpace=wrap;html=1;fillColor=#d9d9d9;strokeColor=none;align=center;verticalAlign=middle;fontSize=12;fontColor=#111827;",
        }
        return tile_styles[category]

    def _drawio_safe_id(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
        return normalized or "section"

    def _drawio_edge_anchor_style(self, source: str, target: str, node_ids: dict[str, str]) -> str:
        node_keys = {value: key for key, value in node_ids.items()}
        source_key = node_keys.get(source)
        target_key = node_keys.get(target)
        anchor_map = {
            ("users", "web"): "exitX=1;exitY=0.5;entryX=0;entryY=0.35;",
            ("partners", "web"): "exitX=1;exitY=0.5;entryX=0;entryY=0.75;",
            ("web", "frontend"): "exitX=1;exitY=0.7;entryX=0;entryY=0.35;",
            ("edge", "frontend"): "exitX=0.5;exitY=1;entryX=0.35;entryY=0;",
            ("aem", "frontend"): "exitX=0;exitY=0.6;entryX=1;entryY=0.2;",
            ("aem_assets", "aem"): "exitX=0.5;exitY=0;entryX=0.5;entryY=1;",
            ("commerce", "frontend"): "exitX=0;exitY=0.2;entryX=0.5;entryY=1;",
            ("personalization", "frontend"): "exitX=0;exitY=0.5;entryX=0.5;entryY=1;",
            ("target", "personalization"): "exitX=0;exitY=0.5;entryX=1;entryY=0.35;",
            ("dynamic_media", "frontend"): "exitX=0;exitY=0.5;entryX=1;entryY=0.65;",
            ("frontend", "entra"): "exitX=1;exitY=0.1;entryX=0;entryY=0.5;",
            ("entra", "apim"): "exitX=1;exitY=0.5;entryX=0;entryY=0.25;",
            ("frontend", "apim"): "exitX=1;exitY=0.5;entryX=0;entryY=0.7;",
            ("apim", "orchestration"): "exitX=1;exitY=0.5;entryX=0;entryY=0.5;",
            ("orchestration", "service_bus"): "exitX=0.5;exitY=1;entryX=0.5;entryY=0;",
            ("orchestration", "domain_services"): "exitX=1;exitY=0.45;entryX=0;entryY=0.45;",
            ("service_bus", "microservices"): "exitX=1;exitY=0.5;entryX=0;entryY=0.5;",
            ("domain_services", "sap"): "exitX=1;exitY=0.25;entryX=0;entryY=0.45;",
            ("domain_services", "salesforce"): "exitX=1;exitY=0.5;entryX=0;entryY=0.5;",
            ("domain_services", "martech"): "exitX=1;exitY=0.8;entryX=0;entryY=0.5;",
            ("domain_services", "canonical_data"): "exitX=0.4;exitY=1;entryX=0.5;entryY=0;",
            ("canonical_data", "customer_profile"): "exitX=1;exitY=0.5;entryX=0;entryY=0.5;",
            ("canonical_data", "search_index"): "exitX=1;exitY=0.75;entryX=0;entryY=0.25;",
            ("canonical_data", "analytics"): "exitX=1;exitY=0.3;entryX=0;entryY=0.3;",
            ("adobe_analytics", "analytics"): "exitX=1;exitY=0.3;entryX=0.2;entryY=1;",
            ("aep", "customer_profile"): "exitX=0.5;exitY=0;entryX=0.5;entryY=1;",
            ("rt_cdp", "customer_profile"): "exitX=0.5;exitY=0;entryX=0.8;entryY=1;",
            ("azure_cloud", "analytics"): "exitX=0.5;exitY=0;entryX=0.8;entryY=1;",
            ("gcp_cloud", "analytics"): "exitX=0;exitY=0.4;entryX=1;entryY=0.8;",
            ("analytics", "personalization"): "exitX=0;exitY=0.15;entryX=1;entryY=0.85;",
            ("apim", "monitor"): "exitX=0.7;exitY=1;entryX=0.5;entryY=0;",
            ("canonical_data", "governance"): "exitX=1;exitY=1;entryX=0;entryY=0.3;",
        }
        return anchor_map.get((source_key, target_key), "")
