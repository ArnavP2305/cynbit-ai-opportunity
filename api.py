"""
Revio Pulse AI - RESTful Microservice API
Production-grade FastAPI implementation with automatic OpenAPI/Swagger documentation.
"""

import os
import sys
from typing import List, Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from engine.sentiment_absa import ABSAEngine
from engine.urgency_churn import UrgencyChurnPredictor
from engine.response_generator import ResponseGenerator
from engine.trend_detector import TrendDetector
from engine.jira_dispatch import TicketDispatcher

# Initialize Core Services
absa_engine = ABSAEngine()
churn_predictor = UrgencyChurnPredictor()
response_gen = ResponseGenerator()
trend_detector = TrendDetector()

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Revio Pulse AI - Reputation & CX Intelligence API",
        description="Autonomous Aspect-Based Sentiment, Churn Prediction & Response Generation API for Cynbit Technologies.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    class SingleReviewRequest(BaseModel):
        review_id: Optional[str] = Field(default="REV-001", description="Unique review identifier")
        reviewer_name: str = Field(default="John Doe", description="Customer full or display name")
        platform: str = Field(default="Google Maps", description="Origin platform (Google Maps, Trustpilot, G2, App Store)")
        rating: float = Field(default=1.0, ge=1.0, le=5.0, description="Customer star rating (1 to 5)")
        review_text: str = Field(..., description="Unstructured customer review text")
        verified_purchase: Optional[bool] = Field(default=True, description="Whether customer is verified")
        brand_tone: Optional[str] = Field(default="Empathetic & Resolution-Oriented", description="Voice tone for response draft")

    class BatchReviewRequest(BaseModel):
        reviews: List[SingleReviewRequest]

    @app.get("/")
    def root():
        return {
            "service": "Revio Pulse AI",
            "version": "1.0.0",
            "company": "Cynbit Technologies",
            "status": "Healthy",
            "endpoints": ["/docs", "/api/v1/analyze", "/api/v1/batch-analyze", "/api/v1/trends"]
        }

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "revio-pulse-ai"}

    @app.post("/api/v1/analyze")
    def analyze_review(req: SingleReviewRequest):
        try:
            absa = absa_engine.analyze(req.review_text, req.rating)
            churn = churn_predictor.predict(req.review_text, req.rating, req.verified_purchase)
            resp = response_gen.generate(
                reviewer_name=req.reviewer_name,
                platform=req.platform,
                rating=req.rating,
                review_text=req.review_text,
                absa_result=absa,
                urgency_result=churn,
                tone=req.brand_tone
            )
            ticket = None
            if churn["requires_human_escalation"]:
                ticket = TicketDispatcher.create_ticket_payload(
                    review_id=req.review_id or "REV-UNKNOWN",
                    reviewer_name=req.reviewer_name,
                    platform=req.platform,
                    review_text=req.review_text,
                    absa_result=absa,
                    urgency_result=churn
                )

            return {
                "review_id": req.review_id,
                "absa_analysis": absa,
                "urgency_prediction": churn,
                "draft_response": resp["draft_response"],
                "tone_applied": resp["tone_applied"],
                "escalation_ticket": ticket
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/v1/batch-analyze")
    def batch_analyze(req: BatchReviewRequest):
        results = []
        for r in req.reviews:
            absa = absa_engine.analyze(r.review_text, r.rating)
            churn = churn_predictor.predict(r.review_text, r.rating, r.verified_purchase)
            results.append({
                "review_id": r.review_id,
                "rating": r.rating,
                "absa_result": absa,
                "urgency_result": churn
            })
        trends = trend_detector.analyze_batch(results)
        return {
            "processed_count": len(results),
            "trends": trends,
            "reviews": results
        }

else:
    # Lightweight Fallback HTTP Server using http.server if FastAPI not yet installed
    import json
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class FallbackHTTPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "service": "Revio Pulse AI (Fallback HTTP Engine)",
                "note": "Install fastapi and uvicorn for full OpenAPI docs: pip install fastapi uvicorn",
                "status": "ready"
            }).encode("utf-8"))

    def run_fallback(port=8000):
        server = HTTPServer(("0.0.0.0", port), FallbackHTTPHandler)
        print(f"Fallback HTTP server running on port {port}...")
        server.serve_forever()

if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn
        uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("[!] FastAPI / uvicorn not found in environment. Starting Fallback Server.")
        run_fallback(8000)
