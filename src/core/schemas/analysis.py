"""
Analysis schemas for API validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.core.schemas.enums import AnalysisStatus, AnalysisType


class AnalysisBase(BaseModel):
    """Base analysis schema"""
    analysis_type: AnalysisType
    extra: dict = Field(default_factory=dict) # metadata


class AnalysisCreate(AnalysisBase):
    """Schema for creating an analysis"""
    project_id: int


class AnalysisUpdate(BaseModel):
    """Schema for updating an analysis"""
    status: Optional[AnalysisStatus] = None
    result_summary: Optional[str] = None
    error_message: Optional[str] = None
    extra: Optional[dict] = None # metadata


class AnalysisInDB(AnalysisBase):
    """Schema for analysis in database"""
    id: int
    project_id: int
    status: AnalysisStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result_summary: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnalysisResponse(AnalysisInDB):
    """Schema for analysis API response"""
    duration_seconds: Optional[float] = None

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class AnalysisList(BaseModel):
    """Schema for analysis list response"""
    items: list[AnalysisResponse]
    total: int
    page: int = 1
    per_page: int = 20