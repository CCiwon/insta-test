from pydantic import BaseModel


class PublishRequest(BaseModel):
    caption: str | None = None
    image_filename: str | None = None


class PublishResponse(BaseModel):
    status: str
    creation_id: str | None = None
    media_id: str | None = None
