from .gemini_client import GeminiClient
from google.genai.types import GenerateContentConfig
from typing import cast
from .templates import AGENDA_PROMPT_KR, AGENDA_PROMPT_EN
from Prompting.exceptions import GeminiCallError, GeminiParseError, catch_and_raise


class AgendaGenerator:
    def __init__(self, temperature: float = 1, top_p: float = 0.95, top_k: int = 40, max_output_tokens: int = 2000):
        """
        Gemini API로 주제에 적절한 회의 안건 제안을 생성
         - 요청을 기반으로 예상되는 회의 규모에 따라 3~10개의 안건 아이템을 생성

        Args:
            temperature: 모델의 온도 설정 (기본값: 1, 설정 가능 범위: 0~2)
            top_p: (단어의) 확률 기반 샘플링을 위한 top_p 값 (기본값: 0.95)
            top_k: (단어의) 확률 기반 샘플링을 위한 top_k 값 (기본값: 40)
            max_output_tokens: 최대 출력 토큰 수 (기본값: 2000)
        """
        self.client = GeminiClient()  # Gemini API 클라이언트 초기화
        self.template = AGENDA_PROMPT_KR  # 프롬프트 템플릿

        # 모델 config 값 설정
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens

        # 응답 형식 설정값
        self.response_mime_type = 'application/json'
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


    @catch_and_raise("Gemini 안건 생성", GeminiCallError)
    async def generate_agenda(self, topic_request: str) -> list[dict]:
        """
        Gemini API를 호출해 회의 안건 생성을 요청하고 응답을 반환

        Args:
            topic_request: 회의 안건 제안에 대한 요청 사항

        Returns:
            Gemini 응답 파싱 결과 (회의 안건 정보가 담긴 dict 리스트)
        """
        prompt = self._build_prompt(topic_request)
        config = GenerateContentConfig(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
            response_mime_type=self.response_mime_type,
            response_schema=self.response_schema
        )
        response = self.client.generate_content(prompt, config)
        agenda_list = cast(list[dict], response.parsed)  # json 형식으로 파싱(IDE 타입 hint 겁사 때문에 cast 적용)

        return agenda_list


    @catch_and_raise("Gemini 안건 응답 파싱", GeminiParseError)
    def parse_response_to_agenda_data(self, response: list[dict]) -> dict:
        """
        Gemini의 응답을 MongoDB 저장 형식에 맞게 변환

        Args:
            response: Gemini 응답으로부터 파싱된 안건 list[dict]

        Returns:
            안건 ID(str) - 안건 주제(str) 매핑 딕셔너리
        """
        agendas = {}
        for data in response:
            step = str(data.get("step", -1))
            topic = data.get("topic", '')
            agendas[step] = topic

        return agendas


    def _build_prompt(self, topic_request: str) -> str:
        """
        프롬프트 템플릿에 필요한 요소를 삽입하여 최종 프롬프트를 생성

        Args:
            topic_request: 회의 안건 제안에 대한 요청 사항

        Returns:
            안건 생성 요청 프롬프트
        """
        prompt = self.template.format(topic_request=topic_request)
        return prompt
