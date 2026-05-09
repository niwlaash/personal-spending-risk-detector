"""
FastAPI backend for Personal Spending Risk & Burnout Detector.
Provides REST API endpoints for file upload and analysis.
"""

import os
import shutil
import uuid

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.models import RiskReport, Transaction, get_db, init_db
from app.pipeline import Pipeline

# Initialize database
init_db()

app = FastAPI(
    title="Personal Spending Risk & Burnout Detector",
    description="Malaysia-focused financial health analysis API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = Pipeline()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Spending Risk & Burnout Detector API"}


@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a bank statement file (CSV or PDF) and get full analysis.

    Returns risk scores, insights, and transaction breakdown.
    """
    # Validate file type
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ("csv", "pdf"):
        raise HTTPException(400, "Only CSV and PDF files are supported.")

    # Save uploaded file
    file_id = str(uuid.uuid4())[:8]
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}_{filename}")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Run pipeline
    try:
        result = pipeline.run(save_path, file_type=ext)
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")
    finally:
        # Clean up uploaded file
        if os.path.exists(save_path):
            os.remove(save_path)

    # Save risk report to DB
    try:
        report = RiskReport(
            financial_risk_score=result["risk_scores"]["financial_risk_score"],
            burnout_risk_score=result["risk_scores"]["burnout_risk_score"],
            financial_risk_level=result["risk_scores"]["financial_risk_level"],
            burnout_risk_level=result["risk_scores"]["burnout_risk_level"],
            insights="\n".join(result["insights"]),
        )
        db.add(report)
        db.commit()
    except Exception:
        pass  # Non-critical: don't fail if DB save fails

    return result


@app.get("/api/reports")
def get_reports(db: Session = Depends(get_db)):
    """Get all past risk reports."""
    reports = (
        db.query(RiskReport).order_by(RiskReport.created_at.desc()).limit(20).all()
    )
    return [
        {
            "id": r.id,
            "financial_risk_score": r.financial_risk_score,
            "burnout_risk_score": r.burnout_risk_score,
            "financial_risk_level": r.financial_risk_level,
            "burnout_risk_level": r.burnout_risk_level,
            "created_at": str(r.created_at),
        }
        for r in reports
    ]
