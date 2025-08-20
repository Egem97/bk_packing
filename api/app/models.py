"""
SQLAlchemy models for the database
"""

from sqlalchemy import Column, String, DateTime, JSON, Date, Text
from sqlalchemy.sql import func
from .database import Base

class PipelineData(Base):
    """Model for pipeline data"""
    __tablename__ = "pipeline_data"
    __table_args__ = {"schema": "pipeline"}
    
    id = Column(String(255), primary_key=True, index=True)
    source_file = Column(String(255), nullable=False, index=True)
    data_type = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)
    raw_data = Column(JSON)
    processed_data = Column(JSON)
    partition_date = Column(Date, server_default=func.current_date(), index=True)

class AuditLog(Base):
    """Model for audit logging"""
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "pipeline"}
    
    id = Column(String(255), primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    operation = Column(String(20), nullable=False, index=True)
    record_id = Column(String(255), index=True)
    old_data = Column(JSON)
    new_data = Column(JSON)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    changed_by = Column(String(100), server_default='system')

class DataStatistics(Base):
    """Model for data statistics"""
    __tablename__ = "data_statistics"
    __table_args__ = {"schema": "pipeline"}
    
    id = Column(String(255), primary_key=True, index=True)
    data_type = Column(String(100), nullable=False, index=True)
    record_count = Column(String(255), default=0)
    file_count = Column(String(255), default=0)
    earliest_record = Column(DateTime(timezone=True))
    latest_record = Column(DateTime(timezone=True))
    quality_score = Column(String(255))
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
