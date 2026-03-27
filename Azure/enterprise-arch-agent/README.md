# Enterprise Architecture AI Agent

A runnable starter project for an **Enterprise Architecture AI Agent** built with:

- Python 3.11
- FastAPI
- Azure AI Projects SDK
- Azure Identity
- Azure OpenAI-compatible responses API (through Azure AI Project client)
- Azure Cosmos DB / Table Storage / Blob Storage support for agent memory
- Docker

## What this agent does

It accepts an enterprise architecture prompt such as:

> Design a target architecture for a global retailer using AEM, Adobe Commerce, SAP S/4HANA, Salesforce, and Azure API Management.

It then returns a structured recommendation with:

1. Business Context
2. Architecture Overview
3. Core Systems
4. Integration Patterns
5. Security & Identity
6. Data Flow
7. Non-Functional Requirements
8. Risks & Assumptions
9. Recommended Delivery Phases

It also generates enterprise delivery artifacts:

- Mermaid flow diagram
- draw.io XML that can be imported into diagrams.net / draw.io

It can also persist memory for:

- architecture request history
- reusable patterns
- prior recommendations
- versioned outputs

## Project structure

```text
enterprise-arch-agent/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── agent.py                  # compatibility wrapper around the agent class
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py             # FastAPI routes
│   ├── agents/
│   │   ├── __init__.py
│   │   └── enterprise_architecture.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # environment-backed settings
│   │   └── logging.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── architecture_analysis.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── system.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── architecture.py       # request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   └── azure_ai_project.py   # Azure AI Project client access
│   ├── models.py                 # compatibility re-export
│   ├── prompts.py                # compatibility re-export
│   └── tools.py                  # compatibility re-export
│
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## Module responsibilities

- `app/api`: HTTP contract and route handlers
- `app/agents`: AI agent orchestration and prompt assembly
- `app/services`: infrastructure clients and external service integration
- `app/services/diagram_generator.py`: Mermaid and draw.io XML generation from the architecture response
- `app/services/memory_store.py`: persistence-backed agent memory using Cosmos DB, Table Storage, or Blob Storage
- `app/domain`: enterprise architecture heuristics and analysis helpers
- `app/schemas`: Pydantic request/response models
- `app/core`: runtime configuration and logging bootstrap
- `app/prompts`: reusable system prompts and prompt assets

## Prerequisites

- Python 3.11+
- VS Code
- Azure CLI
- An Azure AI Foundry / Azure AI Project
- A deployed model in that project
- Local Azure login via:

```bash
az login
```

## 1. Clone or unzip the project

Open the folder in VS Code.

## 2. Create a virtual environment

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Set:

- `PROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT_NAME`
- `AZURE_AUTH_MODE`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `MEMORY_BACKEND`
- `MEMORY_CONNECTION_STRING`

Example:

```env
PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
MODEL_DEPLOYMENT_NAME=gpt-4.1
APP_ENV=local
LOG_LEVEL=INFO
AZURE_AUTH_MODE=service_principal
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
MEMORY_BACKEND=blob
MEMORY_CONNECTION_STRING=<azure-connection-string>
MEMORY_BLOB_CONTAINER_NAME=architecture-memory
```

## 5. Run locally

```bash
uvicorn app.main:app --reload
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 6. Test the agent

Sample JSON for `POST /analyze`:

```json
{
  "prompt": "Create an enterprise architecture for a global retail company using AEM, Adobe Commerce, SAP S/4HANA, Salesforce, and Azure API Management. Include integrations, security, non-functional requirements, and phased roadmap."
}
```

Sample response fields:

```json
{
  "result": "...",
  "detected_domains": "Adobe Experience Manager, eCommerce, ERP, CRM, API Integration, Global Platform, Retail Domain",
  "suggested_azure_services": [
    "Azure AI Foundry",
    "Azure Container Apps",
    "Azure Monitor",
    "Azure API Management"
  ],
  "memory_record_id": "3ce3a640-0b2e-40f7-b0d7-a469b5f8e0c0",
  "memory_backend": "blob",
  "prior_recommendations": [
    "Use API-led integration between commerce and ERP..."
  ],
  "reusable_patterns": [
    "Synchronous APIs for customer-facing real-time interactions via Azure API Management"
  ],
  "mermaid_diagram": "flowchart LR\n    N1[\"Users / Channels\"]\n    ...",
  "drawio_xml": "<mxfile host=\"app.diagrams.net\">...</mxfile>"
}
```

## Agent memory backends

Use `MEMORY_BACKEND` to choose how the agent stores history and versioned outputs:

- `none`: disable persistence
- `cosmos`: store records in Azure Cosmos DB
- `table`: store records in Azure Table Storage
- `blob`: store JSON files in Azure Blob Storage

Example memory settings:

```env
MEMORY_BACKEND=cosmos
MEMORY_CONNECTION_STRING=<cosmos-connection-string>
MEMORY_DATABASE_NAME=enterprise-arch-agent
MEMORY_CONTAINER_NAME=architecture-memory
```

```env
MEMORY_BACKEND=table
MEMORY_CONNECTION_STRING=<storage-account-connection-string>
MEMORY_TABLE_NAME=ArchitectureMemory
```

```env
MEMORY_BACKEND=blob
MEMORY_CONNECTION_STRING=<storage-account-connection-string>
MEMORY_BLOB_CONTAINER_NAME=architecture-memory
```

## Docker

Build:

```bash
docker build -t enterprise-arch-agent:1.0 .
```

Run:

```bash
docker run --env-file .env -p 8000:8000 enterprise-arch-agent:1.0
```

### Docker authentication

`DefaultAzureCredential()` inside a local Docker container does not reuse your host `az login`. For local containers, use a Microsoft Entra service principal:

```env
AZURE_AUTH_MODE=service_principal
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
```

If you deploy this container to Azure with Managed Identity, set:

```env
AZURE_AUTH_MODE=managed_identity
AZURE_MANAGED_IDENTITY_CLIENT_ID=<optional-user-assigned-mi-client-id>
```

## Example curl command

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Design an enterprise architecture for a healthcare platform using AEM, Salesforce, SAP, and Azure integration services."}'
```

## Notes

- Local authentication uses `DefaultAzureCredential()`.
- For Docker, prefer `AZURE_AUTH_MODE=service_principal` unless the container is running on Azure with Managed Identity.
- In Azure-hosted deployment, prefer **Managed Identity** and assign appropriate RBAC permissions to the Azure AI Project / resource.
- This starter version uses internal Python helper tools for domain classification and Azure service suggestions.
- This version also creates Mermaid and draw.io artifacts from the generated architecture narrative.
- This version can also persist request and response history as agent memory using Cosmos DB, Table Storage, or Blob Storage.
- A later version can add:
  - Azure Monitor tracing
  - Hosted tool/function calling
