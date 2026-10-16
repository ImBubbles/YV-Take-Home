from datetime import datetime, timedelta
import requests
from context import env_context

def yv_get_votd(day: int) -> int:
    response = requests.get(
        f"{env_context.get_base_url()}/v1/verse_of_the_days/{day}",
        headers={
            "x-yvp-app-key": env_context.get_api_key()
        },
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    return data["passage_id"]

def yv_get_passages(version: int, passage: int) -> dict:
    response = requests.get(
        f"{env_context.get_base_url()}/v1/bibles/{version}/passages/{passage}",
        headers={
            "x-yvp-app-key": env_context.get_api_key()
        },
        params={
            "format": 'text'
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json()

def _yv_get_eligible_versions() -> list[int]:
    response = requests.get(
        f"{env_context.get_base_url()}/v1/bibles",
        headers={
            "x-yvp-app-key": env_context.get_api_key()
        },
        params={
            "language_ranges[]": 'en*'
        },
        timeout=10
    )
    response.raise_for_status()
    data = response.json()["data"]
    result = []
    for bible in data:
        result.append(bible["id"])
    return result

_VALID_VERSIONS = []
_LAST_UPDATED = None

def _update_valid_versions():
    global _VALID_VERSIONS, _LAST_UPDATED
    _VALID_VERSIONS = _yv_get_eligible_versions()
    _LAST_UPDATED = datetime.now()

def yv_is_eligible_version(version: int) -> bool:
    global _VALID_VERSIONS, _LAST_UPDATED
    if _LAST_UPDATED is None or datetime.now() - _LAST_UPDATED > timedelta(hours=1):
        _update_valid_versions()
    return version in _VALID_VERSIONS