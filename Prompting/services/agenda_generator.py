"""
Gemini API를 사용하여 회의 주제 요청에 따라 적절한 회의 안건을 JSON 형식으로 생성하는 클래스

주어진 회의 주제 요청을 기반으로 3~10개의 안건 아이템을 포함하는 회의 안건을 생성하며,
각 안건은 단계(step), 주제(topic), 설명(description)을 포함함.

생성된 안건은 JSON 형식으로 반환.
"""
from .gemini_client import GeminiClient
from google.genai import types

prompt_template = \
    """
List an appropriate meeting agenda in Korean JSON format for the following requests. 
Provide a minimum of 3 agenda items and no more than 10, depending on the expected size of the meeting:
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
                    'topic',
                    'description'
                ],
                'properties': {
                    'step': {'type': 'INTEGER'},  # 몇 번째 안건인지
                    'topic': {'type': 'STRING'},  # 안건명
                    'description': {'type': 'STRING'},  # 안건에 대한 설명
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

    async def generate_agenda(self, topic_request):
        """
        Gemini API를 사용하여 회의 안건을 생성

        :param topic_request: 회의 주제 요청, str
        :return: 생성된 회의 안건, JSON 형식 (안건 dict가 담긴 list)
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
        response = await self.client.generate_content_async(prompt, config)
        return response.parsed  # json 형식으로 파싱하여 반환
