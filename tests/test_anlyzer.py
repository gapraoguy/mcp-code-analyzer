#!/usr/bin/env python
"""
Test analyzer functionality
"""
import asyncio
from pathlib import Path
from src.analyzers import analyzer_factory, ProjectStructureAnalyzer

async def test_analyzer():
    # Test Python analyzer
    analyzer = analyzer_factory.get_analyzer(Path("src/analyzers/base.py"))
    if analyzer:
        result = await analyzer.analyze(Path("src/analyzers/base.py"))
        print(f"Analysis result: {result.file_info}")
    
    # Test project structure
    structure_analyzer = ProjectStructureAnalyzer()
    project_result = await structure_analyzer.analyze(Path("."))
    print(f"Project files: {project_result['statistics']['total_files']}")

if __name__ == "__main__":
    asyncio.run(test_analyzer())