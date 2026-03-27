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
        "channels": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff7d6;strokeColor=#d97706;",
        "experience": "rounded=1;whiteSpace=wrap;html=1;fillColor=#edf5ff;strokeColor=#2563eb;",
        "identity": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f3ff;strokeColor=#7c3aed;",
        "integration": "rounded=1;whiteSpace=wrap;html=1;fillColor=#eafcf0;strokeColor=#16a34a;fontStyle=1;",
        "applications": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fdf0ff;strokeColor=#c026d3;",
        "systems": "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff1f2;strokeColor=#dc2626;",
        "data": "rounded=1;whiteSpace=wrap;html=1;fillColor=#ecfeff;strokeColor=#0891b2;",
        "observability": "rounded=1;whiteSpace=wrap;html=1;fillColor=#f3f4f6;strokeColor=#4b5563;",
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

        if self._mentions_any(text, ["aem", "content", "cms", "experience"]):
            self._add_node(nodes, "aem", "AEM", "experience")
        if self._mentions_any(text, ["adobe commerce", "commerce", "storefront", "cart", "checkout"]):
            self._add_node(nodes, "commerce", "Adobe Commerce", "experience")
        if not any(node.category == "experience" for node in nodes):
            self._add_node(nodes, "portal", "Digital Experience Portal", "experience")

        self._add_node(nodes, "entra", "Microsoft Entra ID", "identity")
        if self._mentions_any(text, ["private", "network", "private endpoint", "private link", "vnet", "secure"]):
            self._add_node(nodes, "network", "Private Network Boundary", "identity")

        self._add_node(nodes, "apim", "Azure API Management", "integration")
        if self._mentions_any(text, ["event", "async", "messaging", "queue", "service bus"]):
            self._add_node(nodes, "service_bus", "Azure Service Bus", "integration")
        self._add_node(nodes, "orchestration", "Integration Orchestration", "integration")

        if self._contains_service(analysis, "Azure Container Apps"):
            self._add_node(nodes, "container_apps", "Azure Container Apps", "applications")
        if self._contains_service(analysis, "Azure Kubernetes Service"):
            self._add_node(nodes, "aks", "Azure Kubernetes Service", "applications")
        self._add_node(nodes, "domain_services", "Domain Services", "applications")
        if self._contains_service(analysis, "Azure AI Foundry"):
            self._add_node(nodes, "ai_foundry", "Azure AI Foundry", "applications")

        if self._mentions_any(text, ["sap"]):
            self._add_node(nodes, "sap", self._extract_sap_label(text), "systems")
        if self._mentions_any(text, ["salesforce"]):
            self._add_node(nodes, "salesforce", "Salesforce", "systems")
        if self._mentions_any(text, ["erp", "crm", "backend", "line of business"]) and len(
            [node for node in nodes if node.category == "systems"]
        ) < 2:
            self._add_node(nodes, "lob", "Line-of-Business Systems", "systems")

        if self._contains_any_service(analysis, ["Azure Storage or Cosmos DB", "Azure Storage", "Cosmos DB"]):
            self._add_node(nodes, "operational_data", "Operational Data Store", "data")
        self._add_node(nodes, "canonical_data", "Canonical Data Model", "data")
        if self._contains_any_service(analysis, ["Azure Data Lake / Synapse / Fabric", "Synapse", "Fabric"]):
            self._add_node(nodes, "analytics", "Analytics & Reporting", "data")

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

        for experience in self._node_keys(nodes, "experience"):
            connect("web", experience, "UX / Content")
            connect(experience, "entra", "SSO / Session")
            connect(experience, "apim", "Experience APIs")

        connect("entra", "apim", "AuthN / Tokens")
        connect("network", "apim", "Private Access")
        connect("apim", "orchestration", "Policy / Routing")
        connect("orchestration", "domain_services", "Service Composition")
        connect("orchestration", "service_bus", "Events")
        connect("service_bus", "domain_services", "Async Commands")
        connect("domain_services", "container_apps", "Runtime")
        connect("domain_services", "aks", "Runtime")
        connect("domain_services", "ai_foundry", "AI Enrichment")
        connect("domain_services", "operational_data", "Transactional Data")
        connect("domain_services", "canonical_data", "Canonical Events")
        connect("service_bus", "canonical_data", "Event Stream")

        for system in self._node_keys(nodes, "systems"):
            connect("orchestration", system, "API / Event Integration")
            connect(system, "canonical_data", "Master Data")

        connect("operational_data", "analytics", "Batch / CDC")
        connect("canonical_data", "analytics", "Analytics Feed")
        connect("analytics", "web", "Insights / Reporting")

        for observable in ("apim", "orchestration", "domain_services", "service_bus", "container_apps", "aks"):
            connect(observable, "monitor", "Telemetry", style="dashed")
        for governed in ("entra", "apim", "canonical_data", "analytics"):
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
        lines = [
            '<mxfile host="app.diagrams.net">',
            '  <diagram id="enterprise-architecture" name="Enterprise Architecture">',
            '    <mxGraphModel dx="1600" dy="960" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2200" pageHeight="1400" math="0" shadow="0">',
            "      <root>",
            '        <mxCell id="0" />',
            '        <mxCell id="1" parent="0" />',
        ]

        lane_ids: dict[str, str] = {}
        node_ids: dict[str, str] = {}
        lane_x = 40
        lane_y = 80
        lane_width = 2000
        lane_height = 130
        lane_gap = 20

        for index, category in enumerate(self.CATEGORY_ORDER):
            category_nodes = [node for node in nodes if node.category == category]
            if not category_nodes:
                continue
            lane_id = f"lane-{category}"
            lane_ids[category] = lane_id
            y = lane_y + (index * (lane_height + lane_gap))
            lines.extend(
                [
                    f'        <mxCell id="{lane_id}" value="{escape(self.CATEGORY_LABELS[category])}" style="{self.DRAWIO_LANE_STYLES[category]}" vertex="1" parent="1">',
                    f'          <mxGeometry x="{lane_x}" y="{y}" width="{lane_width}" height="{lane_height}" as="geometry" />',
                    "        </mxCell>",
                ]
            )

            node_width = 210
            node_height = 54
            node_gap = 22
            start_x = 70
            for node_index, node in enumerate(category_nodes):
                cell_id = f"node-{node.key}"
                node_ids[node.key] = cell_id
                x = start_x + (node_index * (node_width + node_gap))
                lines.extend(
                    [
                        f'        <mxCell id="{cell_id}" value="{escape(node.label)}" style="{self.DRAWIO_NODE_STYLES[category]}" vertex="1" parent="{lane_id}">',
                        f'          <mxGeometry x="{x}" y="48" width="{node_width}" height="{node_height}" as="geometry" />',
                        "        </mxCell>",
                    ]
                )

        for edge_index, edge in enumerate(edges, start=1):
            if edge.source not in node_ids or edge.target not in node_ids:
                continue
            style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;"
            )
            if edge.style == "dashed":
                style += "dashed=1;"
            lines.extend(
                [
                    f'        <mxCell id="edge-{edge_index}" value="{escape(edge.label)}" style="{style}" edge="1" parent="1" source="{node_ids[edge.source]}" target="{node_ids[edge.target]}">',
                    '          <mxGeometry relative="1" as="geometry" />',
                    "        </mxCell>",
                ]
            )

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
