SUMMARY_PROMPT_KR = \
    """
Text로 주어진 회의 내역을 바탕으로 각 안건별 주요 내용을 한국어로 요약해줘. 
Example처럼 안건과 관련된 각 발언자의 주요 의견과 태도를 요약하고, 안건에 대한 결론을 작성해줘. 
안건 및 회의 주제와 관련된 중요한 발언 위주로만 참여자별 핵심 의견을 정리해주면 돼.

Example:
[
    {{
    "step": 1,
    "sub_topic": "사내 커뮤니케이션 툴 도입",
    "key_statements": "오지훈: 현재 이메일 및 메신저 혼용으로 인해 업무 커뮤니케이션이 비효율적이라며, 일원화된 협업 툴 도입이 필요하다고 주장.\n김민정: 기존 사용 중인 메신저와의 차별점을 분석하여 실질적인 효율성이 있는지 검토해야 하며, 도입 시 직원 교육이 필수라고 강조.\n정다은: 사내 커뮤니케이션 툴 도입으로 인한 기대 효과(업무 흐름 개선, 문서 공유 간소화 등)를 언급하며, 시범 도입 후 피드백을 반영하는 방안을 제안."
    "conclusion": "내부 협업 강화를 위해 사내 커뮤니케이션 툴 도입 여부를 다음 회의에서 결정하기로 함.",
    }}
]

Text: {chat_history}
"""


SUMMARY_PROMPT_EN = \
    """
Summarize the main contents of each agenda item in Korean based on the meeting transcript given in 'Text'. 
Summarize the main opinions and attitudes of each speaker related to the agenda, and write a conclusion to the agenda, as shown in 'Example'. 
You only need to organize key statements for each participant by focusing on important statements related to the agenda and meeting topic.

Example:
[
    {{
    "step": 1,
    "sub_topic": "사내 커뮤니케이션 툴 도입",
    "key_statements": "오지훈: 현재 이메일 및 메신저 혼용으로 인해 업무 커뮤니케이션이 비효율적이라며, 일원화된 협업 툴 도입이 필요하다고 주장.\n김민정: 기존 사용 중인 메신저와의 차별점을 분석하여 실질적인 효율성이 있는지 검토해야 하며, 도입 시 직원 교육이 필수라고 강조.\n정다은: 사내 커뮤니케이션 툴 도입으로 인한 기대 효과(업무 흐름 개선, 문서 공유 간소화 등)를 언급하며, 시범 도입 후 피드백을 반영하는 방안을 제안."
    "conclusion": "내부 협업 강화를 위해 사내 커뮤니케이션 툴 도입 여부를 다음 회의에서 결정하기로 함.",
    }}
]

Text: {chat_history}
"""

