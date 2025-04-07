import os
from dotenv import load_dotenv
from typing import Optional, cast

from google.genai import Client
from google.genai.types import GenerateContentResponse, GenerateContentConfig

import asyncio                  # 비동기 처리
import concurrent.futures       # API 호출용 스레드 관리
import functools                # 키워드 인자를 미리 함수에 고정하기 위해 사용


class GeminiClient:
    DEFAULT_MODEL = "gemini-2.0-flash"  # 사용할 Gemini 모델 이름 미설정 시 기본값
    INPUT_TOKEN_LIMIT = 1048576  # 기본 모델 입력 토큰 제한 수
    OUTPUT_TOKEN_LIMIT = 8192  # 기본 모델 출력 토큰 제한 수

    def __init__(self):
        """
        Gemini 호출을 위한 공통 API 클라이언트 정의

        주요 기능:
         - 요청 텍스트의 토큰 수 계산
         - 텍스트(JSON 문자열 포함) 생성을 요청
         - 비동기적인 API 호출을 지원 (지원되지 않는 배치 처리 구현을 위해)
        """
        load_dotenv()  # .env 파일 로드
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # 환경 변수에서 Gemini API 키 읽기
        self.client = Client(api_key=GEMINI_API_KEY)  # Gemini 클라이언트 초기화


    def count_tokens(self, text: str) -> int:

        """주어진 텍스트의 토큰 수 계산"""

        token_cnt = self.client.models.count_tokens(
            model='gemini-2.0-flash',   # 토큰 수 계산 기준 모델 지정
            contents=text)
        return token_cnt.total_tokens


    def generate_content(
            self,
            prompt: str,
            config: Optional[GenerateContentConfig] = None,
            model: Optional[str] = None
    ) -> GenerateContentResponse:
        """
        Gemini API로 텍스트 생성을 요청하여 응답을 반환

        Args:
            prompt: 입력 프롬프트 텍스트
            config: 요청에 사용될 Generation 설정
            model: 사용할 Gemini 모델 이름 (기본값: gemini-2.0-flash)

        Returns:
            생성된 텍스트 응답 객체 (GenerateContentResponse)
        """
        response = self.client.models.generate_content(
            model=model if model else self.DEFAULT_MODEL,
            contents=prompt,
            config=config,
        )
        return response


    async def generate_content_async(
            self,
            prompt: str,
            config: Optional[GenerateContentConfig] = None,
            model: Optional[str] = None
    ) -> GenerateContentResponse:
        """
        Gemini API 텍스트 생성 요청을 비동기적으로 실행하여 응답을 반환

        Note:
             - self.process_prompts()에서 다수의 프롬프트 요청 처리를 위해 고안
             - 단일 요청은 self.generate_content() 활용할 것)
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:  # 스레드 풀을 사용하여 API 호출
            loop = asyncio.get_running_loop()  # 현재 실행 중인 이벤트 루프 가져오기

            # functools.partial을 사용하여 키워드 인자 고정
            generate_content_with_config = functools.partial(
                self.client.models.generate_content,
                model=model if model else self.DEFAULT_MODEL,
                contents=prompt,
                config=config,
            )

            # 별도의 스레드에서 API 호출 실행
            response = await loop.run_in_executor(executor, generate_content_with_config)
            return response


    async def process_prompts(
            self,
            prompts: list[str],
            config: Optional[GenerateContentConfig] = None,
            model: Optional[str] = None
    ) -> list[GenerateContentResponse]:
        """
        여러 개의 요청 프롬프트를 비동기적으로 처리하여 응답 리스트를 반환
        (프롬프트 입력 순서에 따른 응답 순서 보장)
        """
        tasks = [self.generate_content_async(prompt, config, model) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        return cast(list[GenerateContentResponse], results)
