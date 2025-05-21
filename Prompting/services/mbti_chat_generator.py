from .gemini_client import GeminiClient
from google.genai.types import GenerateContentConfig
from Prompting.services.context_builders import MbtiTraitBuilder, MeetingHistoryBuilder
from .templates import CHAT_CONTEXT_KR, CHAT_PROMPT_KR
from Prompting.usecases.meeting_context import MeetingContext
from Prompting.exceptions import GeminiCallError, PromptBuildError, catch_and_raise
from Prompting.schemas import ChatRequest, ChatResponse


class MbtiChatGenerator:
    HANGEUL_ZA_LIMIT = 300  # 봇의 채팅을 한글 기준 몇 자 이내로 생성할 지

    def __init__(self, mbti_instruction_file_path: str = None,
                 temperature: float = 1.5, top_p: float = 0.95, top_k: int = 40):
        """
        Gemini API로 MBTI 성향이 반영된 가상 참여자의 채팅을 생성

        Args:
            mbti_instruction_file_path: 모델이 참조할 MBTI 정보가 담긴 JSON 파일의 경로
            temperature: 모델의 온도 설정 (기본값: 1, 설정 가능 범위: 0~2)
            top_p: (단어의) 확률 기반 샘플링을 위한 top_p 값 (기본값: 0.95)
            top_k: (단어의) 확률 기반 샘플링을 위한 top_k 값 (기본값: 40)
        """
        self.client = GeminiClient()  # Gemini API 클라이언트 초기화
        self.template = CHAT_PROMPT_KR  # 회의록 생성을 위한 프롬프트 템플릿
        self.context_template = CHAT_CONTEXT_KR  # 이전 채팅 내역 첨부를 위한 템플릿

        # 모델 config 값 설정
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = int(self.HANGEUL_ZA_LIMIT * 0.8)   # Gemini는 대략 한글 1~2자에 토큰 1개 사용

        # MBTI 성향 정보 데이터를 제공하는 객체
        self.trait_builder = MbtiTraitBuilder(mbti_instruction_file_path) if mbti_instruction_file_path \
            else MbtiTraitBuilder()


    @catch_and_raise("Gemini 챗 생성", GeminiCallError)
    async def generate_chat(self, meeting_context: MeetingContext, request: ChatRequest) -> ChatResponse:
        """
        Gemini API로 AI 참여자 챗봇의 채팅을 생성

        Args:
            meeting_context: 회의 맥락이 담긴 data class 객체 (주제, 안건, 채팅 내역, 주최자와 참여자)
            step: 새로 시작하는 안건 번호(=안건 ID)

        Returns:
            Gemini 응답 파싱 결과 (AI 참여자 챗봇의 채팅 텍스트)
        """
        history_builder = MeetingHistoryBuilder(meeting_context)
        prompt = self._build_prompt(step=request.agendaId, history_builder=history_builder)
        config = GenerateContentConfig(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
        )
        response = self.client.generate_content(prompt, config)
        chat = response.text
        bot = history_builder.bot
        return ChatResponse(
            roomId=request.roomId,
            name=bot.name,
            email=bot.email,
            agenda_id=request.agendaId,
            message=chat
        )


    @catch_and_raise("Gemini 챗 생성 프롬프트 빌드", PromptBuildError)
    def _build_prompt(self, step: str, history_builder: MeetingHistoryBuilder) -> str:
        """
        프롬프트 템플릿에 필요한 요소를 삽입하여 최종 프롬프트를 생성

        Args:
            step: 새로 시작하는 안건 번호(=안건 ID)
            history_builder: 회의 맥락을 관리하고 프롬프트에 필요한 chunk를 생성하는 MeetingHistoryBuilder

        Returns:
            AI 참여자의 채팅 생성 요청 프롬프트
        """
        mbti = history_builder.bot.mbti  # 참여자 봇의 mbti
        agenda_title = history_builder.agendas.get(step)
        topic = history_builder.topic

        if not agenda_title or not mbti:
            raise PromptBuildError("안건명 및 봇 MBTI 정보 누락")

        mbti_info = self.trait_builder.build_trait_summary(mbti)

        prompt = self.template.format(
            mbti=mbti,
            topic=topic,
            sub_topic=agenda_title,
            hangul_length_limit=self.HANGEUL_ZA_LIMIT,
            mbti_info=mbti_info
        )

        # 유효한 직전 안건 대화 context가 존재할 시 함께 전달
        if history_builder.chats:
            chunks = history_builder.build_prompt_chunks()
            if len(chunks) > 1:
                raise PromptBuildError("의도치 않은 프롬프트 분할 발생")  # context 뭉치가 분할 처리되었으면 에러 발생시키기

            context = self.context_template.format(prev_chat_history=chunks[0])
            prompt += '\n' + context

        return prompt

