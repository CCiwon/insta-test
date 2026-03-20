from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Instagram
    instagram_verify_token: str
    instagram_access_token: str
    instagram_app_secret: str
    instagram_user_id: str

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # 페르소나
    account_persona: str = "친근하고 따뜻한 인플루언서"

    # 게시물 기본값
    public_base_url: str
    default_image_filename: str = "post.jpg"
    default_caption: str = "안녕하세요! 오늘의 포스팅입니다 :)"

    # 관리자 API 키 (publish 엔드포인트 인증)
    admin_api_key: str

    # 환경
    env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def is_production(self) -> bool:
        return self.env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
