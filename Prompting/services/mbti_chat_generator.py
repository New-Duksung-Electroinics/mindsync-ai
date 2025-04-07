"""
Gemini API를 사용하여 MBTI 성향이 반영된 가상 참여자의 채팅을 생성하는 클래스

회의 주제, 직전 안건에 대한 논의 내용, 넘어가고자 하는 안건에 대한 정보를 바탕으로 MBTI 성향 정보를 반영해 채팅 생성.
"""
from .gemini_client import GeminiClient
from google.genai import types
from Prompting.services.context_builders.mbti_trait_builder import MbtiTraitBuilder
from .templates import CHAT_CONTEXT_KR, CHAT_PROMPT_KR


class MbtiChatGenerator():
    def __init__(self, mbti_instruction_file_path=None, temperature=1.5, top_p=0.95, top_k=40, max_output_tokens=8192):
        """
        MeetingSummarizer 클래스 생성자

        :param instruction_file_path: 모델이 참조할 MBTI 정보가 담긴 JSON 파일의 경로, str
        :param temperature: 모델의 온도 설정 (기본값: 1, 설정 가능 범위: 0~2)
        :param top_p: (단어의) 확률 기반 샘플링을 위한 top_p 값 (기본값: 0.95)
        :param top_k: (단어의) 확률 기반 샘플링을 위한 top_k 값 (기본값: 40)
        :param max_output_tokens: 최대 출력 토큰 수 (기본값: 8192, 최댓값)
        """
        self.client = GeminiClient()  # Gemini API 클라이언트 초기화
        self.template = CHAT_PROMPT_KR  # 프롬프트 템플릿
        self.context_template = CHAT_CONTEXT_KR  # 이전 채팅 내역 첨부를 위한 템플릿

        # 모델 config 값 설정
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens

        # MBTI 성향 정보 데이터를 제공하는 객체
        self.trait_builder = MbtiTraitBuilder(mbti_instruction_file_path) if mbti_instruction_file_path \
            else MbtiTraitBuilder()


    def _generate_prompt(self, mbti, topic, step, sub_topic, prev_chat_history, hangul_length_limit=300):
        """
        프롬프트 템플릿에 필요한 요소를 삽입하여 최종 프롬프트를 생성

        :param mbti: 챗봇의 mbti 성향, str
        :param topic: 회의 주제, str
        :param step: 현재 시작되는 안건의 순서, str
        :param sub_topic: 현재 시작되는 안건명, str
        :param prev_chat_history: 직전 안건의 내역, str
        :param hangul_length_limit: 챗봇이 생성할 채팅의 길이 제한값(한글 n자), int
        :return: 생성된 프롬프트, str
        """

        prompt = self.template.format(
            mbti=mbti,
            topic=topic,
            sub_topic=sub_topic,
            hangul_length_limit=hangul_length_limit,
            mbti_info=self.trait_builder.build_trait_summary(mbti),
        )

        if int(step) > 1:  # 첫 안건이 아니면, 직전 안건 대화 context를 함께 전달
            context = self.context_template.format(
                prev_chat_history=prev_chat_history
            )
            prompt += '\n' + context

        return prompt

    async def generate_chat(self, history_builder, mbti, step):
        """
        Gemini API를 사용하여 MBTI 성향 봇의 채팅을 생성

        :param history_builder: 회의 채팅 내역 데이터 로더 객체, MeetingDataLodaer
        :param mbti: 챗봇의 mbti 성향, str
        :param step: 현재 시작되는 안건의 순서, int
        :param sub_topic: 현재 시작되는 안건명, str
        :return: 생성된 채팅, str
        """
        # 채팅 내역 텍스트를 목록으로 준비(토큰 수 제한 고려해 필요 시 분할 처리)
        topic = history_builder.topic
        prev_chat_history = history_builder.build_prompt_chunks()
        sub_topic = history_builder.agendas.get(step, '')
        prompt = self._generate_prompt(mbti, topic, step, sub_topic, prev_chat_history)
        config = types.GenerateContentConfig(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
        )
        response = await self.client.generate_content_async(prompt, config)
        return response.text
