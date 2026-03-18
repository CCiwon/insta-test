import hashlib
import hmac
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _make_signature(body: bytes, secret: str = "test_app_secret") -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


# ────────────────────────────────────────────────
# GET /webhook — 허브 검증
# ────────────────────────────────────────────────

def test_verify_webhook_success():
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test_verify_token",
            "hub.challenge": "challenge_abc",
        },
    )
    assert response.status_code == 200
    assert response.text == "challenge_abc"


def test_verify_webhook_wrong_token():
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "challenge_abc",
        },
    )
    assert response.status_code == 403


def test_verify_webhook_wrong_mode():
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "unsubscribe",
            "hub.verify_token": "test_verify_token",
            "hub.challenge": "challenge_abc",
        },
    )
    assert response.status_code == 400


# ────────────────────────────────────────────────
# POST /webhook — 댓글 이벤트 수신
# ────────────────────────────────────────────────

SAMPLE_COMMENT_PAYLOAD = {
    "object": "instagram",
    "entry": [
        {
            "id": "entry_001",
            "time": 1700000000,
            "changes": [
                {
                    "field": "comments",
                    "value": {
                        "id": "comment_001",
                        "text": "너무 예쁘다! 어디 제품이에요?",
                        "from": {"id": "user_001", "username": "follower_kim"},
                        "media": {"id": "media_001"},
                        "timestamp": "2024-01-01T00:00:00Z",
                    },
                }
            ],
        }
    ],
}


def test_receive_webhook_success():
    body = json.dumps(SAMPLE_COMMENT_PAYLOAD).encode()
    signature = _make_signature(body)

    with patch(
        "app.routes.webhook.handle_comment",
        new_callable=AsyncMock,
    ) as mock_handle:
        response = client.post(
            "/webhook",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": signature,
            },
        )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_handle.assert_awaited_once()


def test_receive_webhook_invalid_signature():
    body = json.dumps(SAMPLE_COMMENT_PAYLOAD).encode()

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalidsignature",
        },
    )
    assert response.status_code == 403


def test_receive_webhook_non_instagram_object():
    payload = {**SAMPLE_COMMENT_PAYLOAD, "object": "page"}
    body = json.dumps(payload).encode()
    signature = _make_signature(body)

    response = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}
