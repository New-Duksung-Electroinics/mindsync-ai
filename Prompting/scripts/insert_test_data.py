from Prompting.repository.mongo_client import MONGO_URI, ROOM_COLLECTION, CHAT_COLLECTION, AGENDA_COLLECTION, USER_COLLECTION, MONGO_DB_NAME
from Prompting.common.enums import AgendaStatus
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
JSON_FILE_PATH = os.path.join(base_dir, "./data/meeting_log_sample_2.json")  # 회의 채팅 내역 샘플 데이터 파일 경로
BOT_MBTI = "ENFP"
TEST_ROOM_ID = "TEST_ROOM_ID"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

def already_inserted():
    return db[ROOM_COLLECTION].find_one({"_id": TEST_ROOM_ID}) is not None

def insert_chatroom(title, content, host, participants, mbti=BOT_MBTI):
    chatroom = {
        "_id": TEST_ROOM_ID,
        "host_email": host,
        "title": title,
        "content": content,
        "participants": participants,
        "mbti": mbti,
        "meta": {"version": "v1"}   # 테스트용 데이터 구분을 위한 메타 정보
    }
    db[ROOM_COLLECTION].insert_one(chatroom)
    return TEST_ROOM_ID      # 문서 id 반환

def insert_chat(timestamp, roomId, sender_email, sender_name, msg, agendaId):
    chat = {
        "roomId": roomId,
        "timestamp": timestamp,
        "email": sender_email,
        "name": sender_name,
        "message": msg,
        "agenda_id": agendaId,
        "meta": {"version": "v1"}
    }
    db[CHAT_COLLECTION].insert_one(chat)

def insert_user(email, name, mbti="ISTJ", password="1234qwer!"):
    chat = {
        "email": email,
        "password": password,
        "username": name,
        "usermbti": mbti,
        "meta": {"version": "v1"}
    }
    db[USER_COLLECTION].insert_one(chat)

def insert_agenda(roomId, agendas_dict):
    last_agenda_id = str(len(agendas_dict) + 1)
    agendas_dict[last_agenda_id] = "예비 안건 (회의 중 추가 논의 시)"
    for aid in agendas_dict:
        title = agendas_dict[aid]
        agendas_dict[aid] = {
            "title": title,
            "status": AgendaStatus.PENDING.value
        }
    agenda = {
        "_id": roomId,
        "roomId": roomId,
        "agendas": agendas_dict,
        "meta": {"version": "v1"}
    }
    db[AGENDA_COLLECTION].insert_one(agenda)

def insert_ai_bots():
    import itertools
    mbti_options = ['EI', 'SN', 'TF', 'JP']
    mbti_types = [''.join(combination) for combination in itertools.product(*mbti_options)]
    for mbti in mbti_types:
        email = f"{mbti.lower()}@ai.com"
        insert_user(email, mbti, mbti)

def insert_sample_meeting_data(json_file_path, ai_mbti):

    with open(json_file_path, 'r', encoding="utf-8") as f:
        json_string = f.read()

    data = json.loads(json_string)  # JSON 문자열 파싱

    topic = data.get('topic', '')  # 회의 주제
    speakers = data.get('speakers', [])  # 발언자 목록

    title = f"{topic} 회의"
    content = topic
    participants = []
    host_email = ''
    for s in speakers:
        name = s.get('name', '')
        email = f"user{s.get('id', -1) + 1}@example.com"
        if s.get('isModerator', False):
            host_email = email
        participants.append(email)
        insert_user(email, name)

    # AI 참가자 추가
    participants.append(f"{ai_mbti.lower()}@ai.com")

    roomId = insert_chatroom(
        title=title,
        content=content,
        host=host_email,
        participants=participants
    )

    contents = data.get('contents', [])  # 안건별 발언 내용
    agendas = {}
    chat_idx = 0
    for content in contents:
        step = content.get('step', '0')  # 안건 번호
        sub_topic = content.get('sub_topic', '')  # 안건 제목
        agendas[step] = sub_topic

        chat_list = content.get('utterance', [])  # 발언 목록
        for c in chat_list:
            email = f"user{c.get('speaker_id', -1) + 1}@example.com"  # 발언자 이메일
            name = c.get('speaker_name', '')
            msg = c.get('msg', '')  # 발언 내용

            # 임의 타임 스탬프 찍기(5초 간격)
            now = datetime.now()
            delayed_time = now + timedelta(seconds=5*chat_idx)
            timestamp =delayed_time.strftime("%Y-%m-%d %H:%M:%S")

            # msgId = f"{roomId}-{str(chat_idx).zfill(10)}",  # 일단 임의로 부여
            insert_chat(
                timestamp=timestamp,
                roomId=roomId,
                sender_email=email,
                sender_name=name,
                msg=msg,
                agendaId=step
            )
            chat_idx += 1
    insert_agenda(roomId=roomId, agendas_dict=agendas)


if not already_inserted():
    print("✅ 테스트 데이터가 존재하지 않아 삽입합니다.")
    insert_ai_bots()
    insert_sample_meeting_data(JSON_FILE_PATH, BOT_MBTI)
else:
    print("⏭️ 이미 테스트 데이터가 존재하므로 삽입하지 않습니다.")
