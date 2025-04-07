# MindSync AI Server: FastAPI 기반 회의 지원 서비스

import logging

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from Prompting.model import RoomIdRequest, ChatGenRequest, AgendaGenRequest, Response
from Prompting.repository import AgendaRepository, ChatRepository, RoomRepository, UserRepository
from Prompting.services import AgendaGenerator, MeetingSummarizer, MbtiChatGenerator
from Prompting.utils import MeetingDataLoader

from Prompting.exceptions.errors import GeminiCallError, GeminiParseError, MongoAccessError, PromptBuildError
from Prompting.exceptions.decorators import catch_and_raise
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

async def load_meeting_room_context(room_id, room_repo, user_repo):
    room_data = await room_repo.get_room_info(room_id)
    user_emails = room_data["participants"] + [room_data["host_email"]]
    user_info_list = await user_repo.get_user_list_by_emails(user_emails)
    return room_data, user_info_list

def create_dataloader(room_data, agenda_data, user_info_list, chat_logs):
    return MeetingDataLoader(
        topic=room_data["content"],
        agendas=agenda_data["agendas"],
        host=room_data["host_email"],
        participants=user_info_list,
        chat_logs=chat_logs
    )

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
        request: AgendaGenRequest,
        agenda_service: AgendaGenerator = Depends(get_agenda_service),
        agenda_repo: AgendaRepository = Depends(get_agenda_repo)
):
    """
    회의 안건 생성 API 엔드포인트

    :param request: 회의 주제 요청, str
    :return: 생성된 회의 안건, id-안건명 매핑된 dict
    """

    # 1. 안건 생성 (Gemini 호출)
    @catch_and_raise("Gemini 안건 생성", GeminiCallError)
    async def generate_agendas():
        agenda_list = await agenda_service.generate_agenda(request.roomId, request.description)
        agendas = agenda_service.parse_response_to_agenda_data(agenda_list)  # DB 저장형식으로 변환
        return agendas

    # 2. MongoDB 저장
    @catch_and_raise("MongoDB 데이터 저장", MongoAccessError)
    async def save_agendas(agendas: dict):
        await agenda_repo.save_agenda(request.roomId, agendas)

    # 실행
    agendas = await generate_agendas()
    await save_agendas(agendas)

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
    회의 요약 생성 API 엔드포인트

    :return: 생성된 회의 요약, JSON string
    """
    # 1. MongoDB 데이터 로드
    @catch_and_raise("MongoDB 데이터 로딩", MongoAccessError)
    async def load_data():
        chat_data = await chat_repo.get_chat_logs_by_room(request.roomId)  # 채팅 내역
        agenda_data = await agenda_repo.get_agenda_by_room(request.roomId)  # 안건 정보
        room_data, user_info_list = await load_meeting_room_context(request.roomId, room_repo, user_repo)  # 채팅방 및 참여자 정보
        return room_data, agenda_data, user_info_list, chat_data

    # 2. 회의 데이터 재구성 객체 초기화
    @catch_and_raise("DataLoader 생성", PromptBuildError)
    async def build_dataloader(room_data, agenda_data, user_info_list, chat_data):
        dataloader = create_dataloader(room_data, agenda_data, user_info_list, chat_data)
        return dataloader

    # 3. 요약 생성 (Gemini 호출)
    @catch_and_raise("Gemini 요약 생성", GeminiCallError)
    async def generate_summary(dataloader):
        summary_list = await summarizer.generate_summary(dataloader)
        summary_dict = summarizer.parse_response_to_summary_data(summary_list)
        return summary_dict

    @catch_and_raise("MongoDB 데이터 저장", MongoAccessError)
    async def save_summary(summary_dict):
        await room_repo.save_summary(request.roomId, summary_dict)

    # 실행
    room_data, agenda_data, user_info_list, chat_data = await load_data()
    dataloader = await build_dataloader(room_data, agenda_data, user_info_list, chat_data)
    summary = await generate_summary(dataloader)
    await save_summary(summary)

    return success_response(data=summary, message="요약 생성을 완료했습니다.")


@app.post("/mbti_chat/", response_model=Response)
async def generate_mbti_chat(
        request: ChatGenRequest,
        bot: MbtiChatGenerator = Depends(get_bot_service),
        chat_repo: ChatRepository = Depends(get_chat_repo),
        room_repo: RoomRepository = Depends(get_room_repo),
        user_repo: UserRepository = Depends(get_user_repo),
        agenda_repo: AgendaRepository = Depends(get_agenda_repo)
):
    """
    MBTI 챗봇의 채팅 생성 API 엔드포인트

    :return: (샘플 데이터에 대해) 생성된 MBTI 챗봇의 채팅, dict
    """
    # 1. MongoDB에서 데이터 로딩 + 안건 유효성 검사
    @catch_and_raise("MongoDB 데이터 로딩", MongoAccessError)
    async def load_data():
        agenda_data = await agenda_repo.get_agenda_by_room(request.roomId)
        if request.agendaId not in agenda_data.get('agendas').keys():
            raise RequestValidationError([{"loc": ["agendaId"], "msg": "유효하지 않은 안건 번호", "type": "value_error"}])

        chat_data = []
        if request.agendaId != '1':  # 첫 번째 안건이 아닐 시
            chat_data = await chat_repo.get_chat_logs_of_previous_agenda(request.roomId, request.agendaId)  # 이전 대화 내역 읽기

        room_data, user_info_list = await load_meeting_room_context(request.roomId, room_repo, user_repo)
        return agenda_data, chat_data, room_data, user_info_list

    # 2. DataLoader 생성
    @catch_and_raise("DataLoader 생성", PromptBuildError)
    async def build_dataloader(room_data, agenda_data, user_info_list, chat_data):
        dataloader = create_dataloader(room_data, agenda_data, user_info_list, chat_data)
        if not dataloader.ai_mbti:
            raise ValueError("봇의 MBTI 설정이 유효하지 않습니다.")
        return dataloader

    # 3. Gemini 챗 생성
    @catch_and_raise("Gemini 챗 생성", GeminiCallError)
    async def generate_chat(dataloader, mbti):
        return await bot.generate_chat(dataloader, mbti, request.agendaId)

    # 실행
    agenda_data, chat_data, room_data, user_info_list = await load_data()
    dataloader = await build_dataloader(room_data, agenda_data, user_info_list, chat_data)
    mbti = dataloader.ai_mbti
    chat = await generate_chat(dataloader, mbti)

    response = {
        "roomId": request.roomId,
        "name": mbti,
        "email": f"{mbti.lower()}@ai.com",
        "message": chat,
        "agenda_id": request.agendaId
    }
    return success_response(data=response, message="MBTI 봇의 채팅 생성을 완료했습니다.")

@app.get("/")
def root():
    """
    루트 경로 핸들러

    :return: 환영 메시지, dict
    """
    return {"message": "Hello It's MindSync AI service server"}
