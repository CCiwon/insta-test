from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.schemas.publish import PublishRequest, PublishResponse
from app.services.content_service import ContentService
from app.services.instagram_publish_service import InstagramPublishService
from app.services.media_service import MediaService
from app.utils.logger import get_logger

router = APIRouter(prefix="/publish", tags=["publish"])
logger = get_logger(__name__)

content_service = ContentService()
media_service = MediaService()
publish_service = InstagramPublishService()

_bearer = HTTPBearer()


def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> None:
    expected = get_settings().admin_api_key
    if credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


@router.post("/feed", response_model=PublishResponse, dependencies=[Depends(verify_api_key)])
async def publish_feed(
    payload: PublishRequest,
) -> PublishResponse:
    image_url = media_service.build_image_url(payload.image_filename)
    caption = content_service.build_caption(payload.caption)

    try:
        result = await publish_service.publish_feed_image(image_url, caption)
    except Exception as e:
        logger.error("피드 게시 실패 | error=%s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Feed publish failed",
        ) from e

    return PublishResponse(
        status="ok",
        creation_id=result.get("creation_id"),
        media_id=result.get("media_id"),
    )


@router.post("/story", response_model=PublishResponse, dependencies=[Depends(verify_api_key)])
async def publish_story(
    payload: PublishRequest,
) -> PublishResponse:
    image_url = media_service.build_image_url(payload.image_filename)

    try:
        result = await publish_service.publish_story_image(image_url)
    except Exception as e:
        logger.error("스토리 게시 실패 | error=%s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Story publish failed",
        ) from e

    return PublishResponse(
        status="ok",
        creation_id=result.get("creation_id"),
        media_id=result.get("media_id"),
    )
