"""
Gemini 호출을 위한 공통 API 클라이언트 정의

주요 기능:
    - Gemini API를 사용하여 토큰 수를 계산
    - 텍스트 생성을 요청
    - 비동기적인 API 호출을 지원 (여러 요청을 동시에 처리할 수 있도록)
        - Gemini API에 배치 처리가 제공되지 않아서
"""
from google import genai
import asyncio                  # 비동기 처리
import concurrent.futures       # API 호출용 스레드 관리
import functools                # 키워드 인자를 미리 함수에 고정하기 위해 사용
from dotenv import load_dotenv
import os


class GeminiClient:
    def __init__(self):
        """
        GeminiClient 클래스 생성자

        .env 파일에서 Gemini API 키를 읽어와 Gemini 클라이언트 초기화
        """
        load_dotenv()  # .env 파일 로드
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # 환경 변수에서 Gemini API 키 읽기
        self.client = genai.Client(api_key=GEMINI_API_KEY)  # Gemini 클라이언트 초기화

    def count_tokens(self, text):
        """
        주어진 텍스트의 토큰 수 계산

        :param text: 토큰 수를 계산할 텍스트, str
        :return: 텍스트의 토큰 수, int
        """
        token_cnt = self.client.models.count_tokens(
            model='gemini-2.0-flash',   # 토큰 수 계산 기준 모델 지정
            contents=text)
        return token_cnt

    def generate_content(self, prompt, config=None, model=None):
        """
        Gemini API를 사용하여 텍스트 생성

        :param prompt: 생성할 텍스트에 대한 요청 프롬프트, str
        :param config: 텍스트 생성을 위한 상세 설정 (선택 사항)
        :param model: 사용할 Gemini 모델명 (선택사항, 기본값, gemini-2.0-flash), str
        :return: Gemini API 응답 객체
        """
        response = self.client.models.generate_content(
            model=model if model else "gemini-2.0-flash",
            contents=prompt,
            config=config,
        )
        return response

    async def generate_content_async(self, prompt, config=None, model=None):
        """
        Gemini API 텍스트 생성 요청을 비동기적으로 실행

        :param prompt: 생성할 텍스트에 대한 요청 프롬프트, str
        :param config: 텍스트 생성을 위한 상세 설정 (선택 사항)
        :param model: 사용할 Gemini 모델명 (선택사항, 기본값, gemini-2.0-flash), str
        :return: Gemini API 응답 객체
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:  # 스레드 풀을 사용하여 API 호출
            loop = asyncio.get_running_loop()  # 현재 실행 중인 이벤트 루프 가져오기

            # functools.partial을 사용하여 키워드 인자 고정
            generate_content_with_config = functools.partial(
                self.client.models.generate_content,
                model=model if model else "gemini-2.0-flash",
                contents=prompt,
                config=config,
            )
            result = await loop.run_in_executor(
                executor, generate_content_with_config  # 별도의 스레드에서 API 호출 실행
            )
            return result

    async def process_prompts(self, prompts, config=None, model=None):
        """
        여러 개의 텍스트 생성 요청 프롬프트를 비동기적으로 처리

        :param prompts: 여러 개의 요청 프롬프트 목록, list
        :param config: 텍스트 생성을 위한 상세 설정 (선택 사항)
        :param model: 사용할 Gemini 모델명 (선택사항, 기본값, gemini-2.0-flash), str
        :return: Gemini API 응답 객체 목록, list
        """
        tasks = [self.generate_content_async(prompt, config, model) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        return results
