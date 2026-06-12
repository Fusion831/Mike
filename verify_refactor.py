import asyncio
import os
import sys
from uuid import UUID, uuid4
from dotenv import load_dotenv

# Ensure the workspace root is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment
load_dotenv()

# ==========================================
# Mock PyTorch/Docling and LangChain to avoid memory/network issues
# ==========================================
from unittest.mock import MagicMock, AsyncMock
import types

# 1. Mock mike.parser
mock_parser = types.ModuleType('mike.parser')
mock_parser.parse_pdf_to_markdown = AsyncMock(return_value="# Chapter 1\nThis is a test policy contract.\n## Section 1.1\nPhysical therapy is covered after surgery.")
from langchain_core.documents import Document
mock_parser.split_markdown_headers = AsyncMock(return_value=[
    Document(page_content="Physical therapy is covered after surgery.", metadata={"Section": "Section 1.1"})
])
sys.modules['mike.parser'] = mock_parser

# 2. Mock mike.llm
from mike.models import (
    PolicySummary, PlanOverview, Financials, FinancialDetail, RoutineCare, CareCost,
    EmergencyScenarios, DrugTier, PriorAuthorizationItem, CoverageExclusion, ScenarioExample, DenialRisk,
    CoverageAnswerDraft, CoverageDecision, CoverageCitation, CitationRole, ClaimCitationLink
)

mock_llm = types.ModuleType('mike.llm')

dummy_summary = PolicySummary(
    overview=PlanOverview(
        insurer_name="Test Insurer",
        plan_name="Test Plan",
        mikes_eli5_summary="ELI5 Summary",
        network_rules="HMO rules",
        specialist_referral_required=True,
        referral_details="Need referrals"
    ),
    financials=Financials(
        in_network_deductible=FinancialDetail(amount="$500", nuance="Per person"),
        out_of_network_deductible=FinancialDetail(amount="$1000", nuance="N/A"),
        out_of_pocket_max=FinancialDetail(amount="$3000", nuance="Individual")
    ),
    routine_care=RoutineCare(
        preventive_care=CareCost(cost="0%", conditions="Waived"),
        primary_care=CareCost(cost="$20", conditions="After deductible"),
        specialist=CareCost(cost="$40", conditions="Referral required")
    ),
    emergency_care=EmergencyScenarios(
        emergency_room=CareCost(cost="$250", conditions="No deductible"),
        ambulance=CareCost(cost="20%", conditions="Copay waived"),
        urgent_care=CareCost(cost="$50", conditions="Flat copay")
    ),
    drug_tiers=[
        DrugTier(tier_name="Tier 1", cost="$10", notes="Generic")
    ],
    prior_authorization_requirements=[
        PriorAuthorizationItem(service="Physical Therapy", details="Approved after surgery", citation="Section 1.1")
    ],
    excluded_services=[
        CoverageExclusion(exclusion="Cosmetic surgery", explanation="Not medically necessary", citation="Section 2")
    ],
    example_scenarios=[
        ScenarioExample(scenario="Broken arm", estimated_user_cost="$300", assumptions=["In network"], explanation="Calculated")
    ],
    denial_risks=[
        DenialRisk(risk="Out of network Specialist", explanation="HMO", prevention_tip="Stay in network", citation="Section 1")
    ]
)

dummy_draft = CoverageAnswerDraft(
    decision=CoverageDecision.CONDITIONALLY_COVERED,
    short_answer="Physical therapy is conditionally covered after surgery.",
    detailed_reasoning="Detailed reasoning text goes here.",
    conditions=["Prior authorization is required"],
    next_steps=["Get referral from PCP"],
    evidence_summary="Evidence summary text.",
    supporting_citations=[
        CoverageCitation(
            citation_id="cit_1",
            document_id="policy_doc_id",
            chunk_id="chunk_id_1",
            heading="Section 1.1",
            quoted_text="Physical therapy is covered after surgery.",
            citation_role=CitationRole.SUPPORTS_COVERAGE
        )
    ],
    contradicting_citations=[],
    unresolved_ambiguities=[],
    missing_information_needed=[],
    risks=[],
    claim_to_citation_map=[
        ClaimCitationLink(claim_id="claim_1", citation_ids=["cit_1"])
    ]
)

mock_llm.generate_policy_summary = AsyncMock(return_value=dummy_summary)
mock_llm.evaluate_coverage_reasoning = MagicMock(return_value=dummy_draft)
sys.modules['mike.llm'] = mock_llm

# ==========================================
# Start Verification
# ==========================================
print("Testing imports with mocks...")
from mike.models import CoverageQuestion, CoverageQuestionInput, DecisionType
from mike.storage import storage
from mike.services import PolicyIngestionService, CoverageEvaluationService
from main import app
print("Imports successful!")

async def test_services():
    print("\n--- Testing Core Services ---")
    
    # 1. Initialize Services
    ingestion = PolicyIngestionService(storage)
    evaluation = CoverageEvaluationService(storage)
    
    policy_id = uuid4()
    pdf_path = os.path.abspath(os.path.join("documents", "RandomFile.pdf"))
    
    # Register mock chunk in storage manually to avoid docling loading if files missing
    # But since docling is mocked, ingest_pdf_path will run successfully
    print(f"Ingesting PDF from path: {pdf_path} for policy: {policy_id}...")
    
    try:
        # 2. Ingest
        ingest_result = await ingestion.ingest_pdf_path(
            policy_id=policy_id,
            file_path=pdf_path,
            policy_version="v1"
        )
        print("Ingestion Result Stats:")
        print(ingest_result)
        
        # 3. Retrieve Summary
        summary = ingestion.get_policy_summary(policy_id)
        print("Summary retrieved successfully:", summary is not None)
        
        # Fix mock draft citation IDs to match actual ingested chunk IDs
        # The actual chunk ID will be like policy_id-md-1, and summary_id like policy_id-summary-1
        actual_chunk_id = f"{policy_id}-md-1"
        dummy_draft.supporting_citations[0].chunk_id = actual_chunk_id
        dummy_draft.supporting_citations[0].document_id = f"policy_{policy_id}"
        
        # 4. Coverage Evaluation
        question = CoverageQuestion(
            user_id=uuid4(),
            policy_id=policy_id,
            question_text="Will physical therapy be covered after surgery?",
            scenario_context={
                "procedure": "knee surgery",
                "provider_network_status": "in_network"
            },
            requested_decision_type=DecisionType.COVERAGE
        )
        
        print(f"Evaluating coverage for question: '{question.question_text}'...")
        eval_result = evaluation.evaluate_coverage(question)
        print("Evaluation Status:", eval_result.processing_status)
        print("Answer Decision:", eval_result.answer.decision)
        print("Short Answer:", eval_result.answer.short_answer)
        print("Confidence Level:", eval_result.confidence.level)
        print("Citations Count:", len(eval_result.citations))
        
        # 5. Retrieve Trace
        trace = evaluation.get_trace(
            retrieval_trace_id=eval_result.audit.retrieval_trace_id,
            llm_trace_id=eval_result.audit.llm_trace_id
        )
        print("Trace retrieved successfully! Keys:", list(trace.keys()))
        
        return True
    except Exception as e:
        print("An error occurred during service pipeline execution:")
        import traceback
        traceback.print_exc()
        return False

def test_api():
    print("\n--- Testing API Router via TestClient ---")
    try:
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # 1. Health check
        res = client.get("/health")
        print("GET /health:", res.status_code, res.json())
        assert res.status_code == 200
        
        # 2. Get non-existent summary
        res = client.get(f"/v1/policies/{uuid4()}/summary")
        print("GET /v1/policies/.../summary (non-existent):", res.status_code, res.json())
        assert res.status_code == 404
        
        print("API routes validation passed!")
        return True
    except ImportError:
        print("fastapi.testclient or httpx not installed. Skipping TestClient tests.")
        # Check routes list directly on the app object
        routes = [r.path for r in app.routes]
        print("Registered routes on app:", routes)
        assert "/health" in routes
        return True
    except Exception as e:
        print("API routes validation failed:")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success_api = test_api()
    success_services = await test_services()
    if success_api and success_services:
        print("\n=== ALL TESTS PASSED SUCCESSFULLY ===")
        sys.exit(0)
    else:
        print("\n=== SOME TESTS FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
