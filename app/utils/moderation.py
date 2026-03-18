import re


_URL_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)
_EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
_PHONE_PATTERN = re.compile(r"\b(\+?\d[\d\-\s]{7,}\d)\b")

_SPAM_KEYWORDS = {
    "무료",
    "광고",
    "홍보",
    "협찬",
    "할인",
    "구독",
    "dm",
    "디엠",
    "링크",
    "클릭",
    "follow",
    "팔로우",
    "crypto",
    "코인",
}

_PROFANITY = {
    "씨발",
    "시발",
    "ㅅㅂ",
    "병신",
    "ㅂㅅ",
    "좆",
    "ㅈ같",
    "fuck",
    "shit",
}


def should_reply(comment_text: str) -> bool:
    text = (comment_text or "").strip()
    if not text:
        return False

    if len(text) < 2:
        return False

    lower = text.lower()

    if _URL_PATTERN.search(lower):
        return False

    if _EMAIL_PATTERN.search(lower):
        return False

    if _PHONE_PATTERN.search(lower):
        return False

    if any(keyword in lower for keyword in _SPAM_KEYWORDS):
        return False

    if any(word in lower for word in _PROFANITY):
        return False

    # 과도한 반복 문자나 이모지 스팸
    if re.search(r"(.)\1{6,}", text):
        return False

    # 이모지/기호만 있는 경우
    if re.fullmatch(r"[\W_]+", text):
        return False

    return True
