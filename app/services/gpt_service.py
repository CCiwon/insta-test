from openai import AsyncOpenAI, OpenAIError

from app.config import get_settings
from app.prompts.reply_prompt import build_messages
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GPTService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model
        self._persona = settings.account_persona

    async def generate_reply_candidates(self, comment_text: str) -> list[str]:
        """댓글에 대한 GPT 답변 후보 3개를 반환한다."""
        messages = build_messages(comment_text, self._persona)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.8,
                max_tokens=300,
            )
        except OpenAIError as e:
            logger.error("GPT API 호출 실패 | error=%s", str(e))
            raise RuntimeError(f"GPT 응답 생성 실패: {e}") from e

        raw_text = response.choices[0].message.content or ""
        candidates = [
            line.strip()
            for line in raw_text.strip().splitlines()
            if line.strip()
        ]

        logger.info(
            "GPT 답변 후보 생성 완료 | comment=%.50s | candidates=%d",
            comment_text,
            len(candidates),
        )
        return candidates
