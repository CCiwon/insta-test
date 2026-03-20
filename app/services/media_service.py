import re

from app.config import get_settings

# 허용 파일명 패턴: 영문자/숫자/하이픈/언더스코어 + 확장자
_SAFE_FILENAME_RE = re.compile(r'^[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+$')


class MediaService:
    def __init__(self) -> None:
        settings = get_settings()
        self._public_base_url = settings.public_base_url.rstrip("/")
        self._default_filename = settings.default_image_filename

    def build_image_url(self, override_filename: str | None) -> str:
        filename = (override_filename or self._default_filename).strip()
        if not _SAFE_FILENAME_RE.match(filename):
            raise ValueError(f"유효하지 않은 파일명입니다: {filename!r}")
        return f"{self._public_base_url}/static/{filename}"
