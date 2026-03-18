import httpx

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v20.0"


class InstagramService:
    def __init__(self) -> None:
        settings = get_settings()
        self._access_token = settings.instagram_access_token

    async def post_reply(self, comment_id: str, reply_text: str) -> dict:
        """
        특정 댓글에 답글을 전송한다.

        1차 MVP: dry-run 모드로 실제 전송 없이 로그만 출력.
        2차 MVP: 아래 주석 처리된 httpx 블록을 활성화.
        """
        logger.info(
            "[DRY-RUN] 답글 전송 예정 | comment_id=%s | preview=%.80s",
            comment_id,
            reply_text,
        )
        return {"status": "dry_run", "comment_id": comment_id}

        # --- 2차 MVP: 실제 전송 ---
        # url = f"{GRAPH_API_BASE}/{comment_id}/replies"
        # params = {
        #     "message": reply_text,
        #     "access_token": self._access_token,
        # }
        # async with httpx.AsyncClient(timeout=10.0) as client:
        #     response = await client.post(url, params=params)
        #     response.raise_for_status()
        #     return response.json()
