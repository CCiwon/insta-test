from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_AUTH = {"Authorization": "Bearer test_admin_key"}


# ────────────────────────────────────────────────
# CRITICAL #1 — 인증 검사
# ────────────────────────────────────────────────

def test_publish_feed_no_auth_returns_403():
    response = client.post(
        "/publish/feed",
        json={"caption": "테스트 캡션", "image_filename": "post.jpg"},
    )
    assert response.status_code == 403


def test_publish_feed_wrong_token_returns_403():
    response = client.post(
        "/publish/feed",
        json={"caption": "테스트 캡션", "image_filename": "post.jpg"},
        headers={"Authorization": "Bearer wrong_key"},
    )
    assert response.status_code == 401


def test_publish_story_no_auth_returns_403():
    response = client.post(
        "/publish/story",
        json={"image_filename": "post.jpg"},
    )
    assert response.status_code == 403


def test_publish_story_wrong_token_returns_403():
    response = client.post(
        "/publish/story",
        json={"image_filename": "post.jpg"},
        headers={"Authorization": "Bearer wrong_key"},
    )
    assert response.status_code == 401


# ────────────────────────────────────────────────
# 정상 케이스 (인증 포함)
# ────────────────────────────────────────────────

def test_publish_feed_success():
    with patch(
        "app.routes.publish.publish_service.publish_feed_image",
        new_callable=AsyncMock,
    ) as mock_publish:
        mock_publish.return_value = {"creation_id": "c1", "media_id": "m1"}

        response = client.post(
            "/publish/feed",
            json={"caption": "테스트 캡션", "image_filename": "post.jpg"},
            headers=VALID_AUTH,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["creation_id"] == "c1"
    assert response.json()["media_id"] == "m1"
    mock_publish.assert_awaited_once()


def test_publish_story_success():
    with patch(
        "app.routes.publish.publish_service.publish_story_image",
        new_callable=AsyncMock,
    ) as mock_publish:
        mock_publish.return_value = {"creation_id": "c2", "media_id": "m2"}

        response = client.post(
            "/publish/story",
            json={"image_filename": "post.jpg"},
            headers=VALID_AUTH,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["creation_id"] == "c2"
    assert response.json()["media_id"] == "m2"
    mock_publish.assert_awaited_once()


def test_publish_feed_failure_returns_generic_message():
    """에러 상세가 클라이언트에 노출되지 않아야 한다."""
    with patch(
        "app.routes.publish.publish_service.publish_feed_image",
        new_callable=AsyncMock,
    ) as mock_publish:
        mock_publish.side_effect = RuntimeError("internal db error details")

        response = client.post(
            "/publish/feed",
            json={"caption": "테스트 캡션", "image_filename": "post.jpg"},
            headers=VALID_AUTH,
        )

    assert response.status_code == 502
    # 내부 에러 메시지가 클라이언트에 노출되면 안 됨
    assert "internal db error details" not in response.json()["detail"]
    assert response.json()["detail"] == "Feed publish failed"


def test_publish_story_failure_returns_generic_message():
    """에러 상세가 클라이언트에 노출되지 않아야 한다."""
    with patch(
        "app.routes.publish.publish_service.publish_story_image",
        new_callable=AsyncMock,
    ) as mock_publish:
        mock_publish.side_effect = RuntimeError("secret internal error")

        response = client.post(
            "/publish/story",
            json={"image_filename": "post.jpg"},
            headers=VALID_AUTH,
        )

    assert response.status_code == 502
    assert "secret internal error" not in response.json()["detail"]
    assert response.json()["detail"] == "Story publish failed"
