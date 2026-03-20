import re

SYSTEM_PROMPT_TEMPLATE = """
당신은 {persona}입니다.
인스타그램 게시물에 달린 팔로워의 댓글에 진심 어린 답글을 작성합니다.

답글 작성 원칙:
- 자연스럽고 따뜻한 말투 유지
- 1~2문장 이내로 간결하게
- 이모지는 1~2개 이하로 절제해서 사용
- 광고성 문구, 외부 링크, 개인정보 요청 금지
- 질문에는 구체적으로 답변, 칭찬에는 감사 표현
""".strip()

USER_PROMPT_TEMPLATE = """
팔로워 댓글: "{comment_text}"

이 댓글에 대한 자연스러운 답글 후보 3개를 작성해주세요.
각 후보는 번호 없이 줄바꿈으로 구분해주세요.
""".strip()

# 댓글 최대 허용 길이 (GPT 토큰 비용 및 프롬프트 인젝션 방어)
_MAX_COMMENT_LENGTH = 500


def sanitize_comment(text: str) -> str:
    """
    GPT 프롬프트 삽입 전 댓글 텍스트를 정제한다.

    - 최대 길이 초과 시 자름
    - 프롬프트 구조를 깨는 큰따옴표를 단따옴표로 치환
    - 역할 전환을 시도하는 대표 패턴 제거
    """
    text = text.strip()
    text = text[:_MAX_COMMENT_LENGTH]
    # 프롬프트 구분자(큰따옴표) 이스케이프
    text = text.replace('"', "'")
    # "Ignore previous instructions" 류 인젝션 패턴 제거
    text = re.sub(
        r'(?i)(ignore|forget|disregard)\s+(all\s+)?(previous|prior|above|system)\s+(instructions?|prompts?|rules?)',
        '[filtered]',
        text,
    )
    return text


def build_messages(comment_text: str, persona: str) -> list[dict[str, str]]:
    safe_text = sanitize_comment(comment_text)
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT_TEMPLATE.format(persona=persona),
        },
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(comment_text=safe_text),
        },
    ]
