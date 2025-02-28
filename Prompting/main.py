"""
FastAPI를 사용하여 회의 안건 생성 및 요약 기능을 제공하는 웹 서버 애플리케이션 구현.

주요 기능:
    - Gemini API를 활용하여 회의 주제 요청에 따른 안건 생성(JSON 형식)
    - Gemini API를 활용하여 회의록 요약 생성(JSON 형식)
    - Gemini API를 활용하여 특정한 MBTI 성향의 가상 회의 참여자 채팅 생성
"""
from Prompting.services.agenda_generator import AgendaGenerator
from Prompting.utils.meeting_data_loader import MeetingDataLoader
from Prompting.services.meeting_summarizer import MeetingSummarizer
from Prompting.services.mbti_chat_generator import MbtiChatGenerator
from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)  # 로깅 설정

json_file_path = "./Prompting/data_samples/meeting_log_sample_2.json"  # 회의 채팅 내역 샘플 데이터 파일 경로
mbti_instruction_file_path = "./Prompting/utils/mbti_type_instructions.json"  # AI 모델이 참조할 MBTI 성향 정보가 담긴 파일 경로
with open(json_file_path, 'r', encoding="utf-8") as f:
    file_string = f.read()
meetingDataloader = MeetingDataLoader(file_string)  # 회의 데이터 로더 객체 생성

agenda_service = AgendaGenerator()  # 안건 생성 서비스 객체 생성
summarizer = MeetingSummarizer()  # 회의 요약 서비스 객체 생성
mbti_bot = MbtiChatGenerator(mbti_instruction_file_path)  # MBTI 챗봇 객체 생성

app = FastAPI()  # FastAPI 애플리케이션 생성

@app.get("/")
def root():
    """
    루트 경로 핸들러

    :return: 환영 메시지, dict
    """
    return {"message": "Hello It's MindSync AI service server"}

@app.get("/home")
def home():
    """
    /home 경로 핸들러

    :return: 기본 메시지, dict
    """
    return {"message": "home"}

@app.get("/agenda_generation/{request}")
# @app.post("/agenda_generation/")
async def generate_agenda(request: str):
    """
    회의 안건 생성 API 엔드포인트

    :param request: 회의 주제 요청, str
    :return: 생성된 회의 안건 목록, JSON string
    """
    agenda_list = await agenda_service.generate_agenda(request)  # 안건 생성
    for agenda in agenda_list:
        print(agenda)  # 생성된 안건 출력
    return agenda_list  # 생성된 안건 반환

# 일단 샘플 데이터에 대해 요약 생성 임시 구현
@app.get("/summarize/")
async def summarize_meeting_chat():
    """
    회의 요약 생성 API 엔드포인트

    :return: (샘플 데이터에 대해) 생성된 회의 요약, JSON string
    """
    agenda_summary_list = await summarizer.generate_summary(meetingDataloader)  # 요약 생성
    return agenda_summary_list  # 생성된 요약 반환


# 일단 샘플 데이터에 대해 채팅 생성하도록 임시 구현
@app.get("/mbti_chat/{mbti}")
async def summarize_meeting_chat(mbti: str):
    """
    MBTI 챗봇의 채팅 생성 API 엔드포인트

    :param mbti: 챗봇의 MBTI 성향 (예: INFJ), str
    :return: (샘플 데이터에 대해) 생성된 MBTI 챗봇의 채팅, dict
    """
    step = int(meetingDataloader.contents[-1].get("step", 0)) + 1   # 테스트용 안건 순서
    sub_topic = "인사 이동 계획"                                      # 테스트용 안건명
    chat = await mbti_bot.generate_chat(meetingDataloader, "intp", step, sub_topic)
    return {"chat_from_bot": chat}