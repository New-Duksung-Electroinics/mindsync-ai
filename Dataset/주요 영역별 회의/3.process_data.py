"""
AI Hub의 [주요 영역별 회의] 라벨링 데이터(JSON)을 전처리하여 원천 데이터셋 구축하기

주요 기능:
1. JSON 파일의 메타데이터 수정:
   - 주요 정보(title, date, speaker_num)만 추출
   - metadata의 type, domain 속성을 결합하여 'keyword'로 저장
   - metadata의 topic 속성을 별도 속성 'topic'으로 저장

2. 발화자(speaker) 데이터 수정:
   - 주요 정보(id, name)만 추출
   - 발화자의 역할(role) 정보는 사회자 여부만 확인하여 'isModerator' 속성으로 저장

3. 한국어 발화(utterance) 데이터 전처리:
   - 주요 정보(id, speaker_id, isIdiom)만 추출
   - 발화자의 역할 정보(speaker_role)도 사회자 여부만 확인하여 'is_speaker_moderator' 속성으로 저장
   - 발화 내용(form)에서 특수기호, 불필요한 환경 정보, 괄호 등을 제거
   - (한글)/(영어 또는 숫자) 형식의 이중 표현을 찾아 더 적절한 표현을 선택
     - analysis/ko_to_eng.py와 analysis/ko_to_num.py를 활용한 변환 규칙 적용
     - 변환 규칙 데이터에 없는 경우 영어 또는 숫자 표현을 우선 선택

4. 전처리된 데이터를 새로운 JSON 파일로 저장
"""
import pandas as pd
import re
import json
import os
import glob

class UtteranceProcessor:
    def __init__(self):
        """
        UtteranceProcessor는 발화 데이터 전처리를 위한 클래스.
        초기화 시 한글-영어 및 한글-숫자 변환 정보가 담긴 맵을 생성.
        """
        print("한글-영어 변환 맵 생성=================")
        self.eng_ko_word_map = self.__get_word_map_from_csv__("analysis/ko_to_eng_map.csv")
        print("한글-숫자 변환 맵 생성=================")
        self.num_ko_word_map = self.__get_word_map_from_csv__("analysis/ko_to_num_map.csv")

    def __get_word_map_from_csv__(self, csv_file_path):
        """
        주어진 CSV 파일에서 한글 표현과 변환 여부를 매핑하여 딕셔너리로 반환하는 메소드.

        :param csv_file_name: CSV 파일 경로, str
        :return word_dict: 한글 표현과 변환 여부가 매핑된 단어 맵, dict
        """
        df = pd.read_csv(csv_file_path)
        print(f"[CSV DF] 단어 쌍 수:{len(df)}\n")

        df = df[['kor', 'to_convert']].drop_duplicates()
        print(f"[중복 제거 후 DF] 단어 쌍 수:{len(df)}\n")

        word_dict = {row['kor']: row['to_convert'] for index, row in df.iterrows()}
        return word_dict

    def __choose_better_expression__(self, kor, eng_or_num):
        """
         한글과 영어/숫자 표현 중 더 적절한 표현을 선택하는 메소드.

        :param kor: 한글 표현, str
        :param eng_or_num: 영어 또는 숫자 표현, str
        :return: 선택된 표현, str
        """
        # 전문 용어 구분을 위한 특수 기호 @ 제거
        kor = kor.replace('@', '')
        eng_or_num = eng_or_num.replace('@', '')

        # 단어 맵을 통해 단어 변환 여부 확인
        to_convert = self.num_ko_word_map.get(kor, self.eng_ko_word_map.get(kor, None))

        # 단어 맵에 존재하지 않는 표현일 시
        if to_convert is None:
            to_convert = True  # 영어 또는 숫자 표현으로 변환하는 것을 Default로
            # print(f"Can't Find '{kor}' from Word Map!")
            # print(f"Choose '{eng_or_num}' instead of '{kor}' as Default.")

        # 변환 여부에 따라 선택된 값 반환
        return eng_or_num if to_convert else kor

    def process_form(self, text):
        """
        주어진 발화 내용을 정규 표현식을 사용하여 전처리하는 메소드.
        - 한글/영어 또는 한글/숫자 변환
        - 전문 용어 표기 제거
        - 불필요한 괄호 및 공백 제거

        :param text: 발화 내용, str
        :return: 전처리된 발화 내용, str

        """
        term_pattern = r"\(@([^)]+)\)"  # 전문 용어 정규 표현식
        two_words_pattern = r"\(([^()/]+)\)/\(([^()/]+)\)"  # 한글/영어 또는 한글/숫자 이중 표기 정규 표현식
        environment_pattern = r"/\([^)]+\)"  # 주변 환경 정규 표현식

        # 한글-영어/숫자 이중 표기 패턴 찾기 (예:'(한 달)/(1달)', '(오이시디)/(oecd)')
        two_words_match = re.findall(two_words_pattern, text)
        for (kor, eng_or_num) in two_words_match:
            # 한글과 영어/숫자 중 적절한 단어 선택 (+idiom 예외 처리)
            chosen_word = kor if eng_or_num == 'idiom' else self.__choose_better_expression__(kor, eng_or_num)
            text = text.replace(f"({kor})/({eng_or_num})", chosen_word)  # 이중 표기를 선택한 단어로 대체

        # 전문 용어 구분을 위한 특수 기호 @ 제거
        term_match = re.findall(term_pattern, text)
        for term in term_match:
            text = text.replace(f"(@{term})", term)

        # 주변 환경 표기 제거 (예: '/(noise)', '/(bgm)')
        text = re.sub(environment_pattern, "", text)

        # 불필요한 괄호 및 공백 제거
        text = text.replace('(', '').replace(')', '').replace('  ', ' ')
        return text

# UtteranceProcessor 객체 생성
utter_processor = UtteranceProcessor()

# 원본 데이터와 처리 후 저장할 parent 경로 설정
org_parent_dir = "./original"
new_parent_dir = "./processed"

# 하위 디렉터리(카테고리)별 JSON 파일 처리
category_dirs = os.listdir(org_parent_dir)
for d in category_dirs:
    org_category_path = os.path.join(org_parent_dir, d)  # 원본 데이터 경로
    new_category_path = os.path.join(new_parent_dir, d)  # 새로 저장할 경로
    if not os.path.exists(new_category_path):  # 새로 저장할 경로 없으면 생성(카테고리 디렉터리)
        os.makedirs(new_category_path)

    # 디렉토리에서 JSON 파일 목록 가져와 하나씩 처리
    org_json_files = glob.glob(os.path.join(org_category_path, "*.json"))
    for org_json_path in org_json_files:
        print("reading file:", org_json_path)
        with open(org_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            org_metadata = data.get("metadata", {})

            # 메타데이터 전처리
            metadata = {
                "title": org_metadata.get("title"),
                "date": org_metadata.get("date"),
                "speaker_num": org_metadata.get("speaker_num")
            }
            keyword = [org_metadata.get("domain")]  # 키워드 정보에 메타 데이터의 domain 추가
            if (type := org_metadata.get("type")):  # 메타 데이터의 type 값이 존재하면 키워드 정보에 추가
                keyword.append(type)
            topic = org_metadata.get("topic")  # 메타 데이터의 topic을 따로 관리

            # 발화자 정보 전처리
            speaker = [{
                "id": sp.get("id"),
                "name": sp.get("name"),
                "isModerator": sp.get("role") == "사회자"
            } for sp in data.get("speaker", [])]

            # 발화 정보 처리
            utterance = [{
                "id": ut.get("id"),
                "speaker_id": ut.get("speaker_id"),
                "is_speaker_moderator": ut.get("speaker_role") == "사회자",
                "form": utter_processor.process_form(ut.get("form", "")),  # 발화 내용 전처리
                "isIdiom": ut.get("isIdiom")
            } for ut in data.get("utterance", [])]

            # 새로 저장할 데이터 형식
            new_data = {
                "metadata": metadata,
                "keyword": keyword,
                "topic": topic,
                "speaker": speaker,
                "utterance": utterance
            }

        # 처리된 데이터를 새 JSON 파일로 저장
        new_json_path = os.path.join(new_category_path, os.path.basename(org_json_path))
        with open(new_json_path, 'w', encoding="utf-8") as f:
            json.dump(new_data, f, indent='\t', ensure_ascii=False)
