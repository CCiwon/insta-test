from app.config import get_settings


class MediaService:
    def __init__(self) -> None:
        settings = get_settings()
        self._public_base_url = settings.public_base_url.rstrip("/")
        self._default_filename = settings.default_image_filename

    def build_image_url(self, override_filename: str | None) -> str:
        filename = (override_filename or self._default_filename).strip()
        return f"{self._public_base_url}/static/{filename}"
