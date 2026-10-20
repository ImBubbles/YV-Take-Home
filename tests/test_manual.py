import pytest
import requests
from fastapi.testclient import TestClient
from unittest.mock import patch

import main
from context import yv_context

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
