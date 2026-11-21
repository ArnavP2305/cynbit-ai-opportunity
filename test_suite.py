"""
Revio Pulse AI - Automated Unit Test Suite
Verifies ABSA accuracy, churn prediction, escalation rules, and response generation.
"""

import unittest
from engine.sentiment_absa import ABSAEngine
from engine.urgency_churn import UrgencyChurnPredictor
from engine.response_generator import ResponseGenerator
from engine.trend_detector import TrendDetector
from engine.jira_dispatch import TicketDispatcher


class TestRevioPulseAI(unittest.TestCase):

    def setUp(self):
        self.absa = ABSAEngine()
        self.churn = UrgencyChurnPredictor()
        self.resp_gen = ResponseGenerator()
        self.trend = TrendDetector()

    def test_absa_aspect_detection(self):
        text = "The pricing is way too high and hidden fees were added. UI is pretty though."
        res = self.absa.analyze(text=text, rating=2.0)
        self.assertIn("Billing & Pricing", res["detected_aspects"])
        self.assertIn("UI/UX & Product Usability", res["detected_aspects"])
        self.assertLess(res["aspect_breakdown"]["Billing & Pricing"]["score"], 0)

    def test_churn_prediction_critical(self):
        text = "System crashed during peak hours. We lost thousands of dollars. We are switching to BirdEye."
        res = self.churn.predict(text=text, rating=1.0, verified=True)
        self.assertEqual(res["urgency_level"], "CRITICAL")
        self.assertTrue(res["requires_human_escalation"])
        self.assertGreaterEqual(res["churn_risk_score"], 75)

    def test_churn_prediction_low(self):
        text = "Amazing experience! Love the clean UI and quick customer service."
        res = self.churn.predict(text=text, rating=5.0, verified=True)
        self.assertEqual(res["urgency_level"], "LOW")
        self.assertFalse(res["requires_human_escalation"])
        self.assertLess(res["churn_risk_score"], 25)

    def test_response_generator_guardrails(self):
        text = "Terrible crash on iOS."
        absa_res = self.absa.analyze(text, rating=1.0)
        urg_res = self.churn.predict(text, rating=1.0)
        res = self.resp_gen.generate(
            reviewer_name="Alex Turner",
            platform="App Store",
            rating=1.0,
            review_text=text,
            absa_result=absa_res,
            urgency_result=urg_res
        )
        self.assertTrue(res["guardrails_verified"])
        self.assertIn("Alex", res["draft_response"])
        self.assertTrue(any(w in res["draft_response"].lower() for w in ["regret", "apologize"]))

    def test_ticket_dispatcher(self):
        text = "Charged twice on card. Calling lawyer."
        absa_res = self.absa.analyze(text, rating=1.0)
        urg_res = self.churn.predict(text, rating=1.0)
        ticket = TicketDispatcher.create_ticket_payload(
            review_id="REV-TEST",
            reviewer_name="Legal Client",
            platform="Google Maps",
            review_text=text,
            absa_result=absa_res,
            urgency_result=urg_res
        )
        self.assertIn("jira_payload", ticket)
        self.assertIn("slack_payload", ticket)
        self.assertEqual(ticket["jira_payload"]["priority"], "P0 - Blocker")


if __name__ == "__main__":
    unittest.main()
