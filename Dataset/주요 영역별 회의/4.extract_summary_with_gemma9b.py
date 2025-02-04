"""
원천 데이터셋으로부터 회의 안건 및 주요 발언 내용 라벨링 구축하기

Gemma2를 활용해 원천 데이터셋(회의 중 대화 내역)으로부터 회의의 주요 안건을 추출하고,
각 안건별 참여자들의 주요 발언 정리를 생성해 라벨링 구축 (2025.02.03 아직 코드 작성 중)
"""
import os
import glob
import json
import ollama

parent_dir = "./processed"  # 처리 후 저장할 부모 폴더
category_dirs = os.listdir(parent_dir)  # 하위 디렉토리 읽어오기

def get_chat_string(utter, speaker_name, is_speaker_moderator):
    """
    발화자와 발화 내용을 '이름: 내용' 형식으로 변환하는 함수.
    :param utter: 발화 내용, str
    :param speaker_name: 발화자 이름, str
    :param is_speaker_moderator: 발화자가 사회자인지, bool
    :return: '이름: 내용' 또는 '이름(사회자): 내용' 형식의 문자열, str
    """
    speaker_role = "(사회자)" if is_speaker_moderator else ""
    return f"{speaker_name}{speaker_role}: {utter}"

def get_meeting_overview_string(data):
    """
    회의 개요 정보를 문자열로 반환하는 함수.
    :param data: JSON 원천 데이터, dict
    :return: 회의 개요 정보가 담긴 문자열, str
    """
    return '\n'.join([
        "1. 회의 개요",
        f"회의 주제: {data.get('topic', '')}",
        f"회의 키워드: {', '.join(data.get('keyword', []))}",
        f"회의 날짜: {data.get('metadata', {}).get('date', '')}"
    ])

def get_meeting_chat_logs(data, max_length=2000):
    """
    발언 내용을 2000자 이내로 끊어 반환하는 함수.
    Gemma2 토큰 수 제약(8,192)을 고려해 총 2700자 정도 내에서 프롬프트 작성 권고.
    :param data: JSON 원천 데이터, dict
    :return chat_logs: 발언 내용 전문을 2000자 이내로 분할해 담은 리스트, list
    """
    chat_logs, chats, text_len = [], [], 0  # 전체 발언을 담을 리스트, 분할할 발언 묶음, 분할할 발언 묶음의 텍스트 길이
    speaker_id_to_name = {s['id']: s['name'] for s in data.get("speaker", [])}  # 발화자 id-이름 맵 생성

    for u in data.get("utterance", []):
        # '이름: 내용' 형식의 발언 텍스트 생성
        chat = get_chat_string(
            utter = u.get("form"),
            speaker_name = speaker_id_to_name.get(u.get("speaker_id"), "Unknown"),
            is_speaker_moderator = u.get("is_speaker_moderator", False)
        )

        # 분할할 발언 묶음에 발언을 추가할 때마다 총 텍스트 길이 검사
        if text_len + len(chat) <= 2000:  # 발언을 추가해도 길이가 제한을 넘지 않으면 발언 추가
            chats.append(chat)
            text_len += len(chat)
        else:  # 발언을 추가할 시 길이가 제한을 넘으면, 분할 저장 후 새 묶음에 발언 추가
            chat_logs.append('\n'.join(chats))
            chats, text_len = [chat], len(chat)

    if chats:  # 2000자 제한을 채우지 못한 마지막 묶음이 남아 있으면 전체 발언 리스트에 추가
        chat_logs.append('\n'.join(chats))

    return chat_logs

# JSON 파일을 읽고 처리
for d in category_dirs:
    category_path = os.path.join(parent_dir, d)
    org_json_files = glob.glob(os.path.join(category_path, "*.json"))

    for org_json_path in org_json_files:
        print("reading file:", org_json_path)
        with open(org_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            meeting_overview = get_meeting_overview_string(data)  # 데이터로부터 회의 개요 텍스트를 추출
            meeting_logs = get_meeting_chat_logs(data)  # 데이터로부터 2000자 이내의 발언을 묶은 리스트를 추출
        break
    break

print('\n'.join(meeting_logs))  # 변환한 발언 내용 텍스트를 출력하여 확인

# Gemma2 프롬프트 설정 및 요청
# 공통 프롬프트(요청 사항 및 답변 예시) 작성
common_prompt = [{
    'role': 'user',
    'content': "주어진 발언 내용을 읽고, **주어진 답변 예시와 같은 형식**으로 현재 대화하고 있는 **주제(주요 안건)**와 "
               "**축약한 주요 발언 내용(발언자 누구인지 반드시 포함)**을 정리해 돌려줘. 중요하지 않은 발언은 언급하지 말고, "
               "마크다운 없이 간결하게."
}, {
    'role': 'user',
    'content': """
        1. 답변 예시
        - 안건: 지소미아 조건부 연장 둘러싼 논쟁
        - 주요 발언:
            - DG0001(사회자): 지소미아 종료 6시간 전에 조건부 연장 발표 후에도, 일본은 한국이 항복할 때까지 협상조차 안 한다는 태도를 강화하며 완벽한 승리를 주장하는 등 논리적 모순을 보이고 있다.
            - DG0006: 지소미아와 수출 규제 사이의 관계, 두 국가 간 협상 원칙이 모두 무너지고 있는 상황이다. 일본은 한국의 항복을 강요하는 '퍼펙트 게임'을 추구하고 있다는 비판을 받고 있다.
    """
}]
# 발언 묶음 별로 Gemma2에게 프롬프팅 시도, 공통 프롬프트와 발언 묶음을 함께 전달
for i, log in enumerate(meeting_logs):
    print(f"발언 내용 ({i+1}/{len(meeting_logs)})")
    messages = common_prompt + [{
        'role': 'user',
        'content': f"2. 발언 내용 ({i + 1}/{len(meeting_logs)})\n" + log
    }]

    print("Gemma2 is thinking about your question. This might take a while...")
    response = ollama.chat(model='gemma2:9b', messages=messages)

    print(response['message']['content'])  # Gemma2의 응답 출력
