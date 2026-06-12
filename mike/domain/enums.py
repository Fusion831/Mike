from enum import Enum


class DecisionType(str, Enum):
    COVERAGE = "coverage"
    REFERRAL_REQUIREMENT = "referral_requirement"
    NETWORK_IMPACT = "network_impact"
    PRIOR_AUTH = "prior_auth"
    COST_SHARING = "cost_sharing"
    EXCLUSIONS = "exclusions"


class SourceType(str, Enum):
    POLICY_CONTRACT = "policy_contract"
    RIDER = "rider"
    ENDORSEMENT = "endorsement"
    AMENDMENT = "amendment"
    SUMMARY_OF_BENEFITS = "summary_of_benefits"


class CitationRole(str, Enum):
    SUPPORTS_COVERAGE = "supports_coverage"
    SUPPORTS_EXCLUSION = "supports_exclusion"
    SUPPORTS_CONDITION = "supports_condition"
    SUPPORTS_RISK = "supports_risk"
    SUPPORTS_UNCERTAINTY = "supports_uncertainty"


class CoverageRiskCategory(str, Enum):
    DENIAL_RISK = "denial_risk"
    PRIOR_AUTH_RISK = "prior_auth_risk"
    REFERRAL_RISK = "referral_risk"
    OUT_OF_NETWORK_RISK = "out_of_network_risk"
    DOCUMENTATION_RISK = "documentation_risk"
    TIMING_RISK = "timing_risk"
    POLICY_AMBIGUITY_RISK = "policy_ambiguity_risk"


class RiskSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CoverageDecision(str, Enum):
    LIKELY_COVERED = "likely_covered"
    LIKELY_NOT_COVERED = "likely_not_covered"
    CONDITIONALLY_COVERED = "conditionally_covered"
    CANNOT_DETERMINE_FROM_POLICY = "cannot_determine_from_policy"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceEffect(str, Enum):
    RAISES = "raises"
    LOWERS = "lowers"
    NEUTRAL = "neutral"


class GroundingStatus(str, Enum):
    FULLY_GROUNDED = "fully_grounded"
    PARTIALLY_GROUNDED = "partially_grounded"
    WEAKLY_GROUNDED = "weakly_grounded"


class EvaluationStatus(str, Enum):
    COMPLETED = "completed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    FAILED_VALIDATION = "failed_validation"
