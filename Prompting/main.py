# MindSync AI Server: FastAPI 기반 회의 지원 서비스

import logging

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from Prompting.schemas import RoomIdRequest, ChatRequest, AgendaRequest, Response, ChatResponse
from Prompting.repository import AgendaRepository, ChatRepository, RoomRepository, UserRepository
from Prompting.services import AgendaGenerator, MeetingSummarizer, MbtiChatGenerator
from Prompting.services.context_builders.meeting_history_builder import MeetingHistoryBuilder
from Prompting.usecases.agenda_usecase import generate_agendas, save_agendas
from Prompting.usecases.summarize_usecase import load_summary_context, generate_summary, save_summary
from Prompting.usecases.mbti_chat_usecase import load_chat_context, generate_chat

from Prompting.exceptions.errors import GeminiCallError, GeminiParseError, MongoAccessError, PromptBuildError
from Prompting.exceptions.handlers import custom_exception_handler, request_validation_exception_handler, general_exception_handler


# -------------------- 기본 설정 ------------------------
logging.basicConfig(level=logging.INFO)  # 로깅 설정
app = FastAPI()  # FastAPI 애플리케이션 생성

# -------------------- 전역 핸들러 등록 --------------------
for exc in [GeminiCallError, GeminiParseError, MongoAccessError, PromptBuildError]:
    app.add_exception_handler(exc, custom_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# -------------------- 공통 유틸 함수 --------------------
def success_response(data=None, message="요청이 성공했습니다."):
    return JSONResponse(status_code=200, content={"status": "SUCCESS", "message": message, "data": data})

# -------------------- DI 함수 -------------------------
def get_agenda_service():
    return AgendaGenerator()
def get_summarizer_service():
    return MeetingSummarizer()
def get_bot_service():
    return MbtiChatGenerator()
def get_agenda_repo():
    return AgendaRepository()
def get_chat_repo():
    return ChatRepository()
def get_room_repo():
    return RoomRepository()
def get_user_repo():
    return UserRepository()

# -------------------- 엔드포인트 --------------------
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
    agendas = await generate_agendas(request, agenda_service)
    await save_agendas(request, agendas, agenda_repo)

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
    history_builder = MeetingHistoryBuilder(
        topic=meeting_context.topic,
        agendas=meeting_context.agendas,
        host=meeting_context.host,
        participants=meeting_context.participants,
        chat_logs=meeting_context.chats
    )
    summary = await generate_summary(history_builder, summarizer)
    await save_summary(request, summary, room_repo)

    return success_response(data=summary, message="요약 생성을 완료했습니다.")


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
    history_builder = MeetingHistoryBuilder(
        topic=meeting_context.topic,
        agendas=meeting_context.agendas,
        host=meeting_context.host,
        participants=meeting_context.participants,
        chat_logs=meeting_context.chats
    )
    mbti = history_builder.ai_mbti
    if not mbti:
        raise PromptBuildError()

    chat = await generate_chat(request, history_builder, mbti, bot)
    response = ChatResponse(
        roomId=request.roomId,
        name=mbti,
        email=f"{mbti.lower()}@ai.com",
        message=chat,
        agenda_id=request.agendaId
    )
    return success_response(data=response.dict(), message="MBTI 봇의 채팅 생성을 완료했습니다.")

@app.get("/")
def root():
    """
    루트 경로 핸들러

    :return: 환영 메시지, dict
    """
    return {"message": "Hello It's MindSync AI service server"}
