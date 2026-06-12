from pydantic import BaseModel, Field
from typing import List


class PlanOverview(BaseModel):
    insurer_name: str
    plan_name: str
    mikes_eli5_summary: str = Field(description="A 3-sentence 'Explain Like I'm 5' summary. Break down how this plan functions, who it is best for, and the biggest financial risk.")
    network_rules: str = Field(description="Explanation of network rules. E.g., 'This is an HMO. You must stay in-network.'")
    specialist_referral_required: bool = Field(description="True if the user MUST get a PCP referral to see a specialist.")
    referral_details: str = Field(description="Specific rules about getting referrals, or 'No referral needed' if false.")


class FinancialDetail(BaseModel):
    amount: str
    nuance: str = Field(description="Crucial context (e.g., 'Applies per family', 'Does not apply to prescription drugs').")

class Financials(BaseModel):
    in_network_deductible: FinancialDetail
    out_of_network_deductible: FinancialDetail
    out_of_pocket_max: FinancialDetail


class CareCost(BaseModel):
    cost: str
    conditions: str = Field(description="e.g., 'Only applies AFTER deductible is met', or 'Waived for first 3 visits'.")

class RoutineCare(BaseModel):
    preventive_care: CareCost
    primary_care: CareCost
    specialist: CareCost

class EmergencyScenarios(BaseModel):
    emergency_room: CareCost
    ambulance: CareCost
    urgent_care: CareCost


class DrugTier(BaseModel):
    tier_name: str = Field(description="e.g., 'Tier 1 Generic', 'Preferred Brand', 'Specialty'")
    cost: str = Field(description="Copay or coinsurance")
    notes: str = Field(description="Specific rules (e.g., 'Requires step therapy', 'Limited to 30-day supply')")


class PriorAuthorizationItem(BaseModel):
    service: str = Field(description="e.g., MRI, CT Scan, Physical Therapy, Bariatric Surgery")
    details: str = Field(description="What are the specific requirements to get this approved?")
    citation: str = Field(description="Exact markdown heading or section title where this information appears.If unavailable, return 'Citation unavailable in source text")


class CoverageExclusion(BaseModel):
    exclusion: str = Field(description="e.g., Cosmetic surgery, Adult dental, Experimental treatments")
    explanation: str = Field(description="Why is it excluded or are there any rare exceptions?")
    citation: str = Field(description="Exact markdown heading or section title where this information appears.If unavailable, return 'Citation unavailable in source text")


class ScenarioExample(BaseModel):
    scenario: str
    estimated_user_cost: str
    assumptions: List[str]
    explanation: str

class DenialRisk(BaseModel):
    risk: str = Field(description="e.g., 'Missing a Filing Deadline', 'Using an Out-of-Network Anesthesiologist'")
    explanation: str = Field(description="How this trap typically happens based on the policy text.")
    prevention_tip: str = Field(description="Actionable advice for the user to prevent this denial.")
    citation: str = Field(
    description="""
    Exact markdown heading or section title where this information appears.
    If unavailable, return 'Citation unavailable in source text
    """
    )


class PolicySummary(BaseModel):
    overview: PlanOverview
    financials: Financials
    routine_care: RoutineCare
    emergency_care: EmergencyScenarios
    drug_tiers: List[DrugTier] = Field(description="Extract all prescription drug tiers mentioned.")
    prior_authorization_requirements: List[PriorAuthorizationItem] = Field(description="Extract every explicit prior authorization requirement found.")
    excluded_services: List[CoverageExclusion] = Field(description="Extract every explicit exclusion found.")
    example_scenarios: List[ScenarioExample] = Field(description="Create 3 relatable medical scenarios (e.g., broken bone, hospital stay, chronic illness) and estimate the cost.")
    denial_risks: List[DenialRisk] = Field(description="Identify 3 to 5 strict rules that will result in an automatic claim denial if not followed.")