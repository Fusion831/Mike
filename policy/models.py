from pydantic import BaseModel, Field
from typing import List

class PlanOverview(BaseModel):
    insurer_name: str = Field(description="Name of the insurance company")
    plan_name: str = Field(description="Name or type of the plan (e.g., Bronze, Silver, HMO, PPO)")
    mikes_eli5_summary: str = Field(description="A detailed, 3-to-4 sentence 'Explain Like I'm 5' summary. Break down how this specific plan functions, who it is best for, and the biggest financial risk the user carries.")
    network_rules: str = Field(description="Detailed explanation of the network rules. E.g., 'This is an HMO. You must stay in-network. Out-of-network care is 100% your financial responsibility unless it is a life-threatening emergency.'")

class FinancialDetail(BaseModel):
    amount: str = Field(description="The exact monetary amount (e.g., $2,500)")
    nuance: str = Field(description="Crucial context. Does this apply per person or per family? Are prescription drugs included in this amount, or do they have a separate deductible?")

class Financials(BaseModel):
    in_network_deductible: FinancialDetail
    out_of_pocket_max: FinancialDetail

class CareCost(BaseModel):
    cost: str = Field(description="The copay or coinsurance (e.g., '$50' or '20%')")
    conditions: str = Field(description="Conditions attached to this cost. E.g., 'Only applies AFTER deductible is met', 'Waived for the first 3 visits', or 'Requires Prior Authorization'.")

class RoutineCare(BaseModel):
    preventive_care: CareCost
    primary_care: CareCost
    specialist: CareCost
    prescription_drugs: CareCost = Field(description="Provide details on generic vs. brand name tiers if available.")

class EmergencyScenarios(BaseModel):
    emergency_room: CareCost
    ambulance: CareCost
    urgent_care: CareCost

class MikeAlert(BaseModel):
    alert_title: str = Field(description="A punchy title for the warning (e.g., 'Severe Ambulance Penalty', 'Strict Referral Rule')")
    description: str = Field(description="A detailed explanation of the trap, rule, or exclusion.")
    citation: str = Field(description="The exact section or page number where this rule is found so the user can verify it.")

class PolicySummary(BaseModel):
    overview: PlanOverview
    financials: Financials
    routine_care: RoutineCare
    emergency_scenarios: EmergencyScenarios
    mike_alerts: List[MikeAlert] = Field(description="Extract 3 to 5 of the most dangerous hidden traps, strict rules (like prior auth), or severe exclusions found in the document.")