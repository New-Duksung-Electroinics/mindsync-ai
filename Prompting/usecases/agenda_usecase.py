# 안건 생성 하위 use case 모음
from Prompting.exceptions import catch_and_raise, MongoAccessError, GeminiCallError
from Prompting.services import AgendaGenerator
from Prompting.schemas import AgendaRequest
from Prompting.repository import AgendaRepository


# 1. 안건 생성 (Gemini 호출)
@catch_and_raise("Gemini 안건 생성", GeminiCallError)
async def generate_agendas(request: AgendaRequest, agenda_service: AgendaGenerator):
    agenda_list = await agenda_service.generate_agenda(request.roomId, request.description)
    agendas = agenda_service.parse_response_to_agenda_data(agenda_list)  # DB 저장형식으로 변환
    return agendas

# 2. MongoDB 저장
@catch_and_raise("MongoDB 데이터 저장", MongoAccessError)
async def save_agendas(request: AgendaRequest, agendas: dict, agenda_repo: AgendaRepository):
    await agenda_repo.save_agenda(request.roomId, agendas)