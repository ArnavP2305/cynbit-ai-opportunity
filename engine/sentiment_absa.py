"""
Revio Pulse AI - Aspect-Based Sentiment Analysis (ABSA) Engine
Extracts multi-faceted sentiment dimensions from unstructured customer feedback.
"""

import re
from typing import Dict, List, Any


ASPECT_TAXONOMY = {
    "Billing & Pricing": {
        "keywords": ["billing", "price", "pricing", "charged", "fee", "cost", "subscription", 
                     "hidden fee", "refund", "invoice", "double-billed", "chargeback", "expensive", "money"],
        "weight": 1.2
    },
    "Platform Reliability & Uptime": {
        "keywords": ["crash", "crashed", "downtime", "down", "bug", "error", "locked out", 
                     "latency", "slow", "broken", "freeze", "failure", "glitch", "uptime", "unresponsive"],
        "weight": 1.3
    },
    "Customer Support & Responsiveness": {
        "keywords": ["support", "service", "helpdesk", "ticket", "response", "unresponsive", 
                     "representative", "call", "agent", "zoom", "queue", "resolution", "assistance"],
        "weight": 1.1
    },
    "UI/UX & Product Usability": {
        "keywords": ["ui", "ux", "interface", "design", "look", "navigation", "dashboard", 
                     "sleek", "intuitive", "clunky", "confusing", "export", "clean", "minimalist"],
        "weight": 1.0
    },
    "Features & Integrations": {
        "keywords": ["feature", "integration", "webhook", "api", "slack", "csv", "sync", 
                     "synchronization", "functionality", "hubspot", "reports", "connector"],
        "weight": 1.0
    },
    "Property & Maintenance Operations": {
        "keywords": ["maintenance", "leakage", "water", "unit", "tenant", "repair", 
                     "portal", "property", "manager", "living conditions", "rent"],
        "weight": 1.1
    }
}

POSITIVE_LEXICON = {
    "amazing", "great", "excellent", "outstanding", "accurate", "shockingly", "saves", 
    "clean", "minimalist", "sleek", "recommend", "love", "solid", "faster", "easy", 
    "helpful", "polite", "wonderful", "best", "flawless", "prompt", "top-tier"
}

NEGATIVE_LEXICON = {
    "horrible", "crashed", "crash", "locked out", "unresponsive", "lost", "avoid", 
    "deceptive", "hidden", "non-refundable", "broke", "broken", "fraudulent", 
    "chargeback", "never", "unacceptable", "dismissive", "misinterprets", "slow", 
    "fail", "worst", "terrible", "waste", "disappointed", "annoying", "poor"
}

INTENSIFIERS = {"very", "completely", "totally", "shockingly", "extremely", "absolutely", "severely"}
NEGATIONS = {"not", "never", "no", "without", "zero", "hardly", "barely"}


class ABSAEngine:
    """Extracts fine-grained sentiment scores for predefined business aspects."""

    def __init__(self):
        self.taxonomy = ASPECT_TAXONOMY

    def analyze(self, text: str, rating: float = 3.0) -> Dict[str, Any]:
        text_lower = text.lower()
        words = re.findall(r"\b[\w'-]+\b", text_lower)
        sentences = re.split(r"[.!?]+", text_lower)

        aspect_results = {}
        detected_aspects = []

        for aspect_name, aspect_info in self.taxonomy.items():
            matched_keywords = [kw for kw in aspect_info["keywords"] if kw in text_lower]
            if not matched_keywords:
                continue

            # Calculate sentiment specific to sentences containing this aspect
            aspect_sentences = [
                s for s in sentences if any(kw in s for kw in matched_keywords)
            ]
            
            aspect_score = 0.0
            word_count = 0

            for sent in aspect_sentences:
                sent_words = re.findall(r"\b[\w'-]+\b", sent)
                for i, w in enumerate(sent_words):
                    prev_w = sent_words[i-1] if i > 0 else ""
                    is_negated = prev_w in NEGATIONS
                    multiplier = -1.0 if is_negated else 1.0

                    if prev_w in INTENSIFIERS:
                        multiplier *= 1.5

                    if w in POSITIVE_LEXICON:
                        aspect_score += 1.0 * multiplier
                        word_count += 1
                    elif w in NEGATIVE_LEXICON:
                        aspect_score -= 1.0 * multiplier
                        word_count += 1

            # Fallback/Normalize to [-1.0, 1.0]
            if word_count > 0:
                normalized_score = max(min(aspect_score / word_count, 1.0), -1.0)
            else:
                # If neutral or inferred from rating
                normalized_score = (rating - 3.0) / 2.0

            polarity = "Neutral"
            if normalized_score >= 0.2:
                polarity = "Positive"
            elif normalized_score <= -0.2:
                polarity = "Negative"

            aspect_results[aspect_name] = {
                "score": round(float(normalized_score), 2),
                "polarity": polarity,
                "matched_terms": matched_keywords
            }
            detected_aspects.append(aspect_name)

        # Overall sentiment calculation
        pos_hits = sum(1 for w in words if w in POSITIVE_LEXICON)
        neg_hits = sum(1 for w in words if w in NEGATIVE_LEXICON)

        if rating >= 4:
            overall_polarity = "Positive"
            overall_score = round(0.5 + (rating - 4) * 0.5, 2)
        elif rating <= 2:
            overall_polarity = "Negative"
            overall_score = round(-0.5 - (2 - rating) * 0.5, 2)
        else:
            if pos_hits > neg_hits:
                overall_polarity = "Positive"
                overall_score = 0.35
            elif neg_hits > pos_hits:
                overall_polarity = "Negative"
                overall_score = -0.35
            else:
                overall_polarity = "Neutral"
                overall_score = 0.0

        if pos_hits > 0 and neg_hits > 0 and abs(pos_hits - neg_hits) <= 2:
            overall_polarity = "Mixed"

        return {
            "overall_score": overall_score,
            "overall_polarity": overall_polarity,
            "detected_aspects": detected_aspects,
            "aspect_breakdown": aspect_results
        }
