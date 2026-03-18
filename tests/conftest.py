import os

import pytest

# 모든 테스트 파일보다 먼저 환경변수를 확정한다.
os.environ["INSTAGRAM_VERIFY_TOKEN"] = "test_verify_token"
os.environ["INSTAGRAM_ACCESS_TOKEN"] = "test_access_token"
os.environ["INSTAGRAM_APP_SECRET"] = "test_app_secret"
os.environ["INSTAGRAM_USER_ID"] = "test_user_id"
os.environ["OPENAI_API_KEY"] = "sk-test"
os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
os.environ["PUBLIC_BASE_URL"] = "https://test.ngrok-free.app"
os.environ["DEFAULT_IMAGE_FILENAME"] = "post.jpg"
os.environ["DEFAULT_CAPTION"] = "테스트 캡션"
os.environ["ENV"] = "development"


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """테스트마다 lru_cache를 초기화해 환경변수 오염을 방지한다."""
    from app.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
