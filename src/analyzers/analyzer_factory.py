"""
Analyzer factory for creating appropriate analyzers
"""
from pathlib import Path
from typing import Optional, List, Set
import logging
from src.analyzers.base import BaseAnalyzer
from src.analyzers.python_analyzer import PythonAnalyzer
from src.analyzers.constants import LANGUAGE_MAP

logger = logging.getLogger(__name__)


class AnalyzerFactory:
    """Factory for creating code analyzers"""
    
    def __init__(self):
        self._analyzers: List[BaseAnalyzer] = [
            PythonAnalyzer(),
            # TODO: Add more analyzers here
            # JavaScriptAnalyzer(),
            # TypeScriptAnalyzer(),
            # GoAnalyzer(),
        ]
    
    def get_analyzer(self, file_path: Path) -> Optional[BaseAnalyzer]:
        """Get appropriate analyzer for the file"""
        for analyzer in self._analyzers:
            if analyzer.can_analyze(file_path):
                return analyzer
        
        logger.warning(f"No analyzer found for file: {file_path}")
        return None
    
    def register_analyzer(self, analyzer: BaseAnalyzer) -> None:
        """Register a new analyzer"""
        self._analyzers.append(analyzer)
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        extensions = set()
        for analyzer in self._analyzers:
            if hasattr(analyzer, 'SUPPORTED_EXTENSIONS'):
                extensions.update(analyzer.SUPPORTED_EXTENSIONS)
        return sorted(list(extensions))
    
    def get_supported_languages(self) -> Set[str]:
        """Get list of supported programming languages"""
        supported_languages = set()
        supported_extensions = self.get_supported_extensions()
        
        for ext in supported_extensions:
            if ext in LANGUAGE_MAP:
                supported_languages.add(LANGUAGE_MAP[ext])
        
        return supported_languages


# Global factory instance
analyzer_factory = AnalyzerFactory()