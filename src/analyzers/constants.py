"""
Constants for code analyzers
"""

# Common ignore patterns for project analysis
DEFAULT_IGNORE_PATTERNS = {
    "__pycache__", ".git", ".venv", "venv", "env",
    "node_modules", ".idea", ".vscode", "*.pyc",
    "*.pyo", ".DS_Store", "*.egg-info", "dist",
    "build", ".pytest_cache", ".mypy_cache",
    ".coverage", "htmlcov", ".tox", ".ruff_cache",
    "*.log", "*.sqlite", "*.db", ".env*",
    ".dockerignore", ".gitignore"
}

# Language detection by file extension
LANGUAGE_MAP = {
    # Python
    ".py": "python",
    ".pyw": "python",
    ".pyx": "python",
    ".pxd": "python",
    ".pyi": "python",
    # JavaScript/TypeScript
    ".js": "javascript",
    ".mjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    # Java/JVM
    ".java": "java",
    ".scala": "scala",
    ".kt": "kotlin",
    ".groovy": "groovy",
    # C/C++
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".hxx": "cpp",
    # Other languages
    ".go": "go",
    ".rs": "rust",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".r": "r",
    ".R": "r",
    ".m": "matlab",
    ".jl": "julia",
    ".lua": "lua",
    ".dart": "dart",
    # Shell
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".fish": "shell",
    ".ps1": "powershell",
    ".psm1": "powershell",
    # Data/Config
    ".sql": "sql",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "conf",
    # Web
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    # Documentation
    ".md": "markdown",
    ".rst": "restructuredtext",
    ".tex": "latex",
    ".adoc": "asciidoc",
}