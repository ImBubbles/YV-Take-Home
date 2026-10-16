import pytest
import requests
from fastapi.testclient import TestClient
from unittest.mock import patch

import main
from context import yv_context

client = TestClient(main.app)


def test_votd_happy_path():
    expected = {
        "day": 100,
        "reference": "John 3:16",
        "text": "For God so loved the world...",
        "version_id": 12,
    }
    with patch.object(main.yv_context, "yv_is_eligible_version", return_value=True), \
         patch.object(yv_context, "yv_get_votd_reference", return_value="JHN.3.16"), \
         patch.object(yv_context, "yv_get_passages", return_value={
             "id": "JHN.3.16",
             "reference": "John 3:16",
             "content": "For God so loved the world...",
         }):
        response = client.get("/votd?day=100&version=12")

    assert response.status_code == 200
    assert response.json() == expected


def test_votd_invalid_day():
    response = client.get("/votd?day=0&version=12")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "INVALID_DAY",
            "message": "day must be an integer between 1 and 366",
        }
    }


def test_votd_non_integer_day():
    response = client.get("/votd?day=abc&version=12")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "INVALID_DAY",
            "message": "day must be an integer between 1 and 366",
        }
    }


def test_yv_upstream_failure():
    with patch.object(main.yv_context, "yv_is_eligible_version", return_value=True), \
         patch.object(yv_context.requests, "get") as mock_get:
        mock_response = requests.Response()
        mock_response.status_code = 500
        mock_response.url = "https://example.com/v1/bibles"
        mock_get.return_value = mock_response

        response = client.get("/votd?day=195&version=12")

    assert response.status_code == 502
    assert response.json() == {
        "error": {"code": "UPSTREAM_ERROR", "message": "YouVersion request failed"}
    }


def test_votd_cache_is_keyed_by_day_and_version(monkeypatch):
    yv_context._VOTD_CACHE.clear()
    passage_calls = []
    monkeypatch.setattr(yv_context, "yv_get_votd_reference", lambda day: "JHN.3.16")

    def get_passage(version, passage):
        passage_calls.append((version, passage))
        return {"reference": "John 3:16", "content": f"Text for {version}"}

    monkeypatch.setattr(yv_context, "yv_get_passages", get_passage)
    try:
        first = yv_context.yv_get_votd(100, 12)
        repeated = yv_context.yv_get_votd(100, 12)
        other_version = yv_context.yv_get_votd(100, 206)
    finally:
        yv_context._VOTD_CACHE.clear()

    assert first == repeated
    assert first["version_id"] == 12
    assert other_version["version_id"] == 206
    assert passage_calls == [(12, "JHN.3.16"), (206, "JHN.3.16")]


def test_english_versions_returns_only_english_records(monkeypatch):
    monkeypatch.setattr(yv_context, "_get_valid_versions", lambda: {
        12: {
            "id": 12,
            "language_tag": "en",
            "abbreviation": "ASV",
            "title": "American Standard Version",
        },
        206: {
            "id": 206,
            "language_tag": "en-US",
            "abbreviation": "WEB",
            "title": "World English Bible",
        },
        999: {
            "id": 999,
            "language_tag": "fr",
            "abbreviation": "LSG",
            "title": "Louis Segond",
        },
    })

    assert yv_context.yv_get_english_versions() == [
        {"id": 12, "abbreviation": "ASV", "title": "American Standard Version"},
        {"id": 206, "abbreviation": "WEB", "title": "World English Bible"},
    ]