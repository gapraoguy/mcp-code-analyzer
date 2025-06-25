"""
Suggestions API endpoints
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.database import get_db
from src.core.models import Project, Suggestion, FileAnalysis
from src.core.schemas import (
    SuggestionCreate,
    SuggestionResponse,
    SuggestionList,
    SuggestionUpdate,
    SuggestionApply,
    ErrorFixRequest,
    FeatureRequest
)
from src.core.schemas.enums import SuggestionType, SuggestionStatus
from src.workers.tasks import generate_suggestion

router = APIRouter()


@router.post("/error-fix", response_model=SuggestionResponse)
async def suggest_error_fix(
    request: ErrorFixRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Suggestion:
    """Generate fix suggestion for an error"""
    # Verify project exists
    project = await db.get(Project, request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create suggestion placeholder
    suggestion = Suggestion(
        project_id=request.project_id,
        suggestion_type=SuggestionType.ERROR_FIX,
        title=f"Fix for: {request.error_message[:100]}...",
        description=f"Error: {request.error_message}",
        extra={
            "file_path": request.file_path,
            "line_number": request.line_number,
            "context_lines": request.context_lines
        }
    )
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)
    
    # Start generation task
    background_tasks.add_task(
        generate_suggestion.delay,
        request_type="error_fix",
        context={
            "suggestion_id": suggestion.id,
            "error_message": request.error_message,
            "file_path": request.file_path,
            "line_number": request.line_number
        }
    )
    
    return suggestion


@router.post("/feature", response_model=SuggestionResponse)
async def suggest_feature_implementation(
    request: FeatureRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Suggestion:
    """Generate implementation suggestion for a new feature"""
    # Verify project exists
    project = await db.get(Project, request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create suggestion placeholder
    suggestion = Suggestion(
        project_id=request.project_id,
        suggestion_type=SuggestionType.FEATURE,
        title=f"Implementation: {request.feature_description[:100]}...",
        description=request.feature_description,
        extra={
            "target_file": request.target_file,
            "integration_points": request.integration_points,
            "constraints": request.constraints
        }
    )
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)
    
    # Start generation task
    background_tasks.add_task(
        generate_suggestion.delay,
        request_type="feature",
        context={
            "suggestion_id": suggestion.id,
            "feature_description": request.feature_description,
            "target_file": request.target_file,
            "integration_points": request.integration_points
        }
    )
    
    return suggestion


@router.get("/", response_model=SuggestionList)
async def list_suggestions(
    project_id: Optional[int] = None,
    suggestion_type: Optional[SuggestionType] = None,
    status: Optional[SuggestionStatus] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> SuggestionList:
    """List suggestions with optional filters"""
    # Build query
    query = select(Suggestion)
    
    if project_id:
        query = query.where(Suggestion.project_id == project_id)
    if suggestion_type:
        query = query.where(Suggestion.suggestion_type == suggestion_type)
    if status:
        query = query.where(Suggestion.status == status)
    
    # Count total
    count_stmt = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_stmt)
    
    # Get paginated results
    offset = (page - 1) * per_page
    stmt = query.offset(offset).limit(per_page).order_by(Suggestion.created_at.desc())
    result = await db.execute(stmt)
    suggestions = result.scalars().all()
    
    # Get counts by type and status for summary
    type_counts = {}
    status_counts = {}
    if suggestions:
        # Count by type
        type_stmt = select(
            Suggestion.suggestion_type,
            func.count(Suggestion.id)
        ).group_by(Suggestion.suggestion_type)
        if project_id:
            type_stmt = type_stmt.where(Suggestion.project_id == project_id)
        type_result = await db.execute(type_stmt)
        type_counts = {str(t): c for t, c in type_result}
        
        # Count by status
        status_stmt = select(
            Suggestion.status,
            func.count(Suggestion.id)
        ).group_by(Suggestion.status)
        if project_id:
            status_stmt = status_stmt.where(Suggestion.project_id == project_id)
        status_result = await db.execute(status_stmt)
        status_counts = {str(s): c for s, c in status_result}
    
    return SuggestionList(
        items=suggestions,
        total=total,
        page=page,
        per_page=per_page,
        by_type=type_counts,
        by_status=status_counts
    )


@router.get("/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(
    suggestion_id: int,
    db: AsyncSession = Depends(get_db)
) -> Suggestion:
    """Get a specific suggestion"""
    suggestion = await db.get(Suggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return suggestion


@router.patch("/{suggestion_id}", response_model=SuggestionResponse)
async def update_suggestion(
    suggestion_id: int,
    suggestion_update: SuggestionUpdate,
    db: AsyncSession = Depends(get_db)
) -> Suggestion:
    """Update suggestion status or scores"""
    suggestion = await db.get(Suggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Update fields
    update_data = suggestion_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(suggestion, field, value)
    
    await db.commit()
    await db.refresh(suggestion)
    return suggestion


@router.post("/{suggestion_id}/apply", response_model=SuggestionResponse)
async def apply_suggestion(
    suggestion_id: int,
    apply_request: SuggestionApply,
    db: AsyncSession = Depends(get_db)
) -> Suggestion:
    """Apply or reject a suggestion"""
    suggestion = await db.get(Suggestion, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    if suggestion.status != SuggestionStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending suggestions can be applied"
        )
    
    if apply_request.apply:
        suggestion.status = SuggestionStatus.APPLIED
        suggestion.applied_at = datetime.utcnow()
        
        # TODO: Actually apply the code changes
        if apply_request.modified_code:
            suggestion.code_after = apply_request.modified_code
    else:
        suggestion.status = SuggestionStatus.REJECTED
    
    await db.commit()
    await db.refresh(suggestion)
    return suggestion