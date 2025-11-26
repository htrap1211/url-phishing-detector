"""
URL check API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import time
from urllib.parse import urlparse

from app.core.database import get_db
from app.schemas import (
    URLCheckRequest, URLCheckResponse, URLCheckResult,
    URLCheckDetail, SearchParams, SearchResult, StatsResponse
)
from app.models import URLCheck, Enrichment
from app.ml.model import get_detector
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/check", response_model=URLCheckResponse)
async def check_url(
    request: URLCheckRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Submit a URL for phishing detection.
    Returns immediately with check_id, processing happens synchronously for MVP.
    """
    try:
        start_time = time.time()
        
        # Normalize URL
        normalized_url = request.url.lower().strip()
        
        # Get ML detector
        detector = get_detector()
        
        # Predict (synchronous for MVP, will be async with Celery in Phase 5)
        prediction = detector.predict(normalized_url, enrichment_data=None)
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Save to database
        url_check = URLCheck(
            submitted_url=request.url,
            normalized_url=normalized_url,
            ip_address=http_request.client.host if http_request.client else None,
            verdict=prediction["verdict"],
            confidence=prediction["confidence"],
            model_version=prediction["model_version"],
            processing_time_ms=processing_time_ms
        )
        
        db.add(url_check)
        db.commit()
        db.refresh(url_check)
        
        logger.info(f"URL check complete: {url_check.id} - {prediction['verdict']} ({prediction['confidence']:.2f})")
        
        return URLCheckResponse(
            check_id=url_check.id,
            status="complete",
            estimated_time_seconds=0
        )
        
    except Exception as e:
        logger.error(f"URL check failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process URL: {str(e)}")


@router.get("/{check_id}", response_model=URLCheckResult)
async def get_check_result(
    check_id: str,
    db: Session = Depends(get_db)
):
    """Get result of a URL check by ID."""
    try:
        url_check = db.query(URLCheck).filter(URLCheck.id == check_id).first()
        
        if not url_check:
            raise HTTPException(status_code=404, detail="Check not found")
        
        # Get top features from model
        detector = get_detector()
        prediction = detector.predict(url_check.normalized_url, enrichment_data=None)
        
        return URLCheckResult(
            check_id=url_check.id,
            url=url_check.submitted_url,
            verdict=url_check.verdict,
            confidence=url_check.confidence,
            model_version=url_check.model_version,
            top_features=prediction["top_features"],
            enrichments=[],  # Empty for MVP, will add in Phase 5
            additional_info=prediction.get("additional_info"),
            processing_time_ms=url_check.processing_time_ms,
            timestamp=url_check.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get check result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{check_id}/detail", response_model=URLCheckDetail)
async def get_check_detail(
    check_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed result including all features and enrichments."""
    try:
        url_check = db.query(URLCheck).filter(URLCheck.id == check_id).first()
        
        if not url_check:
            raise HTTPException(status_code=404, detail="Check not found")
        
        # Get full prediction with all features
        detector = get_detector()
        prediction = detector.predict(url_check.normalized_url, enrichment_data=None)
        
        # Get enrichments
        enrichments = db.query(Enrichment).filter(
            Enrichment.url_check_id == check_id
        ).all()
        
        raw_enrichments = [
            {
                "source": e.source,
                "success": e.success,
                "data": e.parsed_fields
            }
            for e in enrichments
        ]
        
        return URLCheckDetail(
            check_id=url_check.id,
            url=url_check.submitted_url,
            verdict=url_check.verdict,
            confidence=url_check.confidence,
            model_version=url_check.model_version,
            top_features=prediction["top_features"],
            enrichments=[],
            additional_info=prediction.get("additional_info"),
            processing_time_ms=url_check.processing_time_ms,
            timestamp=url_check.created_at,
            raw_enrichments=raw_enrichments,
            all_features=prediction["all_features"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get check detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResult)
async def search_checks(
    params: SearchParams,
    db: Session = Depends(get_db)
):
    """Search and filter URL checks."""
    try:
        query = db.query(URLCheck)
        
        # Apply filters
        if params.domain:
            query = query.filter(URLCheck.normalized_url.contains(params.domain))
        
        if params.verdict:
            query = query.filter(URLCheck.verdict == params.verdict)
        
        if params.start_date:
            query = query.filter(URLCheck.created_at >= params.start_date)
        
        if params.end_date:
            query = query.filter(URLCheck.created_at <= params.end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        results = query.order_by(URLCheck.created_at.desc()) \
            .offset(params.offset) \
            .limit(params.limit) \
            .all()
        
        # Convert to response format
        url_results = []
        detector = get_detector()
        
        for url_check in results:
            prediction = detector.predict(url_check.normalized_url, enrichment_data=None)
            
            url_results.append(URLCheckResult(
                check_id=url_check.id,
                url=url_check.submitted_url,
                verdict=url_check.verdict,
                confidence=url_check.confidence,
                model_version=url_check.model_version,
                top_features=prediction["top_features"][:3],  # Top 3 for list view
                enrichments=[],
                processing_time_ms=url_check.processing_time_ms,
                timestamp=url_check.created_at
            ))
        
        return SearchResult(
            total=total,
            results=url_results
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get aggregate statistics."""
    try:
        # Total checks
        total_checks = db.query(URLCheck).count()
        
        # Verdict distribution
        verdicts = db.query(
            URLCheck.verdict,
            db.func.count(URLCheck.id)
        ).group_by(URLCheck.verdict).all()
        
        verdict_distribution = {verdict: count for verdict, count in verdicts}
        
        # Top domains
        top_domains_query = db.query(
            URLCheck.normalized_url,
            db.func.count(URLCheck.id).label('count')
        ).group_by(URLCheck.normalized_url) \
         .order_by(db.func.count(URLCheck.id).desc()) \
         .limit(10).all()
        
        top_domains = [
            {"domain": urlparse(url).netloc, "count": count}
            for url, count in top_domains_query
        ]
        
        # Average confidence
        avg_confidence = db.query(db.func.avg(URLCheck.confidence)).scalar() or 0.0
        
        # Date range
        first_check = db.query(db.func.min(URLCheck.created_at)).scalar()
        last_check = db.query(db.func.max(URLCheck.created_at)).scalar()
        
        return StatsResponse(
            total_checks=total_checks,
            verdict_distribution=verdict_distribution,
            top_domains=top_domains,
            avg_confidence=float(avg_confidence),
            date_range={
                "first": first_check or datetime.utcnow(),
                "last": last_check or datetime.utcnow()
            }
        )
        
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
