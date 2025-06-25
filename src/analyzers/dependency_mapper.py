"""
Enhanced dependency mapping for Python projects
"""
from pathlib import Path
from typing import Dict, List, Set, Optional
import ast
import sys
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ImportInfo:
    """Information about an import statement"""
    from_file: Path
    import_type: str  # 'import' or 'from_import'
    module: str
    names: List[str]
    line_number: int
    is_relative: bool = False
    level: int = 0  # For relative imports


class PythonDependencyMapper:
    """Maps Python module dependencies"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dependencies: Dict[str, Set[str]] = {}
        self.imports: Dict[str, List[ImportInfo]] = {}
        self.module_paths: Dict[str, Path] = {}
    
    async def map_dependencies(self, files: List[Path]) -> Dict:
        """Map dependencies for all Python files"""
        # First pass: collect all module paths
        for file_path in files:
            if file_path.suffix == '.py':
                module_name = self._path_to_module(file_path)
                self.module_paths[module_name] = file_path

        # Second pass: analyze imports
        for file_path in files:
            if file_path.suffix == '.py':
                await self._analyze_file_imports(file_path)
        
        return {
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "imports": self._serialize_imports(),
            "module_paths": {k: str(v) for k, v in self.module_paths.items()},
            "external_dependencies": self._get_external_dependencies()
        }
    
    async def _analyze_file_imports(self, file_path: Path) -> None:
        """Analyze imports in a single file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))

            module_name = self._path_to_module(file_path)
            self.dependencies[module_name] = set()
            self.imports[module_name] = []

            visitor = ImportVisitor(file_path, module_name)
            visitor.visit(tree)

            # Process collected imports
            for import_info in visitor.imports:
                self.imports[module_name].append(import_info)

                # Resolve the imported module to a file
                resolved = self._resolve_import(
                    import_info.module,
                    file_path,
                    import_info.is_relative,
                    import_info.level
                )
                if resolved and (resolved in self.module_paths):
                    self.dependencies[module_name].add(resolved)
        except Exception as e:
            logger.error(f"Error analyzing imports in {file_path}: {e}")

    def _path_to_module(self, path: Path) -> str:
        """Convert file path to module name"""
        try:
            relative_path = path.relative_to(self.project_root)
            parts = list(relative_path.parts[:-1]) + [relative_path.stem]

            # Remove __init__ from module name
            if parts[-1] == '__init__':
                parts = parts[:-1]
            
            return '.'.join(parts)
        except ValueError:
            return path.stem
        
    def _resolve_import(
        self,
        module_name: str,
        from_file: Path,
        is_relative: bool,
        level: int
    ) -> Optional[str]:
        """Resolve an import to a module name"""
        if is_relative:
            # Handle relative imports
            current_module = self._path_to_module(from_file)
            current_parts = current_module.split('.')
            
            # Go up 'level' directories
            if level > len(current_parts):
                return None
            
            if level > 0:
                base_parts = current_parts[:-level]
            else:
                base_parts = current_parts[:-1]
            
            if module_name:
                return '.'.join(base_parts + module_name.split('.'))
            else:
                return '.'.join(base_parts)
        else:
            # Absolute import - check if it's internal
            for known_module in self.module_paths:
                if known_module == module_name or known_module.startswith(module_name + '.'):
                    return module_name
            
            # Check if it's a submodule of a known module
            parts = module_name.split('.')
            for i in range(len(parts), 0, -1):
                partial = '.'.join(parts[:i])
                if partial in self.module_paths:
                    return partial
            
            return None

    def _serialize_imports(self) -> Dict[str, List[Dict]]:
        """Serialize import information"""
        result = {}
        for module, imports in self.imports.items():
            result[module] = [
                {
                    "type": imp.import_type,
                    "module": imp.module,
                    "names": imp.names,
                    "line": imp.line_number,
                    "is_relative": imp.is_relative,
                    "level": imp.level
                }
                for imp in imports
            ]
        return result
    
    def _get_external_dependencies(self) -> List[str]:
        """Get list of external (third-party) dependencies"""
        external = set()
        
        for imports_list in self.imports.values():
            for import_info in imports_list:
                # Skip relative imports
                if import_info.is_relative:
                    continue
                
                # Skip if it's an internal module
                if self._resolve_import(
                    import_info.module,
                    import_info.from_file,
                    False,
                    0
                ):
                    continue
                
                # Extract base package name
                base_package = import_info.module.split('.')[0]
                
                # Skip standard library modules
                if not self._is_stdlib_module(base_package):
                    external.add(base_package)

        return sorted(list(external))

    def _is_stdlib_module(self, module: str) -> bool:
        """Check if module is part of Python standard library"""
        return module in sys.stdlib_module_names


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to collect import information"""

    def __init__(self, file_path: Path, module_name: str):
        self.file_path = file_path
        self.module_name = module_name
        self.imports: List[ImportInfo] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Handle import statements"""
        for alias in node.names:
            self.imports.append(ImportInfo(
                from_file=self.file_path,
                import_type='import',
                module=alias.name,
                names=[alias.asname or alias.name],
                line_number=node.lineno,
                is_relative=False,
                level=0
            ))
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle from...import statements"""
        module = node.module or ''
        level = node.level
        
        names = []
        for alias in node.names:
            names.append(alias.name)
        
        self.imports.append(ImportInfo(
            from_file=self.file_path,
            import_type='from_import',
            module=module,
            names=names,
            line_number=node.lineno,
            is_relative=level > 0,
            level=level
        ))
        self.generic_visit(node)