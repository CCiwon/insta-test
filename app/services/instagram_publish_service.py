import httpx

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v20.0"


class InstagramPublishService:
    def __init__(self) -> None:
        settings = get_settings()
        self._access_token = settings.instagram_access_token
        self._user_id = settings.instagram_user_id
        self._max_attempts = 3

    async def publish_feed_image(self, image_url: str, caption: str) -> dict:
        creation_id = await self._create_container(
            image_url=image_url,
            caption=caption,
            media_type=None,
        )
        media_id = await self._publish_container(creation_id)
        return {"creation_id": creation_id, "media_id": media_id}

    async def publish_story_image(self, image_url: str) -> dict:
        creation_id = await self._create_container(
            image_url=image_url,
            caption=None,
            media_type="STORIES",
        )
        media_id = await self._publish_container(creation_id)
        return {"creation_id": creation_id, "media_id": media_id}

    async def _create_container(
        self,
        image_url: str,
        caption: str | None,
        media_type: str | None,
    ) -> str:
        url = f"{GRAPH_API_BASE}/{self._user_id}/media"
        params: dict[str, str] = {
            "image_url": image_url,
            "access_token": self._access_token,
        }
        if caption:
            params["caption"] = caption
        if media_type:
            params["media_type"] = media_type

        data = await self._post_with_retry(url, params)

        creation_id = data.get("id")
        if not creation_id:
            raise RuntimeError("미디어 컨테이너 생성 실패: id 없음")
        return creation_id

    async def _publish_container(self, creation_id: str) -> str:
        url = f"{GRAPH_API_BASE}/{self._user_id}/media_publish"
        params = {
            "creation_id": creation_id,
            "access_token": self._access_token,
        }
        data = await self._post_with_retry(url, params)

        media_id = data.get("id")
        if not media_id:
            raise RuntimeError("미디어 퍼블리시 실패: id 없음")
        logger.info("미디어 퍼블리시 성공 | media_id=%s", media_id)
        return media_id

    async def _post_with_retry(self, url: str, params: dict[str, str]) -> dict:
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(url, params=params)
                    response.raise_for_status()
                    return response.json()
            except (httpx.HTTPError, ValueError) as e:
                last_error = e
                logger.warning(
                    "Instagram API 요청 실패 | attempt=%s | url=%s | error=%s",
                    attempt,
                    url,
                    str(e),
                )

        raise RuntimeError(f"Instagram API 요청 실패: {last_error}")
