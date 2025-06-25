"""
Project structure analyzer
"""
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging
from dataclasses import dataclass, field
from src.analyzers.constants import DEFAULT_IGNORE_PATTERNS, LANGUAGE_MAP

logger = logging.getLogger(__name__)

@dataclass
class FileNode:
    """Represents a file in the project structure"""
    name: str
    path: Path
    size: int
    extension: str
    language: Optional[str] = None
    analyzed: bool = False

@dataclass
class DirectoryNode:
    """Represents a directory in the project structure"""
    name: str
    path: Path
    files: List[FileNode] = field(default_factory=list)
    directories: Dict[str, 'DirectoryNode'] = field(default_factory=dict)

    def add_file(self, file_node: FileNode) -> None:
        """Add a file to this directory"""
        self.files.append(file_node)

    def add_directory(self, dir_node: 'DirectoryNode') -> None:
        """Add a subdirectory"""
        self.directories[dir_node.name] = dir_node

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "path": str(self.path),
            "files": [
                {
                    "name": f.name,
                    "size": f.size,
                    "extension": f.extension,
                    "language": f.language
                }
                for f in self.files
            ],
            "directories": {
                name: dir_node.to_dict()
                for name, dir_node in self.directories.items()
            }
        }

class ProjectStructureAnalyzer:
    """Analyzes project directory structure"""
    def __init__(
            self,
            ignore_patterns: Optional[Set[str]] = None,
            max_depth: int = 10
    ):
        self.max_depth = max_depth
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS
        self.total_files = 0
        self.total_size = 0
        self.file_types: Dict[str, int] = {}
        self.language_stats: Dict[str, int] = {}

    async def analyze(self, project_path: Path) -> Dict:
        """Analyze project structure"""
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        if not project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {project_path}")
        # Reset statistics
        self.total_files = 0
        self.total_size = 0
        self.file_types.clear()
        self.language_stats.clear()

        # Build directory tree
        root = await self._analyze_directory(project_path, depth=0)

        return {
            "root": root.to_dict(),
            "statistics": {
                "total_files": self.total_files,
                "total_size": self.total_size,
                "file_types": self.file_types,
                "language_stats": self.language_stats,
                "largest_files": await self._find_largest_files(project_path, n=10)
            }
        }

    async def _analyze_directory(
            self,
            dir_path: Path,
            depth: int
    ) -> DirectoryNode:
        """Recursively analyze a directory"""
        if depth > self.max_depth:
            logger.warning(f"Max depth reached at {dir_path}")
            return DirectoryNode(name=dir_path.name, path=dir_path)
        
        dir_node = DirectoryNode(name=dir_path.name, path=dir_path)

        try:
            for item in dir_path.iterdir():
                # Skip ignored items
                if self._should_ignore(item):
                    continue

                if item.is_file():
                    file_node = self._analyze_file(item)
                    dir_node.add_file(file_node)
                    # Update statistics
                    self.total_files += 1
                    self.total_size += file_node.size
                    self.file_types[file_node.extension] = self.file_types.get(file_node.extension, 0) + 1
                    if file_node.language:
                        self.language_stats[file_node.language] = self.language_stats.get(file_node.language, 0) + 1

                elif item.is_dir():
                    # Recursively analyze subdirectory
                    subdir = await self._analyze_directory(item, depth + 1)
                    dir_node.add_directory(subdir)

        except PermissionError:
            logger.warning(f"Permission denied: {dir_path}")
        except Exception as e:
            logger.error(f"Error analyzing directory {dir_path}: {e}")

        return dir_node
    
    def _analyze_file(self, file_path: Path) -> FileNode:
        """Analyze a single file"""
        try:
            stat = file_path.stat()
            extension = file_path.suffix.lower()

            return FileNode(
                name=file_path.name,
                path=file_path,
                size=stat.st_size,
                extension=extension,
                language=LANGUAGE_MAP.get(extension)
            )
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return FileNode(
                name=file_path.name,
                path=file_path,
                size=0,
                extension=file_path.suffix.lower()
            )

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored"""
        name = path.name
        
        # Check exact matches
        if name in self.ignore_patterns:
            return True
        
        # Check pattern matches
        for pattern in self.ignore_patterns:
            if pattern.startswith("*") and name.endswith(pattern[1:]):
                return True
            elif pattern.endswith("*") and name.startswith(pattern[:-1]):
                return True
        
        return False
    
    async def _find_largest_files(
        self,
        root_path: Path,
        n: int = 10
    ) -> List[Dict]:
        """Find the n largest files in the project"""
        files_with_size = []
        
        for path in root_path.rglob("*"):
            if path.is_file() and not self._should_ignore(path):
                try:
                    size = path.stat().st_size
                    files_with_size.append({
                        "path": str(path.relative_to(root_path)),
                        "size": size,
                        "size_mb": round(size / (1024 * 1024), 2)
                    })
                except Exception:
                    continue
        
        # Sort by size and return top n
        files_with_size.sort(key=lambda x: x["size"], reverse=True)
        return files_with_size[:n]

class DependencyMapper:
    """Maps dependencies between files in a project"""
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependencies: Dict[str, Set[str]] = {}

    def add_dependency(self, from_file: str, to_file: str) -> None:
        """Add a dependency relationship"""
        if from_file not in self.dependency_graph:
            self.dependency_graph[from_file] = set()
        self.dependency_graph[from_file].add(to_file)
        if to_file not in self.reverse_dependencies:
            self.reverse_dependencies[to_file] = set()
        self.reverse_dependencies[to_file].add(from_file)

    def get_dependencies(self, file: str) -> List[str]:
        """Get all files that this file depends on"""
        return list(self.dependency_graph.get(file, set()))
    
    def get_dependents(self, file: str) -> List[str]:
        """Get all files that depend on this file"""
        return list(self.reverse_dependencies.get(file, set()))
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the graph"""
        visited = set()
        rec_stack = set()
        cycles = []

        def _find_cycles(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    _find_cycles(neighbor, path.copy())
                else:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for node in self.dependency_graph:
            if node not in visited:
                _find_cycles(node, [])
        
        return cycles
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "dependencies": {
                k: list(v) for k, v in self.dependency_graph.items()
            },
            "reverse_dependencies": {
                k: list(v) for k, v in self.reverse_dependencies.items()
            },
            "circular_dependencies": self.find_circular_dependencies()
        }