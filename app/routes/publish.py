from fastapi import APIRouter, HTTPException, status
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


@router.post("/feed", response_model=PublishResponse)
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
            detail=f"Feed publish failed: {e}",
        ) from e

    return PublishResponse(
        status="ok",
        creation_id=result.get("creation_id"),
        media_id=result.get("media_id"),
    )


@router.post("/story", response_model=PublishResponse)
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
            detail=f"Story publish failed: {e}",
        ) from e

    return PublishResponse(
        status="ok",
        creation_id=result.get("creation_id"),
        media_id=result.get("media_id"),
    )
