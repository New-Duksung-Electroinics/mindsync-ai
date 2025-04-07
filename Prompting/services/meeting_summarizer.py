"""
Gemini API를 사용하여 회의록을 요약하는 클래스

회의 채팅 내역을 기반으로 각 안건별 주요 내용을 정리하고 결론을 도출.
안건별 주요 내용 정리는 각 발언자의 의견과 태도를 정리하는 형식으로 생성.
생성된 요약은 JSON 형식으로 반환.
"""
from .gemini_client import GeminiClient
from google.genai import types

INPUT_TOKEN_LIMIT = 1048576     # Limit of Gemini 2.0 flash 입력 토큰 제한 수
prompt_template = \
    """
Based on the following meeting logs, 
summarize the main content of each agenda item in Korean. 
Referring to the example given, summarize the main opinions and attitudes of each speaker related to the agenda, 
and write a conclusion for each agenda item.

Example:
[
    {{
    "step": 1,
    "sub_topic": "사내 커뮤니케이션 툴 도입",
    "summary": "오지훈: 현재 이메일 및 메신저 혼용으로 인해 업무 커뮤니케이션이 비효율적이라며, 일원화된 협업 툴 도입이 필요하다고 주장.\n김민정: 기존 사용 중인 메신저와의 차별점을 분석하여 실질적인 효율성이 있는지 검토해야 하며, 도입 시 직원 교육이 필수라고 강조.\n정다은: 사내 커뮤니케이션 툴 도입으로 인한 기대 효과(업무 흐름 개선, 문서 공유 간소화 등)를 언급하며, 시범 도입 후 피드백을 반영하는 방안을 제안."
    "conclusion": "내부 협업 강화를 위해 사내 커뮤니케이션 툴 도입 여부를 다음 회의에서 결정하기로 함.",
    }}
]

Text: {chat_history}
"""


class MeetingSummarizer:
    def __init__(self, temperature=1, top_p=0.95, top_k=40, max_output_tokens=8192):
        """
        MeetingSummarizer 클래스 생성자

        :param temperature: 모델의 온도 설정 (기본값: 1, 설정 가능 범위: 0~2)
        :param top_p: (단어의) 확률 기반 샘플링을 위한 top_p 값 (기본값: 0.95)
        :param top_k: (단어의) 확률 기반 샘플링을 위한 top_k 값 (기본값: 40)
        :param max_output_tokens: 최대 출력 토큰 수 (기본값: 8192, 최댓값)
        """
        self.client = GeminiClient()  # Gemini API 클라이언트 초기화
        self.template = prompt_template  # 회의록 생성을 위한 프롬프트 템플릿
        self.chat_history_token_alloc = INPUT_TOKEN_LIMIT - self.count_tokens(self.generate_prompt(''))  # 채팅 기록에 할당할 토큰 수 계산

        # 모델 config 값 설정
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens

        # 응답 형식 설정값
        self.response_mime_type = 'application/json'  # JSON 형식
        self.response_schema = {    # 세부 Schema 정의
            'items': {
                'type': 'OBJECT',
                'required': [
                    'step',
                    'sub_topic',
                    'summary',
                    'conclusion'
                ],
                'properties': {
                    'step': {'type': 'INTEGER'},  # 몇 번째 안건인지
                    'sub_topic': {'type': 'STRING'},  # 안건명
                    'summary': {'type': 'STRING'},  # 논의 내용 요약
                    'conclusion': {'type': 'STRING'},  # 논의 결론
                }
            },
            'type': 'ARRAY',  # 위 요소를 갖는 (안건별) 요약 object가 담긴 배열을 반환하도록 정의
        }

    def generate_prompt(self, chat_history: str):
        """
        프롬프트 템플릿에 채팅 내역 텍스트를 첨부하여 프름프트를 생성.

        :param chat_history: 채팅 내역 텍스트, str
        :return: 생성된 프롬프트, str
        """
        return self.template.format(chat_history=chat_history)

    def generate_prompts(self, chat_history: list):
        """
        여러 개의 채팅 내역 텍스트를 첨부하여 프름프트를 생성.
        토큰 수 제한으로 인한 분할 처리에 활용 가능.

        :param chat_history: 채팅 내역 텍스트 목록, str list
        :return: 생성된 프롬프트 목록, str list
        """
        prompts = []
        for c in chat_history:
            prompts.append(self.template.format(chat_history=c))
        return prompts

    def count_tokens(self, text):
        """
        텍스트의 토큰 수 계산

        :param text: 토큰 수를 계산할 텍스트, str
        :return: 텍스트의 토큰 수, int
        """
        token_cnt = self.client.count_tokens(text).total_tokens
        return token_cnt

    async def generate_summary(self, history_builder):
        """
        Gemini API를 사용하여 회의 요약을 생성.
        채팅 내역이 길어질 시 분할 처리가 필요할 수 있으므로 다수의 요청을 처리하여 응답을 병합할 수 있도록 구현.

        :param history_builder: 회의 채팅 내역 데이터 로더 객체, MeetingDataLodaer
        :return: 생성된 회의 요약 데이터, JSON 형식 (안건별 요약 dict가 담긴 list)
        """
        # 채팅 내역 텍스트를 목록으로 준비(토큰 수 제한 고려해 필요 시 분할 처리)
        chat_history = history_builder.process_chat_history_for_prompt(count_tokens_callback=self.count_tokens,
                                                                  token_alloc=self.chat_history_token_alloc)
        result = []
        prompts = self.generate_prompts(chat_history)   # 요청 프롬프트 목록을 생성
        config = types.GenerateContentConfig(   # Gemini API 상세 설정
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
            response_mime_type=self.response_mime_type,
            response_schema=self.response_schema
        )

        response = await self.client.process_prompts(prompts, config)   # 비동기 처리로 요청 프롬프트 목록을 한 꺼번에 처리
        for r in response:
            result += r.parsed  # 응답 결과 병합
        return result

    def parse_response_to_summary_data(self, response):
        summary_list = []
        for data in response:
            step = data.get("step", -1)
            sub_topic = data.get("sub_topic", '')
            conclusion = data.get("conclusion", '')
            highlights = data.get("summary", '').split('\n')
            indented_highlights = ''
            for h in highlights:
                indented_highlights += '\t' + h + '\n'

            title = f"{step}. {sub_topic}\n\n"
            highlight_text = "주요 발언:\n" + indented_highlights
            conclusion_text = "결론:\n" + '\t' + conclusion

            summary_content = highlight_text + conclusion_text
            agenda_summary = {
                "agendaId": step,
                "topic": sub_topic,
                "content": summary_content
            }

            summary_list.append(agenda_summary)

        return summary_list
