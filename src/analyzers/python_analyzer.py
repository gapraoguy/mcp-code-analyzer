"""
Python code analyzer using AST
"""

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import logging
from src.analyzers.base import BaseAnalyzer, AnalysisResult, FileInfo

logger = logging.getLogger(__name__)

class PythonAnalyzer(BaseAnalyzer):
    """Analyzer for Python source code"""

    SUPPORTED_EXTENSIONS = {'.py', '.pyw'}

    def can_analyze(self, file_path):
        """Check if this is a Python file"""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    async def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze Python file using AST"""
        try:
            if not self._check_file_size(file_path):
                raise ValueError(f"File too large: {file_path}")
            encoding = self._detect_encoding(file_path)
            content = file_path.read_text(encoding=encoding)
            file_info = FileInfo(
                path=file_path,
                size_bytes=file_path.stat().st_size,
                line_count=self._count_lines(content),
                encoding=encoding,
                language="python"
            )
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            visitor = PythonASTVisitor()
            visitor.visit(tree)
            complexity_metrics = self._calculate_complexity(tree, visitor)
            return AnalysisResult(
                file_info=file_info,
                ast_data=self._ast_to_dict(tree),
                imports=visitor.imports,
                functions=visitor.functions,
                classes=visitor.classes,
                dependencies=visitor.get_dependencies(),
                complexity_metrics=complexity_metrics
            )

        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return AnalysisResult(
                file_info=FileInfo(
                    path=file_path,
                    size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                    line_count=0,
                    language="python"
                ),
                errors=[{
                    "type": "SyntaxError",
                    "message": str(e),
                    "line": e.lineno,
                    "offset": e.offset
                }]
            )

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            raise

    def _ast_to_dict(self, node: ast.AST) -> Dict[str, Any]:
        """Convert AST node to dictionary (simplified)"""
        return {
            "type": node.__class__.__name__,
            "fields": {
                field: getattr(node, field)
                for field in node._fields
                if isinstance(getattr(node, field, None), (str, int, bool, type(None)))
            }
        }

    def _calculate_complexity(self, tree: ast.AST, visitor: 'PythonASTVisitor') -> Dict[str, Any]:
        """Calculate code complexity metrics"""
        return {
            "cyclomatic_complexity": self._calculate_cyclomatic_complexity(tree),
            "cognitive_complexity": 0,  # TODO: Implement cognitive complexity
            "maintainability_index": 0,  # TODO: Implement maintainability inde
            "lines_of_code": visitor.lines_of_code,
            "comment_lines": visitor.comment_lines,
        }

    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += len(node.items)
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _calculate_avg_function_length(self, functions: List[Dict[str, Any]]) -> float:
        """Calculate average function length"""
        if not functions:
            return 0

        total_lines = sum(
            func.get('line_end', 0) - func.get('line_start', 0) + 1
            for func in functions
        )
        return total_lines / len(functions)

class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor to extract information from Python code"""

    def __init__(self):
        self.imports: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.classes: List[Dict[str, Any]] = []
        self.dependencies: Set[str] = set()
        self.current_class: Optional[str] = None
        self.lines_of_code = 0
        self.comment_lines = 0
        self.blank_lines = 0

    def visit_Import(self, node):
        """Visit import statement"""
        for alias in node.names:
            self.imports.append({
                "module": alias.name,
                "alias": alias.asname,
                "line": alias.lineno,
                "type": "import"
            })
            self.dependencies.add(alias.name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from...import statement"""
        module = node.module or ''
        level = '.' * node.level + module

        for alias in node.names:
            self.imports.append({
                "module": level,
                "name": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
                "type": "from_import"
            })
            if module:
                self.dependencies.add(module.split('.')[0])
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition"""
        func_info = {
            "name": node.name,
            "line_start": node.lineno,
            "line_end": node.end_lineno,
            "parameters": [arg.arg for arg in node.args.args],
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "returns": self._get_annotation(node.returns),
            "docstring": ast.get_docstring(node),
            "is_async": False,
            "parent_class": self.current_class,
            "complexity": self._calculate_function_complexity(node)
        }
        self.functions.append(func_info)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition"""
        func_info = {
            "name": node.name,
            "line_start": node.lineno,
            "line_end": node.end_lineno,
            "parameters": [arg.arg for arg in node.args.args],
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "returns": self._get_annotation(node.returns),
            "docstring": ast.get_docstring(node),
            "is_async": True,
            "parent_class": self.current_class,
            "complexity": self._calculate_function_complexity(node)
        }
        self.functions.append(func_info)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition"""
        class_info = {
            "name": node.name,
            "line_start": node.lineno,
            "line_end": node.end_lineno,
            "bases": [self._get_name(base) for base in node.bases],
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "docstring": ast.get_docstring(node),
            "methods": [],
            "attributes": []
        }

        # Store current class context
        old_class = self.current_class
        self.current_class = node.name

        # Visit class body to collect methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                class_info["methods"].append(item.name)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                class_info["attributes"].append({
                    "name": item.target.id,
                    "type": self._get_annotation(item.annotation)
                })

        self.classes.append(class_info)
        self.generic_visit(node)

        # Restore class context
        self.current_class = old_class

    def get_dependencies(self) -> List[str]:
        """Get list of external dependencies"""
        # Filter out standard library modules (basic filter)
        stdlib_modules = sys.stdlib_module_names
        return sorted(list(self.dependencies - stdlib_modules))

    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name as string"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_name(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return "unknown"

    def _get_name(self, node: ast.AST) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "unknown"

    def _get_annotation(self, node: Optional[ast.AST]) -> Optional[str]:
        """Get type annotation as string"""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        # TODO: Handle more complex annotations
        return "complex_type"

    def _calculate_function_complexity(self, node: ast.AST) -> int:
        """Calculate complexity of a single function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        return complexity