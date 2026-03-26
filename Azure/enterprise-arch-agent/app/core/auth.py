from __future__ import annotations

from azure.identity import ClientSecretCredential, DefaultAzureCredential, ManagedIdentityCredential

from app.core.config import Settings


def build_credential(settings: Settings):
    if settings.azure_auth_mode == "service_principal":
        return ClientSecretCredential(
            tenant_id=settings.azure_tenant_id,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret,
        )

    if settings.azure_auth_mode == "managed_identity":
        return ManagedIdentityCredential(client_id=settings.azure_managed_identity_client_id)

    return DefaultAzureCredential()
