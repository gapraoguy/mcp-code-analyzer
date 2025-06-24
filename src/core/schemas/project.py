"""
Project schemas for API validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.core.schemas.enums import ProjectStatus


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., min_length=1)
    description: Optional[str] = None
    language: str = Field(default="python", pattern="^(python|javascript|typescript|go)$")


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    language: Optional[str] = Field(None, pattern="^(python|javascript|typescript|go)$")


class ProjectInDB(ProjectBase):
    """Schema for project in database"""
    id: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    total_files: int
    total_lines: int
    last_analyzed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectResponse(ProjectInDB):
    """Schema for project API response"""
    analysis_count: int = 0
    suggestion_count: int = 0
    pending_suggestion_count: int = 0


class ProjectList(BaseModel):
    """Schema for project list response"""
    items: list[ProjectResponse]
    total: int
    page: int = 1
    per_page: int = 20