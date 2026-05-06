import os
import json


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise RuntimeError(f"환경변수 누락: {name}")
    return value.strip()


SPREADSHEET_ID = required_env("SPREADSHEET_ID")
OPENAI_API_KEY = required_env("OPENAI_API_KEY")

GOOGLE_SERVICE_ACCOUNT_JSON = required_env("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_CREDENTIALS = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)

DISCORD_SHEET = os.getenv("DISCORD_SHEET", "디스코드 동향")
NEGATIVE_SHEET = os.getenv("NEGATIVE_SHEET", "언디셈버_KR_부정 동향")
FLOOR_SHEET = os.getenv("FLOOR_SHEET", "언디셈버_KR_플로어 동향")
SUMMARY_SHEET = os.getenv("SUMMARY_SHEET", "일별 동향 요약")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TARGET_DATE = os.getenv("TARGET_DATE", "").strip()
TIMEZONE = os.getenv("TIMEZONE", "Asia/Seoul")
