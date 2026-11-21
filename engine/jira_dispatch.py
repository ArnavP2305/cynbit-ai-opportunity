"""
Revio Pulse AI - Automated Ticket Dispatcher (Jira / Linear / Slack Webhook)
Converts high-risk reviews into actionable engineering or customer success tickets.
"""

from typing import Dict, Any


class TicketDispatcher:
    """Creates structured operational payload for internal ticketing systems."""

    @staticmethod
    def create_ticket_payload(
        review_id: str,
        reviewer_name: str,
        platform: str,
        review_text: str,
        absa_result: Dict[str, Any],
        urgency_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        urgency = urgency_result.get("urgency_level", "MEDIUM")
        dept = urgency_result.get("escalation_department", "Customer Success")
        risk_score = urgency_result.get("churn_risk_score", 50)
        aspects = absa_result.get("detected_aspects", [])

        priority_mapping = {
            "CRITICAL": "P0 - Blocker",
            "HIGH": "P1 - Critical",
            "MEDIUM": "P2 - Major",
            "LOW": "P3 - Minor"
        }

        jira_issue = {
            "project_key": "REV",
            "issue_type": "Incident",
            "priority": priority_mapping.get(urgency, "P2 - Major"),
            "summary": f"[{urgency}] Customer Churn Risk ({risk_score}%): {reviewer_name} on {platform}",
            "assignee_group": dept,
            "labels": ["revio-ai", "cx-escalation", platform.lower().replace(" ", "-")] + [a.lower().replace(" ", "-") for a in aspects],
            "description": (
                f"*Review ID:* {review_id}\n"
                f"*Reviewer:* {reviewer_name}\n"
                f"*Platform:* {platform}\n"
                f"*Urgency SLA:* {urgency_result.get('sla_target')}\n"
                f"*Detected Risk Signals:* {', '.join(urgency_result.get('detected_risk_signals', []))}\n"
                f"*Primary Concerns:* {', '.join(aspects)}\n\n"
                f"*Customer Feedback Content:*\n\"{review_text}\""
            ),
            "webhook_ready": True
        }

        slack_block = {
            "channel": "#alerts-customer-escalations",
            "text": f":warning: *{urgency} Escalation Alert* from {reviewer_name} on {platform}",
            "attachments": [
                {
                    "color": "#D32F2F" if urgency in ["CRITICAL", "HIGH"] else "#FBC02D",
                    "fields": [
                        {"title": "Churn Probability", "value": f"{risk_score}%", "short": True},
                        {"title": "Target SLA", "value": urgency_result.get("sla_target"), "short": True},
                        {"title": "Assigned Department", "value": dept, "short": True},
                        {"title": "Aspects", "value": ", ".join(aspects), "short": True},
                        {"title": "Review Excerpt", "value": f"\"{review_text[:140]}...\"", "short": False}
                    ]
                }
            ]
        }

        return {
            "jira_payload": jira_issue,
            "slack_payload": slack_block
        }
