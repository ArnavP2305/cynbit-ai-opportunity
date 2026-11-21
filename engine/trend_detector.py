"""
Revio Pulse AI - Trend & Topic Anomaly Detector
Aggregates customer sentiment across time, platforms, and detects systemic anomalies.
"""

from typing import List, Dict, Any
from collections import Counter


class TrendDetector:
    """Performs aggregate analytics, NPS estimation, and topic anomaly detection."""

    def analyze_batch(self, analyzed_reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_count = len(analyzed_reviews)
        if total_count == 0:
            return {"error": "Empty dataset"}

        # Rating & Sentiment breakdown
        ratings = [r.get("rating", 3.0) for r in analyzed_reviews]
        avg_rating = round(sum(ratings) / total_count, 2)

        # NPS Calculation (Promoters: 5, Passives: 4, Detractors: 1-3)
        promoters = sum(1 for r in ratings if r >= 5)
        passives = sum(1 for r in ratings if r == 4)
        detractors = sum(1 for r in ratings if r <= 3)
        nps_score = round(((promoters - detractors) / total_count) * 100, 1)

        # Aspect distribution and polarity
        aspect_counter = Counter()
        aspect_sentiments = {}
        urgency_counter = Counter()

        for r in analyzed_reviews:
            urgency = r.get("urgency_result", {}).get("urgency_level", "LOW")
            urgency_counter[urgency] += 1

            absa = r.get("absa_result", {})
            for aspect, details in absa.get("aspect_breakdown", {}).items():
                aspect_counter[aspect] += 1
                if aspect not in aspect_sentiments:
                    aspect_sentiments[aspect] = []
                aspect_sentiments[aspect].append(details.get("score", 0.0))

        # Average score per aspect
        aspect_averages = {
            aspect: round(sum(scores) / len(scores), 2)
            for aspect, scores in aspect_sentiments.items()
        }

        # Anomaly Detection: High volume of negative sentiment in specific aspects
        anomalies = []
        if aspect_averages.get("Platform Reliability & Uptime", 0) < -0.3:
            anomalies.append({
                "severity": "CRITICAL",
                "area": "Platform Reliability & Uptime",
                "issue": "High negative cluster detected around crashes, downtime, or billing lockout."
            })
        if aspect_averages.get("Billing & Pricing", 0) < -0.3:
            anomalies.append({
                "severity": "HIGH",
                "area": "Billing & Pricing",
                "issue": "Disproportionate volume of complaints regarding hidden fees or chargeback risks."
            })

        return {
            "total_reviews_analyzed": total_count,
            "average_rating": avg_rating,
            "estimated_nps": nps_score,
            "nps_distribution": {
                "promoters_pct": round((promoters / total_count) * 100, 1),
                "passives_pct": round((passives / total_count) * 100, 1),
                "detractors_pct": round((detractors / total_count) * 100, 1)
            },
            "urgency_distribution": dict(urgency_counter),
            "aspect_mention_frequency": dict(aspect_counter),
            "aspect_sentiment_benchmarks": aspect_averages,
            "detected_anomalies": anomalies
        }
