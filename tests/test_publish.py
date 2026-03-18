from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_publish_feed_success():
    with patch(
        "app.routes.publish.publish_service.publish_feed_image",
        new_callable=AsyncMock,
    ) as mock_publish:
        mock_publish.return_value = {"creation_id": "c1", "media_id": "m1"}

        response = client.post(
            "/publish/feed",
            json={"caption": "테스트 캡션", "image_filename": "post.jpg"},
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
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["creation_id"] == "c2"
    assert response.json()["media_id"] == "m2"
    mock_publish.assert_awaited_once()


def test_publish_feed_failure():
    with patch(
        "app.routes.publish.publish_service.publish_feed_image",
        new_callable=AsyncMock,
    ) as mock_publish:
        mock_publish.side_effect = RuntimeError("failed")

        response = client.post(
            "/publish/feed",
            json={"caption": "테스트 캡션", "image_filename": "post.jpg"},
        )

    assert response.status_code == 502
    assert response.json()["detail"].startswith("Feed publish failed:")
