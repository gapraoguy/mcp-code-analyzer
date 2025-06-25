"""
Analyses API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.database import get_db
from src.core.models import Project, Analysis
from src.core.schemas import (
    AnalysisCreate,
    AnalysisResponse,
    AnalysisList,
    AnalysisUpdate
)
from src.core.schemas.enums import AnalysisStatus
from src.workers.tasks import analyze_project

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    analysis: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Analysis:
    """Start a new analysis for a project"""
    # Check if project exists
    project = await db.get(Project, analysis.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if there's already a running analysis
    stmt = select(Analysis).where(
        Analysis.project_id == analysis.project_id,
        Analysis.status == AnalysisStatus.RUNNING
    )
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Analysis already running for this project"
        )
    
    # Create new analysis
    db_analysis = Analysis(**analysis.model_dump())
    db.add(db_analysis)
    await db.commit()
    await db.refresh(db_analysis)
    
    # Start analysis task in background
    background_tasks.add_task(
        analyze_project.delay,
        project_id=project.id
    )
    
    return db_analysis


@router.get("/", response_model=AnalysisList)
async def list_analyses(
    project_id: Optional[int] = None,
    status: Optional[AnalysisStatus] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> AnalysisList:
    """List analyses with optional filters"""
    # Build query
    query = select(Analysis)
    
    if project_id:
        query = query.where(Analysis.project_id == project_id)
    if status:
        query = query.where(Analysis.status == status)
    
    # Count total
    count_stmt = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_stmt)
    
    # Get paginated results
    offset = (page - 1) * per_page
    stmt = query.offset(offset).limit(per_page).order_by(Analysis.created_at.desc())
    result = await db.execute(stmt)
    analyses = result.scalars().all()
    
    return AnalysisList(
        items=analyses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
) -> Analysis:
    """Get a specific analysis"""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis


@router.patch("/{analysis_id}", response_model=AnalysisResponse)
async def update_analysis(
    analysis_id: int,
    analysis_update: AnalysisUpdate,
    db: AsyncSession = Depends(get_db)
) -> Analysis:
    """Update analysis status or results"""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Update fields
    update_data = analysis_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(analysis, field, value)
    
    await db.commit()
    await db.refresh(analysis)
    return analysis


@router.post("/{analysis_id}/cancel")
async def cancel_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Cancel a running analysis"""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != AnalysisStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Only running analyses can be cancelled"
        )
    
    analysis.status = AnalysisStatus.CANCELLED
    await db.commit()
    
    # TODO: Cancel Celery task
    
    return {"message": "Analysis cancelled successfully"}

@router.post("/{analysis_id}/analyze-file")
async def analyze_single_file(
    analysis_id: int,
    file_path: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Analyze a single file within an analysis
    """
    # Get analysis
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get project
    project = await db.get(Project, analysis.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Start file analysis task
    from src.workers.tasks import analyze_file
    background_tasks.add_task(
        analyze_file.delay,
        file_path=file_path,
        project_id=project.id
    )
    
    return {
        "message": "File analysis started",
        "analysis_id": analysis_id,
        "file_path": file_path
    }