"""
Pydantic schemas for API validation
"""
from src.core.schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectList,
)
from src.core.schemas.analysis import (
    AnalysisBase,
    AnalysisCreate,
    AnalysisUpdate,
    AnalysisResponse,
    AnalysisList,
)
from src.core.schemas.file_analysis import (
    FileAnalysisBase,
    FileAnalysisCreate,
    FileAnalysisResponse,
    FileAnalysisList,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    ComplexityMetrics,
)
from src.core.schemas.suggestion import (
    SuggestionBase,
    SuggestionCreate,
    SuggestionUpdate,
    SuggestionApply,
    SuggestionResponse,
    SuggestionList,
    ErrorFixRequest,
    FeatureRequest,
)
from src.core.schemas.enums import (
    ProjectStatus,
    AnalysisStatus,
    AnalysisType,
    SuggestionType,
    SuggestionStatus,
)

__all__ = [
    # Project
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectList",
    # Analysis
    "AnalysisBase",
    "AnalysisCreate",
    "AnalysisUpdate",
    "AnalysisResponse",
    "AnalysisList",
    # FileAnalysis
    "FileAnalysisBase",
    "FileAnalysisCreate",
    "FileAnalysisResponse",
    "FileAnalysisList",
    "FunctionInfo",
    "ClassInfo",
    "ImportInfo",
    "ComplexityMetrics",
    # Suggestion
    "SuggestionBase",
    "SuggestionCreate",
    "SuggestionUpdate",
    "SuggestionApply",
    "SuggestionResponse",
    "SuggestionList",
    "ErrorFixRequest",
    "FeatureRequest",
    # Enums
    "ProjectStatus",
    "AnalysisStatus",
    "AnalysisType",
    "SuggestionType",
    "SuggestionStatus",
]