"""
Revio Pulse AI - Urgency Scoring & Churn Risk Forecasting
Identifies flight risks, high-stakes complaints, and routes escalation SLAs.
"""

import re
from typing import Dict, Any


HIGH_RISK_SIGNALS = {
    "legal_action": ["legal", "lawyer", "attorney", "court", "fraudulent", "chargeback", "police", "sue"],
    "direct_churn_threat": ["cancel", "cancelling", "moving to", "switching to", "switch to", "competitor", "leaving", "boycott", "avoid this"],
    "financial_impact": ["lost", "loss", "dollars", "transactions", "overcharge", "stole", "hidden fee", "refund"],
    "outage_critical": ["crash", "crashed", "outage", "locked out", "peak hours", "unusable", "broken"],
    "health_safety_living": ["leakage", "water", "mold", "hazard", "unacceptable living", "emergency"]
}


class UrgencyChurnPredictor:
    """Computes Churn Probability (0-100) and operational urgency SLAs."""

    def __init__(self):
        self.risk_patterns = HIGH_RISK_SIGNALS

    def predict(self, text: str, rating: float, verified: bool = True) -> Dict[str, Any]:
        text_lower = text.lower()
        score = 0
        detected_signals = []
        escalation_department = "Customer Success"

        # Base score from rating
        if rating == 1:
            score += 45
        elif rating == 2:
            score += 28
        elif rating == 3:
            score += 10
        else:
            score += 2

        # Check for specific high risk signals
        for category, keywords in self.risk_patterns.items():
            hits = [kw for kw in keywords if kw in text_lower]
            if hits:
                detected_signals.extend(hits)
                if category == "legal_action":
                    score += 35
                    escalation_department = "Legal & Risk Compliance"
                elif category == "direct_churn_threat":
                    score += 25
                    escalation_department = "Executive Escalations / Retention"
                elif category == "financial_impact":
                    score += 20
                    if escalation_department == "Customer Success":
                        escalation_department = "Finance & Billing Operations"
                elif category == "outage_critical":
                    score += 22
                    if escalation_department == "Customer Success":
                        escalation_department = "DevOps & Engineering Reliability"
                elif category == "health_safety_living":
                    score += 25
                    escalation_department = "Property Management & Emergency Ops"

        # Verified buyer multiplier
        if verified and score > 20:
            score = int(score * 1.1)

        # Cap between 0 and 100
        churn_risk_score = min(max(score, 0), 100)

        # Determine Urgency Level & SLA
        if churn_risk_score >= 75:
            urgency_level = "CRITICAL"
            sla_target = "< 1 hour"
            requires_human_escalation = True
        elif churn_risk_score >= 50:
            urgency_level = "HIGH"
            sla_target = "< 4 hours"
            requires_human_escalation = True
        elif churn_risk_score >= 25:
            urgency_level = "MEDIUM"
            sla_target = "< 24 hours"
            requires_human_escalation = False
        else:
            urgency_level = "LOW"
            sla_target = "< 48 hours"
            requires_human_escalation = False

        return {
            "churn_risk_score": churn_risk_score,
            "urgency_level": urgency_level,
            "sla_target": sla_target,
            "requires_human_escalation": requires_human_escalation,
            "escalation_department": escalation_department,
            "detected_risk_signals": list(set(detected_signals))
        }
