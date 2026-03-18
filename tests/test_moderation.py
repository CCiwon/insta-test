from app.utils.moderation import should_reply


def test_should_reply_allows_normal_text():
    assert should_reply("너무 예뻐요! 어디서 샀어요?")


def test_should_reply_blocks_empty_or_short():
    assert not should_reply("")
    assert not should_reply(" ")
    assert not should_reply("ㅋ")


def test_should_reply_blocks_spam_keywords():
    assert not should_reply("무료 이벤트 참여하고 링크 클릭!")


def test_should_reply_blocks_urls_emails_phones():
    assert not should_reply("https://spam.example.com")
    assert not should_reply("문의는 test@example.com 으로")
    assert not should_reply("연락처 010-1234-5678")


def test_should_reply_blocks_profanity():
    assert not should_reply("씨발 뭐야")


def test_should_reply_blocks_repetition():
    assert not should_reply("ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ")
