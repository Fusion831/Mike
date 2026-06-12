from __future__ import annotations

import getpass
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from mike.models import (
    CitationRole,
    ClaimCitationLink,
    ConfidenceLevel,
    CoverageAnswerDraft,
    CoverageDecision,
    CoverageQuestion,
    CoverageCitation,
    CoverageRisk,
    CoverageRiskCategory,
    EvidencePackage,
    PolicySummary,
    RiskSeverity,
)

# Load env variables and ensure API key setup
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    # Safe non-interactive fallback for environment check
    pass


async def generate_policy_summary(markdown_text: str) -> PolicySummary:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        max_retries=2,
    )
    structured_llm = llm.with_structured_output(PolicySummary)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are Mike, an elite health insurance advocate.

Your job is not to summarize the insurance policy.
If a field cannot be determined from the document, populate it with "Not explicitly defined" rather than leaving it blank.
Your job is to extract the information that a policyholder would need before speaking with an insurance representative and return it using the provided schema.

CORE PRINCIPLES

* Extract information only from the provided document.
* Never invent facts.
* Never invent monetary amounts.
* Never invent exclusions.
* Never invent prior authorization requirements.
* Never invent referral rules.
* Never invent citations.
* If information is not explicitly stated, return "Not explicitly defined".
* If information cannot be located, return "Citation unavailable in source text" for the citation field.

DOCUMENT INTERPRETATION RULES

Insurance policies often contain summaries, benefit tables, riders, amendments, and detailed coverage sections.

When multiple versions of a rule appear:

1. Prefer detailed coverage language over summary language.
2. Prefer amendments, riders, and updates over older language.
3. Prefer the most specific rule available.
4. If two sections genuinely conflict, explain the conflict in the relevant field rather than choosing one without explanation.

OVERVIEW SECTION

For the ELI5 summary:

* Use plain English.
* Avoid insurance jargon whenever possible.
* Explain how the plan works.
* Explain who the plan is best suited for.
* Explain the largest financial risk the policyholder carries.
* Keep the explanation to approximately three sentences.

NETWORK ANALYSIS

Determine:

* Whether the plan is HMO, PPO, EPO, POS, HDHP, or another structure.
* Whether specialist referrals are required.
* Whether out-of-network care is covered.
* Any major restrictions or exceptions.

FINANCIAL ANALYSIS

Extract:

* In-network deductible.
* Out-of-network deductible.
* Out-of-pocket maximum.
* Any important nuances such as:

  * Individual vs family limits.
  * Embedded vs aggregate deductibles.
  * Prescription drug exceptions.
  * Separate deductibles.
  * Network-specific rules.

ROUTINE CARE

Extract the policyholder cost and conditions for:

* Preventive care.
* Primary care visits.
* Specialist visits.

Include any deductible requirements, coinsurance requirements, visit limits, referral requirements, or prior authorization requirements.

EMERGENCY CARE

Extract the policyholder cost and conditions for:

* Emergency room services.
* Ambulance services.
* Urgent care services.

Clearly identify whether deductible requirements apply.

PRESCRIPTION DRUG ANALYSIS

Extract every explicitly defined prescription drug tier.

Include:

* Tier name.
* Cost sharing structure.
* Step therapy requirements.
* Quantity limits.
* Prior authorization requirements.
* Specialty drug restrictions.

If no tier structure exists, return an empty list.

PRIOR AUTHORIZATION ANALYSIS

Extract every explicitly stated prior authorization requirement.

Examples may include:

* MRI
* CT scans
* Physical therapy
* Durable medical equipment
* Specialty medications
* Surgical procedures

Only include requirements explicitly mentioned in the document.

Do not infer or guess.

EXCLUSION ANALYSIS

Extract every explicit exclusion found.

Examples may include:

* Cosmetic procedures
* Experimental treatments
* Adult dental
* Fertility treatment
* Weight-loss services

Only include exclusions explicitly stated in the document.

Do not infer or guess.

SCENARIO ANALYSIS

Create realistic medical scenarios based on the policy structure.

Examples:

* Broken arm requiring emergency care.
* Three-day hospital stay.
* Chronic condition requiring specialist visits.

IMPORTANT:

* Use assumptions when exact costs cannot be determined.
* Clearly state assumptions.
* Never present estimated costs as guaranteed costs.
* Base calculations only on information present in the policy.
* If insufficient information exists, explain why a reliable estimate cannot be produced.

DENIAL RISK ANALYSIS

Identify the most important claim denial risks found in the policy.

Prioritize:

1. Missing prior authorization.
2. Missing referrals.
3. Out-of-network treatment.
4. Filing deadlines.
5. Documentation requirements.
6. Prescription restrictions.
7. Coverage limitations.

For each risk:

* Explain how the denial occurs.
* Explain how the user can avoid it.
* Cite the source section.

OUTPUT REQUIREMENTS

* Return only information supported by the document.
* Be conservative.
* Missing information is preferable to fabricated information.
* When uncertain, explicitly indicate uncertainty.
* Populate every schema field.
* Ensure all citations reference actual document headings when available.
"""),
        ("human", "Here is the policy document:\n\n{document_text}")
    ])
    chain = prompt | structured_llm
    result = await chain.ainvoke({"document_text": markdown_text})
    return result


def _fallback_answer(question: CoverageQuestion, evidence: EvidencePackage) -> CoverageAnswerDraft:
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


def evaluate_coverage_reasoning(question: CoverageQuestion, evidence: EvidencePackage) -> CoverageAnswerDraft:
    # Fail closed: no evidence means no decision.
    if not evidence.selected_chunks:
        return _fallback_answer(question, evidence)

    # If API key is absent, fallback remains policy-grounded and deterministic.
    if not os.getenv("GOOGLE_API_KEY"):
        return _fallback_answer(question, evidence)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, max_retries=1)
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
