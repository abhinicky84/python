from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "Enterprise Architecture AI Agent"
    app_version: str = "1.0.0"
    app_env: str = os.getenv("APP_ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    project_endpoint: str | None = os.getenv("PROJECT_ENDPOINT")
    model_deployment_name: str | None = os.getenv("MODEL_DEPLOYMENT_NAME")
    azure_auth_mode: str = os.getenv("AZURE_AUTH_MODE", "default").lower()
    azure_tenant_id: str | None = os.getenv("AZURE_TENANT_ID")
    azure_client_id: str | None = os.getenv("AZURE_CLIENT_ID")
    azure_client_secret: str | None = os.getenv("AZURE_CLIENT_SECRET")
    azure_managed_identity_client_id: str | None = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
    memory_backend: str = os.getenv("MEMORY_BACKEND", "none").lower()
    memory_connection_string: str | None = os.getenv("MEMORY_CONNECTION_STRING")
    memory_database_name: str = os.getenv("MEMORY_DATABASE_NAME", "enterprise-arch-agent")
    memory_container_name: str = os.getenv("MEMORY_CONTAINER_NAME", "architecture-memory")
    memory_table_name: str = os.getenv("MEMORY_TABLE_NAME", "ArchitectureMemory")
    memory_blob_container_name: str = os.getenv("MEMORY_BLOB_CONTAINER_NAME", "architecture-memory")

    def validate_runtime(self) -> None:
        if not self.project_endpoint:
            raise ValueError("PROJECT_ENDPOINT is missing. Set it in your .env file.")
        if not self.model_deployment_name:
            raise ValueError("MODEL_DEPLOYMENT_NAME is missing. Set it in your .env file.")
        if self.azure_auth_mode not in {"default", "service_principal", "managed_identity"}:
            raise ValueError("AZURE_AUTH_MODE must be one of: default, service_principal, managed_identity.")
        if self.azure_auth_mode == "service_principal":
            missing = [
                name
                for name, value in (
                    ("AZURE_TENANT_ID", self.azure_tenant_id),
                    ("AZURE_CLIENT_ID", self.azure_client_id),
                    ("AZURE_CLIENT_SECRET", self.azure_client_secret),
                )
                if not value
            ]
            if missing:
                raise ValueError(
                    "Service principal auth is enabled but these variables are missing: "
                    + ", ".join(missing)
                )
        if self.memory_backend not in {"none", "cosmos", "table", "blob"}:
            raise ValueError("MEMORY_BACKEND must be one of: none, cosmos, table, blob.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
