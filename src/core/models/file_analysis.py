"""
File analysis model
"""
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

if TYPE_CHECKING:
    from src.core.models.analysis import Analysis
    from src.core.models.suggestion import Suggestion


class FileAnalysis(Base):
    __tablename__ = "file_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Analysis results
    ast_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    imports: Mapped[list] = mapped_column(JSON, default=list)
    functions: Mapped[list] = mapped_column(JSON, default=list)
    classes: Mapped[list] = mapped_column(JSON, default=list)
    dependencies: Mapped[list] = mapped_column(JSON, default=list)
    complexity_metrics: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="files")
    suggestions: Mapped[list["Suggestion"]] = relationship(
        "Suggestion",
        back_populates="file_analysis",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FileAnalysis(id={self.id}, file_path='{self.file_path}')>"