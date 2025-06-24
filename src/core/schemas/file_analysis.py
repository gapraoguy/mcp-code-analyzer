"""
File analysis schemas for API validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FunctionInfo(BaseModel):
    """Function information"""
    name: str
    line_start: int
    line_end: int
    parameters: list[str] = []
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    complexity: int = 0


class ClassInfo(BaseModel):
    """Class information"""
    name: str
    line_start: int
    line_end: int
    methods: list[str] = []
    attributes: list[str] = []
    base_classes: list[str] = []
    docstring: Optional[str] = None


class ImportInfo(BaseModel):
    """Import information"""
    module: str
    names: list[str] = []
    alias: Optional[str] = None
    line: int


class ComplexityMetrics(BaseModel):
    """Code complexity metrics"""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    maintainability_index: float = 0.0
    lines_of_code: int = 0
    comment_ratio: float = 0.0


class FileAnalysisBase(BaseModel):
    """Base file analysis schema"""
    file_path: str
    file_type: Optional[str] = None
    size_bytes: Optional[int] = None
    line_count: Optional[int] = None


class FileAnalysisCreate(FileAnalysisBase):
    """Schema for creating a file analysis"""
    analysis_id: int
    ast_data: Optional[dict] = None
    imports: list[ImportInfo] = []
    functions: list[FunctionInfo] = []
    classes: list[ClassInfo] = []
    dependencies: list[str] = []
    complexity_metrics: ComplexityMetrics = Field(default_factory=ComplexityMetrics)


class FileAnalysisInDB(FileAnalysisBase):
    """Schema for file analysis in database"""
    id: int
    analysis_id: int
    ast_data: Optional[dict]
    imports: list[dict]
    functions: list[dict]
    classes: list[dict]
    dependencies: list[str]
    complexity_metrics: dict
    created_at: datetime

    class Config:
        from_attributes = True


class FileAnalysisResponse(FileAnalysisInDB):
    """Schema for file analysis API response"""
    pass


class FileAnalysisList(BaseModel):
    """Schema for file analysis list response"""
    items: list[FileAnalysisResponse]
    total: int