"""
SQLAlchemy database models.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class URLCheck(Base):
    """Main table for URL check requests and results."""
    __tablename__ = "url_checks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submitted_url = Column(Text, nullable=False)
    normalized_url = Column(Text, nullable=False, index=True)
    submitter_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Result
    verdict = Column(String(20), nullable=False, index=True)  # benign, suspicious, malicious
    confidence = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)
    
    # Performance
    processing_time_ms = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrichments = relationship("Enrichment", back_populates="url_check", cascade="all, delete-orphan")


class Enrichment(Base):
    """Enrichment data from external sources."""
    __tablename__ = "enrichments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url_check_id = Column(String(36), ForeignKey("url_checks.id"), nullable=False, index=True)
    
    source = Column(String(50), nullable=False)  # whois, dns, gsb, virustotal, etc.
    raw_response = Column(JSON, nullable=True)
    parsed_fields = Column(JSON, nullable=True)
    
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    url_check = relationship("URLCheck", back_populates="enrichments")


class ThreatIntelCache(Base):
    """Cache for threat intelligence lookups."""
    __tablename__ = "threat_intel_cache"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lookup_key = Column(String(255), unique=True, nullable=False, index=True)  # domain or IP
    lookup_type = Column(String(20), nullable=False)  # domain, ip
    
    aggregated_verdicts = Column(JSON, nullable=True)
    
    last_checked_at = Column(DateTime, default=datetime.utcnow)
    ttl_seconds = Column(Integer, default=86400)  # 24 hours default
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit log for tracking actions."""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(100), nullable=False, index=True)
    user_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    request_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
