from datetime import datetime
from zoneinfo import ZoneInfo

from config import (
    TARGET_DATE,
    TIMEZONE,
    DISCORD_SHEET,
    NEGATIVE_SHEET,
    FLOOR_SHEET,
)
from sheets import get_records, append_summary
from summary import summarize_with_ai, split_summary


def today_str():
    return datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d")


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

    # 2026-05-06 / 2026-5-6 / 2026. 05. 06 대응
    match = re.search(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})", text)
    if match:
        y, m, d = match.groups()
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

    # 05-06 처럼 연도 없는 경우는 올해 기준
    match = re.search(r"(\d{1,2})\D+(\d{1,2})", text)
    if match:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from config import TIMEZONE

        m, d = match.groups()
        y = datetime.now(ZoneInfo(TIMEZONE)).year
        return f"{y:04d}-{int(m):02d}-{int(d):02d}"

    return text[:10]


def collect_discord(records, target_date):
    print("디스코드 총 데이터:", len(records))
    print("디스코드 수집 시간 샘플:", records[0].get("수집 시간") if records else "없음")
    print("target_date:", target_date)

    items = []

    for i, row in enumerate(records):
        raw_date = row.get("수집 시간")
        date = normalize_date(raw_date)

        # ✅ 로그 폭주 방지: 앞 10개만 출력
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


def collect_negative(records, target_date):
    items = []

    for row in records:
        date = normalize_date(row.get("수집일자"))
        if date != target_date:
            continue

        title = str(row.get("제목", "")).strip()
        body = str(row.get("본문", "")).strip()
        keyword = str(row.get("키워드", "")).strip()
        link = str(row.get("링크", "")).strip()

        if not title and not body:
            continue

        items.append({
            "키워드": keyword,
            "제목": title,
            "본문": body,
            "링크": link,
        })

    return items


def collect_floor(records, target_date):
    items = []

    for row in records:
        date = normalize_date(row.get("수집일자"))
        if date != target_date:
            continue

        title = str(row.get("제목", "")).strip()
        category = str(row.get("분류", "")).strip()
        keyword = str(row.get("매칭 키워드", "")).strip()
        link = str(row.get("링크", "")).strip()

        if not title:
            continue

        items.append({
            "분류": category,
            "키워드": keyword,
            "제목": title,
            "링크": link,
        })

    return items


def limit_items(items, limit=80):
    return items[:limit]


def main():
    target_date = TARGET_DATE or today_str()

    print(f"요약 대상 날짜: {target_date}")

    discord_records = get_records(DISCORD_SHEET)
    negative_records = get_records(NEGATIVE_SHEET)
    floor_records = get_records(FLOOR_SHEET)

    discord_items = limit_items(collect_discord(discord_records, target_date))
    negative_items = limit_items(collect_negative(negative_records, target_date))
    floor_items = limit_items(collect_floor(floor_records, target_date))

    print(f"디스코드 데이터: {len(discord_items)}건")
    print(f"부정 동향 데이터: {len(negative_items)}건")
    print(f"플로어 데이터: {len(floor_items)}건")

    if not discord_items and not negative_items and not floor_items:
        print("요약할 데이터가 없습니다.")
        return

    result = summarize_with_ai(
        target_date=target_date,
        discord_items=discord_items,
        negative_items=negative_items,
        floor_items=floor_items,
    )

    sections = split_summary(result)

    created_at = datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")

    append_summary([
        target_date,
        sections.get("디스코드 요약", ""),
        sections.get("부정 동향 요약", ""),
        sections.get("플로어 동향 요약", ""),
        sections.get("종합 요약", ""),
        sections.get("주요 이슈 TOP 5", ""),
        sections.get("운영 대응 추천", ""),
        created_at,
    ])

    print("일별 동향 요약 저장 완료")


if __name__ == "__main__":
    main()
