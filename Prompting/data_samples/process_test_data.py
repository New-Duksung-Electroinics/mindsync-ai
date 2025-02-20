"""
테스트를 위한 회의 채팅 기록 샘플 데이터를 생성하는 데 사용한 코드

Gemini Flash 2.0과 ChatGPT(GPT-4o mini)를 통해 생성한 가상의 회의록 줄글을 바탕으로,
회의 주제, 참여자, 안건별 채팅 기록에 대한 정보를 구조화한 JSON Obejct 파일을 만들어 저장
"""
import re
import json

# 파일 생성을 위한 설정 값
file_name = "context1.txt"  # 읽어올 원본 파일명
json_file_name = "meeting_log_sample_2.json"  # 저장할 json 파일명
created_by = "ChatGPT(GPT-4o mini)"  # 생성자 정보 (ChatGPT(GPT-4o mini) 또는 Gemini Flash 2.0)
moderator_name = "김철수"  # 회의 진행자 이름
split_all_sentences = True  # 모든 발언을 문장 단위로 분리하여 별개의 채팅으로 저장할지 여부

# 정규 표현식 패턴
topic_regex = r"회의 주제: (.*)"    # 회의 주제 추출 패턴
sub_topic_regex = r"안건 ([0-9]): (.*)"   # 안건 추출 패턴
utter_regex = r"([가-힣]{3}): (.*)"   # 발화자-발언 추출 패턴

# 데이터 임시 저장 변수
speaker_names = []  # 발언자 이름 목록
topic = ""  # 회의 주제
contents = []   # 안건별 발언 내용 목록

# 가상의 회의록 텍스트 파일 읽기
with open(file_name, 'r', encoding='utf-8-sig') as f:
    # 회의 주제 추출
    line = f.readline()
    while line:
        topic_match = re.search(topic_regex, line)
        if topic_match:
            topic = topic_match.group(1)
            print("FOUND TOPIC:", topic)
            break
        else:
            line = f.readline()

    # 안건별 발언 내역 추출
    line = f.readline()
    while line:
        sub_topic_match = re.search(sub_topic_regex, line)
        if sub_topic_match:
            step = sub_topic_match.group(1)     # 안건 번호
            sub_topic = sub_topic_match.group(2)    # 안건 제목
            print("FOUND SUB TOPIC:", step, sub_topic)

            utters = []     # 해당 안건의 발언 목록
            line = f.readline()
            while line and (not re.search(sub_topic_regex, line)):  # 다음 안건이 나올 때까지 발언 추출
                utter_match = re.search(utter_regex, line)
                if utter_match:
                    speaker_name = utter_match.group(1)  # 발언자 이름
                    # 발언자 ID 관리 (기존 발언자 목록에 있으면 ID 사용, 없으면 새로 등록)
                    if speaker_name in speaker_names:
                        speaker_id = speaker_names.index(speaker_name)
                    else:
                        speaker_id = len(speaker_names)  # 발언자 ID는 index로 임의 설정
                        speaker_names.append(speaker_name)
                    is_speaker_moderator = (speaker_name == moderator_name)  # 발언자가 진행자인지 여부
                    text = utter_match.group(2)  # 발언 내용
                    if split_all_sentences:  # 발언 내용 문장 단위 분리 O
                        sentences = text.split('. ')
                        for s in sentences:
                            s = s.strip()
                            sentence = s + '.' if s[-1] != '.' else s  # split 때문에 사라진 종결 부호(.) 추가
                            utters.append({
                                "speaker_id": speaker_id,
                                "speaker_name": speaker_name,
                                "is_speaker_moderator": is_speaker_moderator,
                                "msg": sentence
                            })
                            print("FOUND CHAT LOG:", speaker_id, is_speaker_moderator, speaker_name, sentence)
                    else:  # 발언 내용 문장 단위 분리 X
                        utters.append({
                            "speaker_id": speaker_id,
                            "speaker_name": speaker_name,
                            "is_speaker_moderator": is_speaker_moderator,
                            "msg": text
                        })
                        print("FOUND CHAT LOG:", speaker_id, is_speaker_moderator, speaker_name, text)
                line = f.readline()

            # 수집한 정보를 안건별 발언 내용 목록에 추가
            contents.append({
                "step": step,
                "sub_topic": sub_topic,
                "utterance": utters
            })
        else:
            line = f.readline()

# JSON 데이터 구성
metadata = {
    "created_by": created_by,
    "speaker_num": len(speaker_names)
}

speakers = []
for idx, name in enumerate(speaker_names):
    speakers.append({
        "id": idx,
        "name": name,
        "isModerator": name == moderator_name
    })

json_data = {
    "metadata": metadata,
    "topic": topic,
    "speakers": speakers,
    "contents": contents
}

# JSON 파일 저장
with open(json_file_name, 'w', encoding="utf-8") as f:
    json.dump(json_data, f, indent='\t', ensure_ascii=False)
