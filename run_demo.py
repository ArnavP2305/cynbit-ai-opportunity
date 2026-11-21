"""
Revio Pulse AI - Interactive CLI Demonstration & Verification Script
Executes the end-to-end AI/ML pipeline over sample real-world reviews.
"""

import os
import sys
import csv
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.sentiment_absa import ABSAEngine
from engine.urgency_churn import UrgencyChurnPredictor
from engine.response_generator import ResponseGenerator
from engine.trend_detector import TrendDetector
from engine.jira_dispatch import TicketDispatcher


def run_pipeline():
    print("=" * 80)
    print("   CYNBIT TECHNOLOGIES - REVIO PULSE AI PROOF-OF-CONCEPT ENGINE")
    print("   Autonomous Customer Experience & Reputation Intelligence Pipeline")
    print("=" * 80)

    absa_engine = ABSAEngine()
    churn_predictor = UrgencyChurnPredictor()
    response_gen = ResponseGenerator()
    trend_detector = TrendDetector()

    csv_path = os.path.join(os.path.dirname(__file__), "data", "sample_reviews.csv")
    reviews: List[Dict[str, Any]] = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reviews.append(row)

    print(f"\n[+] Loaded {len(reviews)} multi-platform customer reviews from {csv_path}\n")

    analyzed_batch = []

    for idx, item in enumerate(reviews[:4], 1):
        rev_id = item["review_id"]
        author = item["reviewer_name"]
        platform = item["platform"]
        rating = float(item["rating"])
        text = item["review_text"]
        verified = item.get("verified_purchase", "TRUE").upper() == "TRUE"

        # 1. Aspect-Based Sentiment Analysis
        absa_res = absa_engine.analyze(text=text, rating=rating)

        # 2. Urgency & Churn Risk Prediction
        urgency_res = churn_predictor.predict(text=text, rating=rating, verified=verified)

        # 3. Context-Aware Autonomous Response Synthesis
        response_res = response_gen.generate(
            reviewer_name=author,
            platform=platform,
            rating=rating,
            review_text=text,
            absa_result=absa_res,
            urgency_result=urgency_res,
            tone="Empathetic & Resolution-Oriented"
        )

        # 4. Jira Ticket generation if high risk
        ticket = None
        if urgency_res["requires_human_escalation"]:
            ticket = TicketDispatcher.create_ticket_payload(
                review_id=rev_id,
                reviewer_name=author,
                platform=platform,
                review_text=text,
                absa_result=absa_res,
                urgency_result=urgency_res
            )

        record = {
            "review_id": rev_id,
            "reviewer_name": author,
            "platform": platform,
            "rating": rating,
            "text": text,
            "absa_result": absa_res,
            "urgency_result": urgency_res,
            "generated_response": response_res["draft_response"],
            "ticket": ticket
        }
        analyzed_batch.append(record)

        print("-" * 80)
        print(f"CASE #{idx} | {rev_id} | {author} on [{platform}] | Rating: {int(rating)}/5 ★")
        print(f"Review: \"{text}\"")
        print(f"\n>> Overall Sentiment: {absa_res['overall_polarity']} (Score: {absa_res['overall_score']})")
        print(f">> Detected Aspects: {', '.join(absa_res['detected_aspects'])}")
        for asp, details in absa_res['aspect_breakdown'].items():
            print(f"   * {asp}: {details['polarity']} (score: {details['score']})")
        
        urg = urgency_res["urgency_level"]
        churn = urgency_res["churn_risk_score"]
        print(f"\n>> Churn Risk: {churn}% | Urgency Level: [{urg}] | SLA: {urgency_res['sla_target']}")
        print(f">> Escalation Route: {urgency_res['escalation_department']}")

        if ticket:
            print(f">> Auto-Dispatched Jira Issue: {ticket['jira_payload']['summary']}")
            print(f"   Priority: {ticket['jira_payload']['priority']} | Assigned: {ticket['jira_payload']['assignee_group']}")

        print("\n>> AI Synthesized Resolution Draft:")
        for line in response_res["draft_response"].split("\n"):
            print(f"   | {line}")
        print()

    # Run remaining batch for Trend Analytics
    for item in reviews[4:]:
        absa_res = absa_engine.analyze(item["review_text"], float(item["rating"]))
        urg_res = churn_predictor.predict(item["review_text"], float(item["rating"]))
        analyzed_batch.append({
            "rating": float(item["rating"]),
            "absa_result": absa_res,
            "urgency_result": urg_res
        })

    trends = trend_detector.analyze_batch(analyzed_batch)
    print("=" * 80)
    print("   AGGREGATE REPUTATION HEALTH & ANOMALY DETECTION REPORT")
    print("=" * 80)
    print(f"Total Reviews Analyzed: {trends['total_reviews_analyzed']}")
    print(f"Average Customer Rating: {trends['average_rating']}/5.0")
    print(f"Estimated Net Promoter Score (NPS): {trends['estimated_nps']}")
    print(f"NPS Breakdown: {trends['nps_distribution']['promoters_pct']}% Promoters | {trends['nps_distribution']['passives_pct']}% Passives | {trends['nps_distribution']['detractors_pct']}% Detractors")
    print(f"Urgency Breakdown: {trends['urgency_distribution']}")
    print("\nAspect Sentiment Scores (-1.0 to +1.0):")
    for asp, val in trends['aspect_sentiment_benchmarks'].items():
        print(f"  - {asp:35s}: {val:+.2f}")

    if trends['detected_anomalies']:
        print("\n[!] DETECTED ROOT-CAUSE ANOMALIES:")
        for anomaly in trends['detected_anomalies']:
            print(f"  [{anomaly['severity']}] {anomaly['area']}: {anomaly['issue']}")

    print("=" * 80)
    print("Demo completed successfully!")


if __name__ == "__main__":
    run_pipeline()
