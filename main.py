from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import (
    TARGET_DATE,
    TIMEZONE,
    DISCORD_SHEET,
    COMMUNITY_SHEET,
)
from sheets import get_records, append_summary
from summary import summarize_with_ai


# ✅ 오늘
def today_str():
    return datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d")


# ✅ 어제 (🔥 핵심)
def yesterday_str():
    return (datetime.now(ZoneInfo(TIMEZONE)) - timedelta(days=1)).strftime("%Y-%m-%d")


# ✅ 날짜 정규화 (강화 버전)
def normalize_date(value):
    if value is None:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    text = text.replace(".", "-").replace("/", "-")
    text = text.replace("년", "-").replace("월", "-").replace("일", "")
    text = text.replace("오전", "").replace("오후", "")
    text = " ".join(text.split())

    import re

    match = re.search(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})", text)
    if match:
        y, m, d = match.groups()
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

    match = re.search(r"(\d{1,2})\D+(\d{1,2})", text)
    if match:
        y = datetime.now(ZoneInfo(TIMEZONE)).year
        m, d = match.groups()
        return f"{y:04d}-{int(m):02d}-{int(d):02d}"

    return text[:10]


# ✅ 디스코드 수집
def collect_discord(records, target_date):
    print("디스코드 총 데이터:", len(records))
    print("target_date:", target_date)

    items = []

    for i, row in enumerate(records):
        raw_date = row.get("수집 시간")
        date = normalize_date(raw_date)

        # 🔥 로그 제한
        if i < 10:
            print("원본:", raw_date, "→ 변환:", date)

        if date != target_date:
            continue

        message = str(row.get("번역 (구글)", "")).strip()
        category = str(row.get("분류", "")).strip()
        keyword = str(row.get("매칭 키워드", "")).strip()

        if not message:
            continue

        items.append({
            "분류": category,
            "키워드": keyword,
            "내용": message,
        })

    print("디스코드 필터 후 데이터:", len(items))
    return items


def collect_community(records, target_date):

    items = []

    for row in records:

        date = normalize_date(
            row.get("게시일")
        )

        if date != target_date:
            continue

        summary = str(
            row.get("AI요약", "")
        ).strip()

        if not summary:
            continue

        items.append({
            "출처": str(row.get("출처", "")).strip(),
            "감성": str(row.get("감성", "")).strip(),
            "주제": str(row.get("주제", "")).strip(),
            "대표이슈": str(row.get("대표 이슈", "")).strip(),
            "영향도": str(row.get("영향도", "")).strip(),
            "AI요약": summary,
            "제목": str(row.get("제목", "")).strip(),
        })

    return items


# ✅ 데이터 제한 (속도 핵심)
def limit_items(items, limit=50):
    return items[:limit]


def main():
    # 🔥 핵심: 어제 기준
    target_date = TARGET_DATE or yesterday_str()

    print(f"요약 대상 날짜: {target_date}")

    discord_records = get_records(DISCORD_SHEET)
    community_records = get_records(
        COMMUNITY_SHEET
    )

    community_items = limit_items(
        collect_community(
            community_records,
            target_date
        )
    )

    discord_items = limit_items(collect_discord(discord_records, target_date))

    print("=== 데이터 수집 완료 ===")
    print("디스코드:", len(discord_items))
    print(
        "커뮤니티:",
        len(community_items)
    )

    if not discord_items and not community_items:
        print("요약할 데이터가 없습니다.")
        return

    print("=== AI 요약 시작 ===")

    result = summarize_with_ai(
        target_date=target_date,
        discord_items=discord_items,
        community_items=community_items,
    )

    print("=== AI 요약 완료 ===")

    created_at = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")

    append_summary([
        target_date,
        result,
        created_at,
    ])

    print("일별 동향 요약 저장 완료")


if __name__ == "__main__":
    main()
