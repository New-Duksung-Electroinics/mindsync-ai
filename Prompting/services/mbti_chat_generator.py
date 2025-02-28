"""
Gemini API를 사용하여 MBTI 성향이 반영된 가상 참여자의 채팅을 생성하는 클래스

회의 주제, 직전 안건에 대한 논의 내용, 넘어가고자 하는 안건에 대한 정보를 바탕으로 MBTI 성향 정보를 반영해 채팅 생성.
"""
from .gemini_client import GeminiClient
from google.genai import types
from Prompting.utils.mbti_instructor import MbtiInstructor

prompt_kor_template = \
    """
너는 MBTI 성격유형에서 {mbti} 성향을 가진 회의 참여자야. {topic}에 대한 회의를 진행 중이고, 
이제 {step}번째 안건인 {sub_topic}에 대해 논의를 시작하려고 해.
모두의 회의 참여를 잘 독려하고 원활한 회의 진행을 위한 회의 참여자로서의 채팅을 {hangul_length_limit}자 내로 작성해줘. 
마크다운 서식은 절대 사용하지 말고.
네가 회의의 맥락을 더 이해할 수 있게 바로 직전에 논의했던 안건에 대한 채팅 내역 전문과 {mbti} 성향의 특징에 대한 자료를 함께 제공해줄게.

Your personality info:
{mbti_info}

Previous chat history: {prev_chat_history}
"""

prompt_eng_template = \
    """
You're a meeting participant with the MBTI personality type {mbti}.
You're in a meeting about {topic}, 
and you're about to start discussing the {step}th agenda item, {sub_topic}.
To keep everyone engaged and the meeting running smoothly, please write a chat as a meeting participant in Korean in 300 characters or less. 
Never use markdown formatting.
To help you understand the context of the meeting, 
 I'll provide you with the full chat transcript of the agenda item we just discussed, as well as a resource on {mbti} personality traits.

Your personality traits:
{mbti_info}

Previous chat history: 
{prev_chat_history}
"""


class MbtiChatGenerator():
    def __init__(self, mbti_instruction_file_path, temperature=1.5, top_p=0.95, top_k=40, max_output_tokens=8192):
        """
        MeetingSummarizer 클래스 생성자

        :param instruction_file_path: 모델이 참조할 MBTI 정보가 담긴 JSON 파일의 경로, str
        :param temperature: 모델의 온도 설정 (기본값: 1, 설정 가능 범위: 0~2)
        :param top_p: (단어의) 확률 기반 샘플링을 위한 top_p 값 (기본값: 0.95)
        :param top_k: (단어의) 확률 기반 샘플링을 위한 top_k 값 (기본값: 40)
        :param max_output_tokens: 최대 출력 토큰 수 (기본값: 8192, 최댓값)
        """
        self.client = GeminiClient()  # Gemini API 클라이언트 초기화
        self.template = prompt_kor_template  # 회의록 생성을 위한 프롬프트 템플릿

        # 모델 config 값 설정
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens

        self.mbtiInstructor = MbtiInstructor(mbti_instruction_file_path)  # MBTI 성향 정보 데이터를 제공하는 객체

    def _generate_prompt(self, mbti, topic, step, sub_topic, prev_chat_history, hangul_length_limit=500):
        """
        프롬프트 템플릿에 필요한 요소를 삽입하여 최종 프롬프트를 생성

        :param mbti: 챗봇의 mbti 성향, str
        :param topic: 회의 주제, str
        :param step: 현재 시작되는 안건의 순서, int
        :param sub_topic: 현재 시작되는 안건명, str
        :param prev_chat_history: 직전 안건의 내역, str
        :param hangul_length_limit: 챗봇이 생성할 채팅의 길이 제한값(한글 n자), int
        :return: 생성된 프롬프트, str
        """

        prompt = self.template.format(
            mbti=mbti,
            topic=topic,
            step=step,
            sub_topic=sub_topic,
            prev_chat_history=prev_chat_history,
            hangul_length_limit=hangul_length_limit,
            mbti_info=self.mbtiInstructor.process_mbti_info_for_prompt(mbti),
        )
        return prompt

    async def generate_chat(self, dataloader, mbti, step, sub_topic):
        """
        Gemini API를 사용하여 MBTI 성향 봇의 채팅을 생성

        :param dataloader: 회의 채팅 내역 데이터 로더 객체, MeetingDataLodaer
        :param mbti: 챗봇의 mbti 성향, str
        :param step: 현재 시작되는 안건의 순서, int
        :param sub_topic: 현재 시작되는 안건명, str
        :return: 생성된 채팅, str
        """
        # 채팅 내역 텍스트를 목록으로 준비(토큰 수 제한 고려해 필요 시 분할 처리)
        topic = dataloader.topic
        prev_chat_history = dataloader.process_prev_chat_history_for_prompt()
        prompt = self._generate_prompt(mbti, topic, step, sub_topic, prev_chat_history)
        config = types.GenerateContentConfig(
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
        )
        response = await self.client.generate_content_async(prompt, config)
        return response.text
