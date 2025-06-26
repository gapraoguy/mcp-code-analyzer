"""
Suggestion schemas for API validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.core.schemas.enums import SuggestionType, SuggestionStatus


class SuggestionBase(BaseModel):
    """Base suggestion schema"""
    suggestion_type: SuggestionType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    line_start: Optional[int] = Field(None, ge=1)
    line_end: Optional[int] = Field(None, ge=1)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    impact_score: float = Field(default=0.0, ge=0.0, le=1.0)
    extra: dict = Field(default_factory=dict) #metadata


class SuggestionCreate(SuggestionBase):
    """Schema for creating a suggestion"""
    project_id: int
    file_analysis_id: Optional[int] = None


class SuggestionUpdate(BaseModel):
    """Schema for updating a suggestion"""
    status: Optional[SuggestionStatus] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    impact_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    extra: Optional[dict] = None #metadata


class SuggestionApply(BaseModel):
    """Schema for applying a suggestion"""
    apply: bool = True
    modified_code: Optional[str] = None


class SuggestionInDB(SuggestionBase):
    """Schema for suggestion in database"""
    id: int
    project_id: int
    file_analysis_id: Optional[int]
    status: SuggestionStatus
    created_at: datetime
    applied_at: Optional[datetime]

    class Config:
        from_attributes = True


class SuggestionResponse(SuggestionInDB):
    """Schema for suggestion API response"""
    file_path: Optional[str] = None  # From related FileAnalysis


class SuggestionList(BaseModel):
    """Schema for suggestion list response"""
    items: list[SuggestionResponse]
    total: int
    page: int = 1
    per_page: int = 20

    # Filters summary
    by_type: dict[str, int] = Field(default_factory=dict)
    by_status: dict[str, int] = Field(default_factory=dict)


class ErrorFixRequest(BaseModel):
    """Schema for error fix request"""
    project_id: int
    error_message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    context_lines: int = Field(default=10, ge=0, le=50)


class FeatureRequest(BaseModel):
    """Schema for feature implementation request"""
    project_id: int
    feature_description: str
    target_file: Optional[str] = None
    integration_points: list[str] = Field(default_factory=list)
    constraints: Optional[str] = None