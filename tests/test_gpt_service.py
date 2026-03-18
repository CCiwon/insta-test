from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.gpt_service import GPTService


@pytest.mark.asyncio
async def test_generate_reply_candidates_returns_list():
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="감사해요!\n정말 기뻐요 :)\n꼭 써보세요!"))
    ]

    with patch.object(
        GPTService,
        "__init__",
        lambda self: None,
    ):
        service = GPTService()
        service._client = AsyncMock()
        service._client.chat.completions.create = AsyncMock(return_value=mock_response)
        service._model = "gpt-4o-mini"
        service._persona = "테스트 인플루언서"

        candidates = await service.generate_reply_candidates("예뻐요!")

    assert len(candidates) == 3
    assert candidates[0] == "감사해요!"


@pytest.mark.asyncio
async def test_generate_reply_candidates_openai_error():
    from openai import OpenAIError

    with patch.object(GPTService, "__init__", lambda self: None):
        service = GPTService()
        service._client = AsyncMock()
        service._client.chat.completions.create = AsyncMock(
            side_effect=OpenAIError("API error")
        )
        service._model = "gpt-4o-mini"
        service._persona = "테스트 인플루언서"

        with pytest.raises(RuntimeError, match="GPT 응답 생성 실패"):
            await service.generate_reply_candidates("테스트 댓글")
