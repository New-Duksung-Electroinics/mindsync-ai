"""
Gemini API를 사용하여 회의 주제 요청에 따라 적절한 회의 안건을 JSON 형식으로 생성하는 클래스

주어진 회의 주제 요청을 기반으로 3~10개의 안건 아이템을 포함하는 회의 안건을 생성
"""
from .gemini_client import GeminiClient
from google.genai import types

prompt_template_kr = \
    """
다음 요청에 대해 적절한 회의 안건을 한글 JSON 형식으로 나열해줘. 안건 번호를 의미하는 step은 1부터 시작하는 게 규칙이야.
예상되는 회의 규모에 따라 최소 3개 이상 최대 10개 이하의 안건을 만들어주되, 안건명을 무엇을 논의하는 게 좋을 지 누구나 잘 알 수 있도록 구체적으로 작성해줘.:
Text: {topic_request}
"""

prompt_template = \
    """
List the appropriate meeting agendas in Korean JSON format for the following request. 
The 'step', which is the agenda number, should start with 1.
Provide at least 3 agenda items and no more than 10, depending on the expected size of the meeting,
but please make each 'topic' specific so that everyone knows what to expect:
Text: {topic_request}
"""


class AgendaGenerator:
    def __init__(self, temperature=1, top_p=0.95, top_k=40, max_output_tokens=2000):
        """
        AgendaGenerator 클래스 생성자

        :param temperature: 모델의 온도 설정 (기본값: 1, 설정 가능 범위: 0~2)
        :param top_p: (단어의) 확률 기반 샘플링을 위한 top_p 값 (기본값: 0.95)
        :param top_k: (단어의) 확률 기반 샘플링을 위한 top_k 값 (기본값: 40)
        :param max_output_tokens: 최대 출력 토큰 수 (기본값: 2000)
        """
        self.client = GeminiClient()  # Gemini API 클라이언트 초기화
        self.template = prompt_template  # 회의록 생성을 위한 프롬프트 템플릿

        # 모델 config 값 설정
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens

        # 응답 형식 설정값
        self.response_mime_type = 'application/json'  # JSON 형식
        self.response_schema = {  # 세부 Schema 정의
            'items': {
                'type': 'OBJECT',
                'required': [
                    'step',
                    'topic'
                ],
                'properties': {
                    'step': {'type': 'INTEGER'},  # 몇 번째 안건인지
                    'topic': {'type': 'STRING'},  # 안건명
                }
            },
            'type': 'ARRAY',  # 위 요소를 갖는 안건 object가 담긴 배열을 반환하도록 정의
        }

    def _generate_prompt(self, topic_request):
        """
        프롬프트 템플릿에 회의 주제 요청을 삽입하여 최종 프롬프트를 생성

        :param topic_request: 회의 주제 요청, str
        :return: 생성된 프롬프트, str
        """
        prompt = self.template.format(topic_request=topic_request)
        return prompt

    async def generate_agenda(self, room_id, topic_request):
        """
        Gemini API를 사용하여 회의 안건을 생성하고 DB에 저장

        :param room_id: 회의 방 ID, str
        :param topic_request: 회의 주제 요청, str
        :return: 생성된 회의 안건 리스트, JSON 형식
        """
        prompt = self._generate_prompt(topic_request)
        config = types.GenerateContentConfig(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
            response_mime_type=self.response_mime_type,
            response_schema=self.response_schema
        )
        response = self.client.generate_content(prompt, config)
        agenda_list = response.parsed  # json 형식으로 파싱

        return agenda_list

    def parse_response_to_agenda_data(self, response):
        agendas = {}
        for data in response:
            step = str(data.get("step", -1))
            topic = data.get("topic", '')
            agendas[step] = topic

        return agendas
