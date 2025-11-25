"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from uuid import UUID


# Request schemas
class URLCheckRequest(BaseModel):
    url: str = Field(..., description="URL to check for phishing")
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata")


# Response schemas
class URLCheckResponse(BaseModel):
    check_id: UUID
    status: str  # processing, complete, failed
    estimated_time_seconds: Optional[int] = None
    
    class Config:
        from_attributes = True


class FeatureContribution(BaseModel):
    name: str
    value: float
    contribution: float


class EnrichmentSummary(BaseModel):
    source: str
    success: bool
    key_fields: Optional[Dict] = None


class URLCheckResult(BaseModel):
    check_id: UUID
    url: str
    verdict: str  # benign, suspicious, malicious
    confidence: float
    model_version: str
    
    top_features: List[FeatureContribution]
    enrichments: Optional[List[EnrichmentSummary]] = None
    
    processing_time_ms: Optional[int] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class URLCheckDetail(URLCheckResult):
    """Extended result with full enrichment data."""
    raw_enrichments: Optional[List[Dict]] = None
    all_features: Optional[Dict[str, float]] = None


# Search schemas
class SearchParams(BaseModel):
    domain: Optional[str] = None
    verdict: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)


class SearchResult(BaseModel):
    total: int
    results: List[URLCheckResult]


# Stats schemas
class StatsResponse(BaseModel):
    total_checks: int
    verdict_distribution: Dict[str, int]
    top_domains: List[Dict[str, Any]]
    avg_confidence: float
    date_range: Dict[str, datetime]
