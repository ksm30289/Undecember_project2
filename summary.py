from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)


def summarize_with_ai(target_date, discord_items, negative_items, floor_items):
    prompt = f"""
너는 게임 운영 담당자를 위한 동향 요약 AI야.
대상 게임은 언디셈버야.

아래 수집 데이터를 바탕으로 {target_date} 일별 동향을 요약해줘.

출력 형식은 반드시 아래 형식을 지켜줘.

[디스코드 요약]
- 핵심만 3~5줄

[부정 동향 요약]
- 핵심만 3~5줄

[플로어 동향 요약]
- 핵심만 3~5줄

[종합 요약]
- 전체 분위기와 주요 이슈를 3~5줄

[주요 이슈 TOP 5]
1.
2.
3.
4.
5.

[운영 대응 추천]
- 운영자가 확인하거나 대응하면 좋은 항목을 bullet로 정리

주의사항:
- 과장하지 말 것
- 데이터에 없는 내용을 추측하지 말 것
- 같은 이슈는 묶어서 요약할 것
- 게임 운영 리포트 문체로 작성할 것

====================
[디스코드 데이터]
{discord_items if discord_items else "데이터 없음"}

====================
[부정 동향 데이터]
{negative_items if negative_items else "데이터 없음"}

====================
[플로어 데이터]
{floor_items if floor_items else "데이터 없음"}
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "너는 게임 서비스 운영 리포트를 작성하는 전문 어시스턴트야.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def split_summary(text):
    sections = {
        "디스코드 요약": "",
        "부정 동향 요약": "",
        "플로어 동향 요약": "",
        "종합 요약": "",
        "주요 이슈 TOP 5": "",
        "운영 대응 추천": "",
    }

    current = None
    lines = []

    for line in text.splitlines():
        clean = line.strip()

        matched = None
        for key in sections.keys():
            if clean.startswith(f"[{key}]"):
                matched = key
                break

        if matched:
            if current:
                sections[current] = "\n".join(lines).strip()
            current = matched
            lines = []
        else:
            if current:
                lines.append(line)

    if current:
        sections[current] = "\n".join(lines).strip()

    return sections
