import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

_BASE_URL = os.getenv("YOUVERSION_BASE_URL")
_API_KEY = os.getenv("YOUVERSION_API_KEY")

def get_base_url():
    return _BASE_URL

def get_api_key():
    return _API_KEY