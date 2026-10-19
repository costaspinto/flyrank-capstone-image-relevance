from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
def utcnow():
    return datetime.now(timezone.utc)
class ImageAsset(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    path: Mapped[str] = mapped_column(String(500), unique=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    subject: Mapped[str] = mapped_column(String(160), default="unknown", index=True)
    category: Mapped[str] = mapped_column(String(80), default="unknown", index=True)
    attributes: Mapped[list] = mapped_column(JSON, default=list)
    caption: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    flagged_for_review: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    metadata_source: Mapped[str] = mapped_column(String(30), default="unprocessed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    suggestions: Mapped[list["Suggestion"]] = relationship(back_populates="image")
class ArticlePost(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), index=True)
    content: Mapped[str] = mapped_column(Text)
    expected_subject: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    suggestions: Mapped[list["Suggestion"]] = relationship(back_populates="post")
class Suggestion(Base):
    __tablename__ = "suggestions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), index=True)
    similarity: Mapped[float] = mapped_column(Float)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="suggested", index=True)
    explanation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    post: Mapped["ArticlePost"] = relationship(back_populates="suggestions")
    image: Mapped["ImageAsset"] = relationship(back_populates="suggestions")
class BackgroundJob(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(30), default="queued", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
class CostEntry(Base):
    __tablename__ = "cost_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), index=True)
    operation: Mapped[str] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(120), default="local")
    reference: Mapped[str] = mapped_column(String(200), default="")
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
Index("ix_suggestion_post_similarity", Suggestion.post_id, Suggestion.similarity)
