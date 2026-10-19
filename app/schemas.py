from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
class ImageMetadata(BaseModel):
    subject: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=80)
    attributes: list[str] = Field(default_factory=list, max_length=30)
    caption: str = Field(min_length=1, max_length=1000)
    confidence: float = Field(ge=0, le=1)
class ImageCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    path: str = Field(min_length=1, max_length=500)
    source_url: str | None = None
    subject: str = "unknown"
    category: str = "unknown"
    attributes: list[str] = Field(default_factory=list)
    caption: str = ""
    confidence: float = Field(default=0.0, ge=0, le=1)
    metadata_source: str = "manual"
class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    path: str
    source_url: str | None
    subject: str
    category: str
    attributes: list
    caption: str
    confidence: float
    flagged_for_review: bool
    metadata_source: str
class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    content: str = Field(min_length=1)
    expected_subject: str | None = None
class GuardRequest(BaseModel):
    post_id: int
    image_id: int
    similarity: float = Field(ge=0, le=1)
class ReviewCreate(BaseModel):
    suggestion_id: int
    decision: Literal["approve", "reject"]
    note: str = ""
