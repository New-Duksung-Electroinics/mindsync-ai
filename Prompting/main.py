# MindSync AI Server: FastAPI 기반 회의 지원 서비스

import logging
from typing import Any

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from Prompting.schemas import RoomIdRequest, ChatRequest, AgendaRequest, Response
from Prompting.repository import AgendaRepository, ChatRepository, RoomRepository, UserRepository
from Prompting.services import AgendaGenerator, MeetingSummarizer, MbtiChatGenerator
from Prompting.usecases import load_summary_context, load_chat_context

from Prompting.exceptions.errors import GeminiCallError, GeminiParseError, MongoAccessError, PromptBuildError
from Prompting.exceptions.decorators import catch_and_raise
from Prompting.exceptions.handlers import custom_exception_handler, request_validation_exception_handler, general_exception_handler

from Prompting.common.resonse_util import success_response

from .di import (
    get_agenda_repo, get_room_repo, get_chat_repo, get_user_repo,
    get_agenda_service, get_bot_service, get_summarizer_service
)


# 기본 설정 및 예외 핸들러 등록 ------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)  # 로깅 설정
app = FastAPI()  # FastAPI 애플리케이션 생성

# 허용할 origin 지정
origins = [
    "http://localhost:3000",  # (개발용) 프론트엔드 주소 -> 배포 시 도메인 주소로 변경
]

# ✅ CORS 미들웨어 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] (모두 허용)
    allow_credentials=True,
    allow_methods=["*"],    # or ["POST", "GET"]
    allow_headers=["*"],
)

for exc in [GeminiCallError, GeminiParseError, MongoAccessError, PromptBuildError]:
    app.add_exception_handler(exc, custom_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# API 엔드포인트 -------------------------------------------------------------------------------------
@app.post("/agenda_generation/", response_model=Response)
async def generate_and_save_agendas(
        request: AgendaRequest,
        agenda_service: AgendaGenerator = Depends(get_agenda_service),
        agenda_repo: AgendaRepository = Depends(get_agenda_repo)
):
    """
    회의 안건 생성 API

    Args:
        request: 회의 안건 생성 요청 body
        agenda_service: Gemini 기반 안건 생성 서비스 객체 (DI 자동 관리)
        agenda_repo: 안건 데이터 관리 객체 (DI 자동 관리)

    Returns:
        Response 형식의 JSONResponse (상세는 API 명세서에서 확인)
    """
    agenda_list = await agenda_service.generate_agenda(topic_request=request.description)
    agendas = agenda_service.parse_response_to_agenda_data(response=agenda_list)
    await agenda_repo.save_agenda(room_id=request.roomId, agenda_dict=agendas)

    return success_response(data=agendas, message="안건 생성을 완료했습니다.")


@app.post("/summarize/", response_model=Response)
async def summarize_meeting_chat(
        request: RoomIdRequest,
        summarizer: MeetingSummarizer = Depends(get_summarizer_service),
        chat_repo: ChatRepository = Depends(get_chat_repo),
        room_repo: RoomRepository = Depends(get_room_repo),
        user_repo: UserRepository = Depends(get_user_repo),
        agenda_repo: AgendaRepository = Depends(get_agenda_repo)
):
    """
    회의 요약 생성 API

    Args:
        request: 회의 요약 생성 요청 body
        summarizer: Gemini 기반 요약 생성 서비스 객체 (DI 자동 관리)
        chat_repo: 채팅 데이터 관리 객체 (DI 자동 관리)
        room_repo: 채팅방 데이터 관리 객체 (DI 자동 관리)
        user_repo: 사용자 데이터 관리 객체 (DI 자동 관리)
        agenda_repo: 안건 데이터 관리 객체 (DI 자동 관리)

    Returns:
        Response 형식의 JSONResponse (상세는 API 명세서에서 확인)
    """
    meeting_context = await load_summary_context(request.roomId, chat_repo, agenda_repo, room_repo, user_repo)
    summary = await summarizer.generate_summary(meeting_context)
    summary_data = summarizer.parse_response_to_summary_data(summary)
    await room_repo.save_summary(room_id=request.roomId, summary=summary_data)

    return success_response(data=summary_data, message="요약 생성을 완료했습니다.")


@app.post("/mbti_chat/", response_model=Response)
async def generate_mbti_chat(
        request: ChatRequest,
        bot: MbtiChatGenerator = Depends(get_bot_service),
        chat_repo: ChatRepository = Depends(get_chat_repo),
        room_repo: RoomRepository = Depends(get_room_repo),
        user_repo: UserRepository = Depends(get_user_repo),
        agenda_repo: AgendaRepository = Depends(get_agenda_repo)
):
    """
    MBTI 봇 채팅 생성 API

    Args:
        request: 채팅 생성 요청 body
        bot: Gemini 기반 MBTI 봇 채팅 생성 서비스 객체 (DI 자동 관리)
        chat_repo: 채팅 데이터 관리 객체 (DI 자동 관리)
        room_repo: 채팅방 데이터 관리 객체 (DI 자동 관리)
        user_repo: 사용자 데이터 관리 객체 (DI 자동 관리)
        agenda_repo: 안건 데이터 관리 객체 (DI 자동 관리)

    Returns:
        Response 형식의 JSONResponse (상세는 API 명세서에서 확인)
    """
    meeting_context = await load_chat_context(request, chat_repo, agenda_repo, room_repo, user_repo)
    chat_response = await bot.generate_chat(meeting_context=meeting_context, request=request)

    return success_response(data=chat_response.dict(), message="MBTI 봇의 채팅 생성을 완료했습니다.")


@app.get("/")
def root():
    """루트 경로 핸들러"""
    return {"message": "Hello It's MindSync AI service server"}
