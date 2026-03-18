from app.schemas.webhook import ParsedComment, WebhookChange, WebhookChangeValue
from app.services.gpt_service import GPTService
from app.utils.logger import get_logger
from app.utils.moderation import should_reply

logger = get_logger(__name__)

# 앱 수명 동안 단일 인스턴스 재사용
gpt_service = GPTService()


def extract_comment(change: WebhookChange, entry_id: str) -> ParsedComment | None:
    """
    WebhookChange에서 댓글 데이터를 추출한다.
    `comments` 필드가 아닌 이벤트는 무시한다.
    """
    if change.field != "comments":
        logger.debug("comments 외 필드 이벤트 무시 | field=%s", change.field)
        return None

    value = change.value
    if isinstance(value, dict):
        value = WebhookChangeValue(**value)

    if not value.text:
        logger.warning("댓글 텍스트 없음 | value=%s", value.model_dump())
        return None

    from_data = value.from_ or {}

    return ParsedComment(
        comment_id=value.id or "",
        comment_text=value.text,
        commenter_id=from_data.get("id"),
        commenter_username=from_data.get("username"),
        media_id=(value.media or {}).get("id"),
        raw_entry_id=entry_id,
    )


async def handle_comment(comment: ParsedComment) -> None:
    """
    정제된 댓글을 받아 GPT 답변 후보를 생성한다.

    확장 포인트:
    - DB 저장: await db.save_reply_candidates(comment, candidates)
    - 관리자 큐: await queue.publish("review_queue", {...})
    - 자동 답글: await instagram_service.post_reply(comment.comment_id, candidates[0])
    """
    logger.info(
        "댓글 수신 | comment_id=%s | username=%s | text=%.100s",
        comment.comment_id,
        comment.commenter_username,
        comment.comment_text,
    )

    if not should_reply(comment.comment_text):
        logger.info("댓글 필터링됨 | comment_id=%s", comment.comment_id)
        return

    try:
        candidates = await gpt_service.generate_reply_candidates(comment.comment_text)
    except RuntimeError as e:
        logger.error("답변 생성 실패 | error=%s", str(e))
        return

    for i, candidate in enumerate(candidates, 1):
        logger.info("[답변 후보 %d] %s", i, candidate)
