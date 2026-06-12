from __future__ import annotations

import os
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from mike.application.ports.llm_reasoning_port import CoverageReasoningPort
from mike.domain.enums import CitationRole, CoverageDecision, CoverageRiskCategory, RiskSeverity
from mike.domain.models import (
    ClaimCitationLink,
    CoverageAnswerDraft,
    CoverageCitation,
    CoverageQuestion,
    CoverageRisk,
    EvidencePackage,
)


class GeminiCoverageReasoningAdapter(CoverageReasoningPort):
    def __init__(self) -> None:
        self._model_name = "gemini-2.5-flash"
        self._prompt_version = "coverage_eval_v1"

    def _fallback_answer(self, question: CoverageQuestion, evidence: EvidencePackage) -> CoverageAnswerDraft:
        citations: list[CoverageCitation] = []
        claim_map: list[ClaimCitationLink] = []
        for idx, chunk in enumerate(evidence.selected_chunks[:2]):
            citation_id = f"cit_{idx+1}"
            citations.append(
                CoverageCitation(
                    citation_id=citation_id,
                    document_id=chunk.document_id,
                    chunk_id=chunk.chunk_id,
                    heading=chunk.heading,
                    subsection=chunk.subsection,
                    page_number=chunk.page_number,
                    quoted_text=chunk.chunk_text[:300],
                    citation_role=CitationRole.SUPPORTS_UNCERTAINTY,
                    relevance_note="Fallback synthesis due to unavailable LLM execution context.",
                )
            )
            claim_map.append(ClaimCitationLink(claim_id=f"claim_{idx+1}", citation_ids=[citation_id]))

        no_evidence = len(evidence.selected_chunks) == 0
        decision = CoverageDecision.CANNOT_DETERMINE_FROM_POLICY if no_evidence else CoverageDecision.CONDITIONALLY_COVERED
        short_answer = (
            "Cannot determine from policy evidence currently available."
            if no_evidence
            else "Policy includes related clauses, but determination remains conditional on the cited terms."
        )

        risks: list[CoverageRisk] = []
        if citations:
            risks.append(
                CoverageRisk(
                    category=CoverageRiskCategory.POLICY_AMBIGUITY_RISK,
                    severity=RiskSeverity.MEDIUM,
                    statement="Policy language appears conditional and may lead to denial if requirements are unmet.",
                    triggering_conditions=["Missing referral or authorization details"],
                    mitigation_steps=["Verify plan conditions with insurer before receiving care"],
                    citations=[citations[0]],
                )
            )

        return CoverageAnswerDraft(
            decision=decision,
            short_answer=short_answer,
            detailed_reasoning=(
                "This response is grounded only in retrieved policy chunks. "
                "No external insurance assumptions were used."
            ),
            conditions=["Coverage determination depends on cited policy conditions."],
            next_steps=["Provide more scenario details and retrieve additional policy sections."],
            evidence_summary="Evidence synthesized from retrieved chunks only.",
            supporting_citations=citations,
            contradicting_citations=[],
            unresolved_ambiguities=evidence.evidence_gaps,
            missing_information_needed=evidence.diagnostics.missing_key_terms,
            risks=risks,
            claim_to_citation_map=claim_map,
        )

    def evaluate(self, question: CoverageQuestion, evidence: EvidencePackage) -> CoverageAnswerDraft:
        # Fail closed: no evidence means no decision.
        if not evidence.selected_chunks:
            return self._fallback_answer(question, evidence)

        # If API key is absent, fallback remains policy-grounded and deterministic.
        if not os.getenv("GOOGLE_API_KEY"):
            return self._fallback_answer(question, evidence)

        llm = ChatGoogleGenerativeAI(model=self._model_name, temperature=0.0, max_retries=1)
        structured_llm = llm.with_structured_output(CoverageAnswerDraft)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are Mike Coverage Evaluator.
You MUST reason ONLY from provided evidence chunks.
Do not use general insurance knowledge.
If evidence is insufficient, return decision='cannot_determine_from_policy'.
Every claim must map to citations.
""".strip(),
                ),
                (
                    "human",
                    "Question: {question}\n\nEvidence JSON: {evidence_json}",
                ),
            ]
        )

        chain = prompt | structured_llm
        result: Any = chain.invoke(
            {
                "question": question.question_text,
                "evidence_json": evidence.model_dump_json(),
            }
        )
        if isinstance(result, CoverageAnswerDraft):
            return result
        return CoverageAnswerDraft.model_validate(result)
