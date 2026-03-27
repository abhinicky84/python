from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import json
import logging
import re
from typing import Any
from uuid import uuid4

from azure.cosmos import CosmosClient, PartitionKey
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

from app.core.config import get_settings
from app.schemas.architecture import AnalyzeResponse, ArchitectureAnalysis, MemoryContext, MemoryRecord

logger = logging.getLogger(__name__)


class BaseMemoryStore(ABC):
    backend_name = "none"

    @abstractmethod
    def recall(self, user_input: str, analysis: ArchitectureAnalysis) -> MemoryContext:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        user_input: str,
        analysis: ArchitectureAnalysis,
        response: AnalyzeResponse,
    ) -> str | None:
        raise NotImplementedError

    def build_record(
        self,
        user_input: str,
        analysis: ArchitectureAnalysis,
        response: AnalyzeResponse,
    ) -> MemoryRecord:
        timestamp = datetime.now(tz=UTC)
        partition_key = self._partition_key(analysis)
        reusable_patterns = self._extract_patterns(analysis, response.result)
        return MemoryRecord(
            id=str(uuid4()),
            partition_key=partition_key,
            created_at=timestamp.isoformat(),
            version=timestamp.strftime("v%Y%m%d%H%M%S"),
            request_prompt=user_input,
            result=response.result,
            detected_domains=analysis.detected_domains,
            suggested_azure_services=response.suggested_azure_services,
            mermaid_diagram=response.mermaid_diagram,
            drawio_xml=response.drawio_xml,
            reusable_patterns=reusable_patterns,
            prior_recommendation_summary=self._summarize_response(response.result),
        )

    def _partition_key(self, analysis: ArchitectureAnalysis) -> str:
        first_domain = analysis.detected_domains.split(",")[0].strip().lower()
        return re.sub(r"[^a-z0-9]+", "-", first_domain).strip("-") or "general-enterprise-architecture"

    def _extract_patterns(self, analysis: ArchitectureAnalysis, response_text: str) -> list[str]:
        patterns = [
            line.strip("- ").strip()
            for line in analysis.integration_guidance.splitlines()
            if line.strip().startswith("-")
        ]
        response_patterns = re.findall(r"(?:synchronous|asynchronous|event-driven|batch)[^.:\n]{0,100}", response_text, flags=re.IGNORECASE)
        combined = patterns + [pattern.strip(" -.") for pattern in response_patterns]
        deduped: list[str] = []
        seen: set[str] = set()
        for item in combined:
            normalized = item.strip()
            if not normalized:
                continue
            key = normalized.casefold()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(normalized)
        return deduped[:8]

    def _summarize_response(self, response_text: str) -> str:
        compact = re.sub(r"\s+", " ", response_text).strip()
        return compact[:320]

    def _memory_context_from_records(self, records: list[MemoryRecord]) -> MemoryContext:
        recommendations = [record.prior_recommendation_summary for record in records[:3]]
        patterns: list[str] = []
        seen: set[str] = set()
        for record in records:
            for pattern in record.reusable_patterns:
                key = pattern.casefold()
                if key in seen:
                    continue
                seen.add(key)
                patterns.append(pattern)
        return MemoryContext(
            backend=self.backend_name,
            prior_recommendations=recommendations,
            reusable_patterns=patterns[:8],
        )


class NullMemoryStore(BaseMemoryStore):
    backend_name = "none"

    def recall(self, user_input: str, analysis: ArchitectureAnalysis) -> MemoryContext:
        return MemoryContext(backend=self.backend_name)

    def save(
        self,
        user_input: str,
        analysis: ArchitectureAnalysis,
        response: AnalyzeResponse,
    ) -> str | None:
        return None


class CosmosMemoryStore(BaseMemoryStore):
    backend_name = "cosmos"

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.memory_connection_string or not settings.memory_database_name or not settings.memory_container_name:
            raise ValueError("Cosmos memory requires MEMORY_CONNECTION_STRING, MEMORY_DATABASE_NAME, and MEMORY_CONTAINER_NAME.")
        client = CosmosClient.from_connection_string(settings.memory_connection_string)
        database = client.create_database_if_not_exists(settings.memory_database_name)
        self.container = database.create_container_if_not_exists(
            id=settings.memory_container_name,
            partition_key=PartitionKey(path="/partition_key"),
        )

    def recall(self, user_input: str, analysis: ArchitectureAnalysis) -> MemoryContext:
        partition_key = self._partition_key(analysis)
        query = (
            "SELECT TOP 5 c.id, c.partition_key, c.created_at, c.version, c.request_prompt, c.result, "
            "c.detected_domains, c.suggested_azure_services, c.mermaid_diagram, c.drawio_xml, "
            "c.reusable_patterns, c.prior_recommendation_summary "
            "FROM c WHERE c.partition_key = @pk ORDER BY c.created_at DESC"
        )
        records = [
            MemoryRecord.model_validate(item)
            for item in self.container.query_items(
                query=query,
                parameters=[{"name": "@pk", "value": partition_key}],
                enable_cross_partition_query=True,
            )
        ]
        return self._memory_context_from_records(records)

    def save(
        self,
        user_input: str,
        analysis: ArchitectureAnalysis,
        response: AnalyzeResponse,
    ) -> str | None:
        record = self.build_record(user_input, analysis, response)
        self.container.upsert_item(record.model_dump())
        return record.id


class TableMemoryStore(BaseMemoryStore):
    backend_name = "table"

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.memory_connection_string or not settings.memory_table_name:
            raise ValueError("Table memory requires MEMORY_CONNECTION_STRING and MEMORY_TABLE_NAME.")
        service = TableServiceClient.from_connection_string(settings.memory_connection_string)
        self.table = service.create_table_if_not_exists(table_name=settings.memory_table_name)

    def recall(self, user_input: str, analysis: ArchitectureAnalysis) -> MemoryContext:
        partition_key = self._partition_key(analysis)
        entities = list(
            self.table.query_entities(
                query_filter="PartitionKey eq @partition",
                parameters={"partition": partition_key},
            )
        )
        entities.sort(key=lambda item: item["created_at"], reverse=True)
        records = [self._record_from_entity(entity) for entity in entities[:5]]
        return self._memory_context_from_records(records)

    def save(
        self,
        user_input: str,
        analysis: ArchitectureAnalysis,
        response: AnalyzeResponse,
    ) -> str | None:
        record = self.build_record(user_input, analysis, response)
        entity = {
            "PartitionKey": record.partition_key,
            "RowKey": record.id,
            "created_at": record.created_at,
            "version": record.version,
            "request_prompt": record.request_prompt,
            "result": record.result,
            "detected_domains": record.detected_domains,
            "suggested_azure_services": json.dumps(record.suggested_azure_services),
            "mermaid_diagram": record.mermaid_diagram,
            "drawio_xml": record.drawio_xml,
            "reusable_patterns": json.dumps(record.reusable_patterns),
            "prior_recommendation_summary": record.prior_recommendation_summary,
        }
        self.table.upsert_entity(mode="MERGE", entity=entity)
        return record.id

    def _record_from_entity(self, entity: dict[str, Any]) -> MemoryRecord:
        return MemoryRecord(
            id=entity["RowKey"],
            partition_key=entity["PartitionKey"],
            created_at=entity["created_at"],
            version=entity["version"],
            request_prompt=entity["request_prompt"],
            result=entity["result"],
            detected_domains=entity["detected_domains"],
            suggested_azure_services=json.loads(entity["suggested_azure_services"]),
            mermaid_diagram=entity["mermaid_diagram"],
            drawio_xml=entity["drawio_xml"],
            reusable_patterns=json.loads(entity["reusable_patterns"]),
            prior_recommendation_summary=entity["prior_recommendation_summary"],
        )


class BlobMemoryStore(BaseMemoryStore):
    backend_name = "blob"

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.memory_connection_string or not settings.memory_blob_container_name:
            raise ValueError("Blob memory requires MEMORY_CONNECTION_STRING and MEMORY_BLOB_CONTAINER_NAME.")
        service = BlobServiceClient.from_connection_string(settings.memory_connection_string)
        self.container = service.get_container_client(settings.memory_blob_container_name)
        try:
            self.container.create_container()
        except ResourceExistsError:
            pass

    def recall(self, user_input: str, analysis: ArchitectureAnalysis) -> MemoryContext:
        prefix = f"{self._partition_key(analysis)}/"
        blobs = sorted(self.container.list_blobs(name_starts_with=prefix), key=lambda item: item.name, reverse=True)
        records: list[MemoryRecord] = []
        for blob in blobs[:5]:
            payload = self.container.download_blob(blob.name).readall().decode("utf-8")
            records.append(MemoryRecord.model_validate_json(payload))
        return self._memory_context_from_records(records)

    def save(
        self,
        user_input: str,
        analysis: ArchitectureAnalysis,
        response: AnalyzeResponse,
    ) -> str | None:
        record = self.build_record(user_input, analysis, response)
        blob_name = f"{record.partition_key}/{record.version}-{record.id}.json"
        self.container.upload_blob(blob_name, record.model_dump_json(indent=2), overwrite=True)
        return record.id


def build_memory_store() -> BaseMemoryStore:
    settings = get_settings()
    backend = settings.memory_backend
    try:
        if backend == "cosmos":
            return CosmosMemoryStore()
        if backend == "table":
            return TableMemoryStore()
        if backend == "blob":
            return BlobMemoryStore()
    except Exception as exc:
        logger.warning("Falling back to null memory store: %s", exc)
    return NullMemoryStore()
