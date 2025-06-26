"""
Enum definitions
"""
from enum import Enum


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ANALYZING = "analyzing"
    ERROR = "error"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    FILE = "file"
    DEPENDENCY = "dependency"
    SECURITY = "security"


class SuggestionType(str, Enum):
    ERROR_FIX = "error_fix"
    OPTIMIZATION = "optimization"
    REFACTOR = "refactor"
    SECURITY = "security"
    STYLE = "style"
    FEATURE = "feature"


class SuggestionStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPLIED = "applied"
    REJECTED = "rejected"
    IGNORED = "ignored"