from app.config import get_settings


class ContentService:
    def __init__(self) -> None:
        settings = get_settings()
        self._default_caption = settings.default_caption

    def build_caption(self, override_caption: str | None) -> str:
        if override_caption and override_caption.strip():
            return override_caption.strip()
        return self._default_caption
