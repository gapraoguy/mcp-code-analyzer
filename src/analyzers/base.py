"""
Base analyzer interface
"""
from abc import ABC, abstractmethod
import chardet
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Basic file information"""
    path: Path
    size_bytes: int
    line_count: int
    encoding: str = "utf-8"
    language: str = "unknown"

@dataclass
class AnalysisResult:
    """Result of file analysis"""
    file_info: FileInfo
    ast_data: Optional[Dict[str, Any]] = None
    functions: List[Dict[str, Any]] = None
    imports: List[Dict[str, Any]] = None
    classes: List[Dict[str, Any]] = None
    dependencies: List[str] = None
    complexity_metrics: Dict[str, Any] = None
    errors: List[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.imports is None:
            self.imports = []
        if self.functions is None:
            self.functions = []
        if self.classes is None:
            self.classes = []
        if self.dependencies is None:
            self.dependencies = []
        if self.complexity_metrics is None:
            self.complexity_metrics = {}
        if self.errors is None:
            self.errors = []

class BaseAnalyzer(ABC):
    """Abstract base class for code analyzers"""

    def __init__(self, max_file_size_mb: int = 10):
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    @abstractmethod
    def can_analyze(self, file_path: Path) -> bool:
        """Check if this analyzer can process the file"""
        pass

    @abstractmethod
    async def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze the file and return results"""
        pass

    def _check_file_size(self, file_path: Path) -> bool:
        """Check if file size is within limits"""
        try:
            size = file_path.stat().st_size
            return size <= self.max_file_size_bytes
        except Exception as e:
            logger.error(f"Error checking file size: {e}")
            return False

    def _count_lines(self, content: str) -> int:
        """Count number of lines in content"""
        return len(content.splitlines())

    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception:
            return 'utf-8'