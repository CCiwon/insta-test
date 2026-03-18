from typing import Any

from pydantic import BaseModel, Field


class WebhookChangeValue(BaseModel):
    """Instagram 댓글 이벤트의 실제 데이터"""

    id: str | None = None
    text: str | None = None
    from_: dict[str, str] | None = Field(  # {"id": ..., "username": ...}
        default=None,
        alias="from",
    )
    media: dict[str, str] | None = None  # {"id": ..., "media_product_type": ...}
    parent_id: str | None = None
    timestamp: str | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class WebhookChange(BaseModel):
    field: str
    value: WebhookChangeValue | dict[str, Any]

    model_config = {"extra": "allow"}


class WebhookEntry(BaseModel):
    id: str
    time: int
    changes: list[WebhookChange]

    model_config = {"extra": "allow"}


class WebhookPayload(BaseModel):
    object: str  # "instagram"
    entry: list[WebhookEntry]

    model_config = {"extra": "allow"}


class ParsedComment(BaseModel):
    """서비스 레이어에서 사용할 정제된 댓글 데이터"""

    comment_id: str
    comment_text: str
    commenter_id: str | None
    commenter_username: str | None
    media_id: str | None
    raw_entry_id: str
