import itertools

from .gemini_client import GeminiClient
from google.genai.types import GenerateContentConfig
from .templates import SUMMARY_PROMPT_EN
from Prompting.usecases.meeting_context import MeetingContext
from Prompting.exceptions.decorators import catch_and_raise
from Prompting.exceptions.errors import GeminiCallError, GeminiParseError, MongoAccessError, PromptBuildError
from .context_builders import MeetingHistoryBuilder
from typing import cast
from Prompting.common import AgendaStatus


class MeetingSummarizer:
    def __init__(self, temperature: float = 1, top_p: float = 0.95, top_k: int = 40,
                 max_output_tokens: int = GeminiClient.OUTPUT_TOKEN_LIMIT):
        """
        Gemini API를 사용하여 회의록을 요약하는 클래스

        Note:
            - 회의 채팅 내역을 기반으로 각 안건별 주요 내용을 정리하고 결론을 도출
            - 안건별 주요 내용 정리는 각 발언자의 의견과 태도를 정리하는 형식으로 생성

        Args:
            temperature: 모델의 온도 설정 (기본값: 1, 설정 가능 범위: 0~2)
            top_p: (단어의) 확률 기반 샘플링을 위한 top_p 값 (기본값: 0.95)
            top_k: (단어의) 확률 기반 샘플링을 위한 top_k 값 (기본값: 40)
            max_output_tokens: 최대 출력 토큰 수 (기본값: 8192 -> *Gemini 출력 토큰 최댓값)
        """
        self.client = GeminiClient()  # Gemini API 클라이언트 초기화
        self.template = SUMMARY_PROMPT_EN  # 회의록 생성을 위한 프롬프트 템플릿

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
                    'key_statements',
                    'conclusion'
                ],
                'properties': {
                    'step': {'type': 'INTEGER'},  # 몇 번째 안건인지
                    'sub_topic': {'type': 'STRING'},  # 안건명
                    'key_statements': {'type': 'STRING'},  # 논의 내용 요약
                    'conclusion': {'type': 'STRING'},  # 논의 결론
                }
            },
            'type': 'ARRAY',  # 위 요소를 갖는 (안건별) 요약 object가 담긴 배열을 반환하도록 정의
        }

    @catch_and_raise("Gemini 요약 생성", GeminiCallError)
    async def generate_summary(self, meeting_context: MeetingContext) -> list[dict]:
        """
        Gemini API로 회의 요약을 생성.
        채팅 내역이 길어질 시 분할 처리가 필요할 수 있으므로 다수의 요청을 처리하여 응답을 병합할 수 있도록 구현.

        Args:
            meeting_context: 회의 맥락이 담긴 data class 객체 (주제, 안건, 채팅 내역, 주최자와 참여자)

        Returns:
            Gemini 응답 파싱 결과 (회의 요약 정보가 담긴 dict 리스트)
        """
        history_builder = MeetingHistoryBuilder(meeting_context)
        prompt_list = self._build_prompt_list(history_builder=history_builder)

        config = GenerateContentConfig(  # Gemini API 상세 설정
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
            response_mime_type=self.response_mime_type,
            response_schema=self.response_schema
        )

        # 요청 프롬프트가 입력 토큰 수 제한을 넘어 분할 처리되었을 때와 아닐 때의 로직 분기
        if len(prompt_list) > 1:
            responses = await self.client.process_prompts(prompt_list, config)  # 비동기 처리로 다수의 요청을 한 번에 처리
            parsed_responses = [r.parsed for r in responses]
            summary_data = list(itertools.chain.from_iterable(parsed_responses))  # 파싱한 다수의 응답 결과 병합
        else:
            response = self.client.generate_content(prompt_list[0], config)
            summary_data = response.parsed  # 단일 응답

        agendas = meeting_context.agendas
        included_ids = set()

        for summary in summary_data:
            aid = str(summary["step"])
            summary["is_skipped"] = agendas[aid]["status"] == AgendaStatus.SKIPPED
            included_ids.add(aid)

        # 누락된 안건 추가
        for aid, agenda in agendas.items():
            if aid not in included_ids:
                summary_data.append({
                    "step": int(aid),
                    "sub_topic": agenda["title"],
                    "is_skipped": True
                })

        return cast(list[dict], summary_data)

    @catch_and_raise("Gemini 요약 응답 파싱", GeminiParseError)
    def parse_response_to_summary_data(self, response: list[dict]) -> list[dict]:
        """
        Gemini의 응답을 MongoDB 저장 형식에 맞게 변환

        Args:
            response: Gemini 응답으로부터 파싱된 회의 요약 list[dict]

        Returns:
            안건별 요약이 담긴 list[dict]
            안건별 요약 dict는 안건 번호(agendaId), 안건명(topic), 요약 텍스트(content)로 구성
        """
        summary_list = []
        for data in response:
            step = data.get("step", '')
            sub_topic = data.get("sub_topic", '')
            title = f"{step}. {sub_topic}\n\n"

            is_skipped = data.get("is_skipped", False)

            if is_skipped:
                summary_content = None
            else:
                conclusion = data.get("conclusion", '')
                key_statements = data.get("key_statements", '').split('\n')
                indented_key_statements = ''.join([f"\t{ks}\n" for ks in key_statements])

                key_statements_text = "주요 발언:\n" + indented_key_statements
                conclusion_text = "결론:\n" + '\t' + conclusion

                summary_content = key_statements_text + conclusion_text

            agenda_summary = {
                "agendaId": str(step),
                "topic": sub_topic,
                "content": summary_content
            }

            summary_list.append(agenda_summary)

        return summary_list

    def _build_prompt_list(self, history_builder: MeetingHistoryBuilder) -> list[str]:
        """
        프롬프트 템플릿에 필요한 요소를 삽입하여 최종 프롬프트를 생성

        Note:
            - 토큰 수 제한으로 인해 회의 전체 Context를 하나의 요청 프롬프트에 담지 못할 시 분할 처리 적용
            - 분할 처리 적용 가능성이 있으므로 프롬프트를 항상 리스트에 담아 반환

        Args:
            history_builder: 회의 맥락을 관리하고 프롬프트에 필요한 chunk를 생성하는 MeetingHistoryBuilder

        Returns:
            회의 요약 생성 요청 프롬프트가 담긴 리스트
        """
        # 회의 전체 Context(채팅 기록)에 할당할 토큰 수 계산
        prompt_base = self.template.format(chat_history='')
        history_token_alloc = GeminiClient.INPUT_TOKEN_LIMIT - self.client.count_tokens(prompt_base)

        # 회의 Context 문자열 빌드, 토큰 수 제한에 맞춰 분할 처리 적용
        chunks = history_builder.build_prompt_chunks(
            count_tokens_callback=self.client.count_tokens,
            token_alloc=history_token_alloc
        )

        prompt_list = [self.template.format(chat_history=chunk) for chunk in chunks]
        return prompt_list

