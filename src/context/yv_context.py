from datetime import datetime, timedelta
import requests
from context import env_context
from fastapi import HTTPException

def _upstream_error(message: str = "YouVersion request failed") -> HTTPException:
    return HTTPException(
        status_code=502,
        detail={"code": "UPSTREAM_ERROR", "message": message}
    )

def yv_get_votd_reference(day: int) -> str:
    try:
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
    except requests.exceptions.RequestException:
        raise _upstream_error()
    except (KeyError, TypeError, ValueError):
        raise _upstream_error("YouVersion returned an unexpected response")

def yv_get_passages(version: int, passage: str) -> dict:
    try:
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
        data = response.json()
        return data
    except requests.exceptions.RequestException:
        raise _upstream_error()
    except (KeyError, TypeError, ValueError):
        raise _upstream_error("YouVersion returned an unexpected response")

def _yv_get_eligible_versions() -> list[int]:
    try:
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
    except requests.exceptions.RequestException:
        raise _upstream_error()
    except (KeyError, TypeError, ValueError):
        raise _upstream_error("YouVersion returned an unexpected response")

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

_VOTD_CACHE = {}
def yv_get_votd(day: int, version: int) -> dict:
    global _VOTD_CACHE
    cache_key = (day, version)
    if cache_key in _VOTD_CACHE:
        return _VOTD_CACHE[cache_key]
    passage = yv_get_votd_reference(day)
    passage_data = yv_get_passages(version, passage)
    try:
        result = {
            "day": day,
            "reference": passage_data["reference"],
            "text": passage_data["content"],
            "version_id": version,
        }
    except (KeyError, TypeError):
        raise _upstream_error("YouVersion returned an unexpected response")
    _VOTD_CACHE[cache_key] = result
    return result