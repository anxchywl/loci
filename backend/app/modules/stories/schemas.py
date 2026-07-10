import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.story import LocationPrecision, StoryVisibility

TITLE_MAX = 120
BODY_MAX = 4000
COMMENT_MAX = 1000


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    first_name: str | None
    photo_url: str | None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    color: str
    icon: str
    position: int


class StoryCreateRequest(BaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=TITLE_MAX)
    body: str = Field(min_length=1, max_length=BODY_MAX)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    location_precision: LocationPrecision
    visibility: StoryVisibility = StoryVisibility.public
    is_anonymous: bool = False
    happened_on: date | None = None


class PhotoResponse(BaseModel):
    id: uuid.UUID
    url: str
    thumb_url: str | None
    width: int | None
    height: int | None


class StoryResponse(BaseModel):
    id: uuid.UUID
    category_id: int
    title: str
    body: str
    happened_on: date | None
    lat: float
    lon: float
    location_precision: LocationPrecision
    visibility: StoryVisibility
    is_anonymous: bool
    created_at: datetime
    author: AuthorResponse | None
    reaction_count: int
    comment_count: int
    viewer_reacted: bool
    viewer_bookmarked: bool
    photos: list[PhotoResponse] = []


class CommentCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=COMMENT_MAX)


class CommentResponse(BaseModel):
    id: uuid.UUID
    body: str
    created_at: datetime
    author: AuthorResponse | None


class ReportCreateRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class PhotoUploadRequest(BaseModel):
    content_type: str = Field(pattern=r"^image/(jpeg|png|webp|heic)$")


class PhotoUploadResponse(BaseModel):
    photo_id: uuid.UUID
    upload_url: str
    expires_in: int
