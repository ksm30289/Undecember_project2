from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)


def summarize_with_ai(
    target_date,
    discord_items,
    community_items
):
    prompt = f"""
너는 게임 운영 리포트를 작성하는 담당자야.
보고 대상은 개발팀 및 사업팀이야.

목표:
- 실제 의사결정에 도움이 되는 팀 공유용 운영 리포트 작성
- 반복 이슈는 묶어서 정리
- 데이터에 없는 내용은 추측하지 않기
- 감정 표현은 줄이고 객관적으로 작성

반드시 아래 형식을 지켜서 작성해줘.

📊 언디셈버 운영 리포트 ({target_date})

[1. 전체 요약]
- 

[2. 주요 이슈 TOP 5]
1.
2.
3.
4.
5.

[3. 채널별 분석]

(1) 디스코드
- 

(2) 부정 동향
- 

(3) 플로어
- 

[4. 유저 반응 분석]
- 

[5. 운영 대응 가이드]
- 지금 당장 확인할 것:
- 추적할 것:
- 공유가 필요한 것:

[6. 리스크 알림]
- 

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
    return {
        "디스코드 요약": "",
        "부정 동향 요약": "",
        "플로어 동향 요약": "",
        "종합 요약": text,
        "주요 이슈 TOP 5": "",
        "운영 대응 추천": "",
    }
