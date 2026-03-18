import hashlib
import hmac
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse

from app.config import Settings, get_settings
from app.schemas.webhook import WebhookPayload
from app.services.comment_service import extract_comment, handle_comment
from app.utils.logger import get_logger

router = APIRouter(prefix="/webhook", tags=["webhook"])
logger = get_logger(__name__)


def _verify_signature(
    raw_body: bytes,
    signature_header: str | None,
    app_secret: str,
) -> bool:
    """
    Instagram이 보내는 X-Hub-Signature-256 헤더를 검증한다.
    서명 불일치 시 False 반환.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected = hmac.new(
        app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    received = signature_header[len("sha256="):]
    return hmac.compare_digest(expected, received)


@router.get("", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    settings: Settings = Depends(get_settings),
) -> str:
    """
    Instagram Webhook 최초 등록 시 허브 검증 엔드포인트.
    hub.verify_token이 일치하면 hub.challenge를 그대로 반환한다.
    """
    if hub_mode != "subscribe":
        logger.warning("잘못된 hub.mode | hub_mode=%s", hub_mode)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid hub.mode",
        )

    if hub_verify_token != settings.instagram_verify_token:
        logger.warning("Webhook 검증 토큰 불일치")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify token mismatch",
        )

    logger.info("Webhook 허브 검증 성공")
    return hub_challenge


@router.post("", status_code=status.HTTP_200_OK)
async def receive_webhook(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """
    Instagram 댓글 이벤트를 수신하는 엔드포인트.

    주의: Instagram은 200 응답을 5초 내에 받지 못하면 재시도한다.
    현재는 동기적으로 처리하나, 2차 MVP에서 BackgroundTasks 또는
    ARQ/Celery 큐로 분리 권장.
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_signature(raw_body, signature, settings.instagram_app_secret):
        logger.warning("Webhook 서명 검증 실패 | signature=%s", signature)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature",
        )

    try:
        payload = WebhookPayload.model_validate_json(raw_body)
    except Exception as e:
        logger.error("Webhook payload 파싱 실패 | error=%s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid payload format",
        ) from e

    if payload.object != "instagram":
        logger.info("instagram 외 오브젝트 수신, 무시 | object=%s", payload.object)
        return {"status": "ignored"}

    for entry in payload.entry:
        for change in entry.changes:
            comment = extract_comment(change, entry.id)
            if comment:
                await handle_comment(comment)

    return {"status": "ok"}
