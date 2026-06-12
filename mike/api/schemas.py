from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from mike.domain.enums import DecisionType


class CoverageQuestionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(min_length=3, max_length=4000)
    scenario_context: dict[str, str] | None = None
    requested_decision_type: DecisionType = DecisionType.COVERAGE
    session_id: UUID | None = None
    client_request_id: str | None = None


class CoverageEvaluationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluation_id: UUID
    processing_status: str
    answer: dict[str, Any]
    confidence: dict[str, Any]
    citations: list[dict[str, Any]]
    audit_ref: dict[str, Any]


class PolicyIngestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: str
    version: str
    filename: str
    ingested_at: str
    markdown_chunk_count: int
    total_chunk_count: int
    summary_generated: bool


class PolicyPathIngestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_path: str = Field(min_length=1)
    policy_version: str = Field(default="v1", min_length=1)
