import pytest
import requests
from fastapi.testclient import TestClient
from unittest.mock import patch

import main
from context import yv_context
from context import env_context

client = TestClient(main.app)

def test_votd_happy_path():
    expected = {
        "day": 195,
        "reference": "Revelation 3:20",
        "text": "Behold, I stand at the door and knock. If anyone hears my voice and opens the door, then I will come in to him and will dine with him, and he with me.",
        "version_id": 206
    }
    with (
        patch.object( # /v1/verse_of_the_days/{day}
        yv_context,
        "yv_get_votd_reference",
        return_value="REV.3.20" # func returns data["passage_id"]
        ),
        patch.object( # /v1/bibles/{version}/passages/{passage}
            yv_context,
            "yv_get_passages",
            return_value={ # func returns data (or response.json())
                "id": "REV.3.20",
                "content": "Behold, I stand at the door and knock. If anyone hears my voice and opens the door, then I will come in to him and will dine with him, and he with me.",
                "reference": "Revelation 3:20"
            }
        ),
        patch.object( # /v1/bibles
            yv_context,
            "yv_is_eligible_version",
            return_value=True # func returns if version is valid by checking against YV API
        )
    ):
        response = client.get("/votd?day=195&version=206")
        assert response.status_code == 200
        assert response.json() == expected

def test_votd_invalid_day():
    response = client.get("/votd?day=0")
    assert response.status_code == 400
    assert response.json() == {
        'error': {
            'code': 'INVALID_DAY',
            'message': 'day must be an integer between 1 and 366'
        }
    }

def test_votd_upstream_failure_force():
    yv_context._VOTD_CACHE.clear()
    with patch.object(
        yv_context,
        "yv_get_votd_reference",
        side_effect=yv_context._upstream_error(
            "YouVersion returned an unexpected response"
        )
    ):
        response = client.get("/votd?day=195&version=206")
        assert response.status_code == 502
        assert response.json() == {
            "error": {
                "code": "UPSTREAM_ERROR",
                "message": "YouVersion returned an unexpected response"
            }
        }

def test_votd_upstream_failure_invalid_url():
    yv_context._VOTD_CACHE.clear()
    with patch.object(
        env_context,
        "get_base_url",
        return_value="https://iaminvalid.com/"
    ):
        response = client.get("/votd?day=195&version=206")
        assert response.status_code == 502
        assert response.json() == {
            'error': {
                'code': 'UPSTREAM_ERROR',
                'message': 'YouVersion request failed'
            }
        }

def test_votd_upstream_failure_connection():
    yv_context._VOTD_CACHE.clear()
    with patch.object(
        yv_context.requests,
        "get",
        side_effect=requests.exceptions.ConnectionError()
    ):
        response = client.get("/votd?day=195&version=206")
        assert response.status_code == 502
        assert response.json() == {
            'error': {
                'code': 'UPSTREAM_ERROR',
                'message': 'YouVersion request failed'
            }
        }
