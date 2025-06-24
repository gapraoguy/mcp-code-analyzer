"""
Projects API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.database import get_db
from src.core.models.project import Project
from src.core.models.analysis import Analysis
from src.core.models.suggestion import Suggestion
from src.core.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectList
)
from src.core.schemas.enums import SuggestionStatus

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
) -> Project:
    """Create a new project"""
    # Check if project already exists
    stmt = select(Project).where(Project.path == project.path)
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Project already exists")

    # Create new project
    db_project = Project(**project.model_dump())
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


@router.get("/", response_model=ProjectList)
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> ProjectList:
    """List all projects with pagination"""
    # Count total projects
    count_stmt = select(func.count()).select_from(Project)
    total = await db.scalar(count_stmt)

    # Get paginated projects
    offset = (page - 1) * per_page
    stmt = select(Project).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    projects = result.scalars().all()

    return ProjectList(
        items=projects,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> Project:
    """Get a specific project"""
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get counts for response
    analysis_count = await db.scalar(
        select(func.count()).select_from(Analysis).where(Analysis.project_id == project_id)
    )
    suggestion_count = await db.scalar(
        select(func.count()).select_from(Suggestion).where(Suggestion.project_id == project_id)
    )
    pending_suggestion_count = await db.scalar(
        select(func.count()).select_from(Suggestion).where(
            Suggestion.project_id == project_id,
            Suggestion.status == SuggestionStatus.PENDING
        )
    )

    # Add counts to response
    project_dict = project.__dict__.copy()
    project_dict.update({
        "analysis_count": analysis_count,
        "suggestion_count": suggestion_count,
        "pending_suggestion_count": pending_suggestion_count
    })

    return ProjectResponse(**project_dict)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
) -> Project:
    """Update a project"""
    # Get existing project
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete a project"""
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()

    return {"message": "Project deleted successfully"}