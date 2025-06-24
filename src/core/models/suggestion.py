"""
Suggestion model
"""
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text, Float, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.core.schemas.enums import SuggestionType, SuggestionStatus

if TYPE_CHECKING:
    from src.core.models.project import Project
    from src.core.models.file_analysis import FileAnalysis


class Suggestion(Base):
    __tablename__ = "suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    file_analysis_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("file_analyses.id", ondelete="SET NULL"),
        nullable=True
    )

    suggestion_type: Mapped[SuggestionType] = mapped_column(SQLEnum(SuggestionType))
    status: Mapped[SuggestionStatus] = mapped_column(
        SQLEnum(SuggestionStatus),
        default=SuggestionStatus.PENDING
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_before: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_after: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    line_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    impact_score: Mapped[float] = mapped_column(Float, default=0.0)

    extra: Mapped[dict] = mapped_column(JSON, default=dict) #metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="suggestions")
    file_analysis: Mapped[Optional["FileAnalysis"]] = relationship(
        "FileAnalysis",
        back_populates="suggestions"
    )

    def __repr__(self) -> str:
        return f"<Suggestion(id={self.id}, type={self.suggestion_type}, title='{self.title}')>"