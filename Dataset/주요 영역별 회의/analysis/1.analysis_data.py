"""
AI Hub의 [주요 영역별 회의] 라벨링 데이터(JSON) 분석

- 주요 데이터 항목 분석: 메타데이터(metadata), 발화자(speaker), 발화 내용(utterance)
- 분석 결과 중 몇 가지는 후처리를 위해 CSV 파일 저장:
    - 발화자의 occupation(직업) 값 분포
    - 한글 전사된 숫자 및 영어 값의 분포
"""

import pandas as pd
import json
import os
import glob

# JSON 파일이 저장된 디렉토리 경로
json_dir = "./original"

# 하위 디렉토리 읽어오기
category_dirs = os.listdir(json_dir)

# 모든 JSON 파일 경로를 저장할 리스트 초기화
json_files = []
for d in category_dirs:
    # 각 하위 디렉토리 경로 생성
    category_dir_path = os.path.join(json_dir, d)

    # 하위 디렉토리에서 JSON 파일 목록 가져오기
    category_json_files = glob.glob(os.path.join(category_dir_path, "*.json"))

    # 해당 디렉토리의 JSON 파일을 json_files 리스트에 추가
    json_files += category_json_files


# 데이터를 저장할 리스트 초기화
metadata_list = []  # metadata 정보를 저장할 리스트
speaker_list = []  # speaker 정보를 저장할 리스트
h_to_n_list = []  # 한글->숫자 전사 정보를 저장할 리스트
h_to_e_list = []  # 한글->영어 전사 정보를 저장할 리스트
term_list = []  # 전문용어 정보를 저장할 리스트

# 각 JSON 파일을 반복 처리
for file in json_files:
    print("reading file:", file)  # 현재 읽고 있는 파일 출력
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)  # JSON 파일 읽기

        # metadata 데이터 수집
        metadata = data.get("metadata", {})
        metadata_list.append(metadata)

        # speaker 데이터 수집
        for speaker in data.get("speaker", []):
            speaker_list.append(speaker)

        # utterance 데이터 수집
        for utterance in data.get("utterance", []):
            hanguel_to_english = utterance.get("hangeulToEnglish", [])  # 한글-영어 전사 정보
            hanguel_to_number = utterance.get("hangeulToNumber", [])  # 한글-숫자 전사 정보
            term = utterance.get("term", [])  # 전문용어 정보

            # 한글-영어, 한글-숫자 정보 및 전문용어 리스트에 추가
            if hanguel_to_english:
                h_to_e_list += hanguel_to_english
            if hanguel_to_number:
                h_to_n_list += hanguel_to_number
            if term:
                term_list += term

# 각 데이터를 Pandas DataFrame으로 변환
metadata_df = pd.DataFrame(metadata_list)
speaker_df = pd.DataFrame(speaker_list)
hanguel_to_number_df = pd.DataFrame(h_to_n_list)
hanguel_to_english_df = pd.DataFrame(h_to_e_list)
term_df = pd.DataFrame(term_list)

print()  # 출력 구분을 위한 빈 줄 추가

# 1차 분석: 각 데이터프레임에 대해 고유값 및 값 분포 분석

print("Metadata 분석 ===================================")
print(metadata_df.nunique())  # 고유값 개수
print()
print(metadata_df.value_counts())  # 값 분포
print()

print("\nSpeaker 분석 ===================================")
print(speaker_df.nunique())  # 고유값 개수
print()
print(speaker_df["occupation"].value_counts())  # occupation 값 분포
print()
print(speaker_df["role"].value_counts())  # role 값 분포
print()

print("\nUtterance-HanguelToNumber 분석 ===================================")
print(hanguel_to_number_df.nunique())  # 고유값 개수
print()

print("\nUtterance-HanguelToEnglish 분석 ===================================")
print(hanguel_to_english_df.nunique())  # 고유값 개수
print()


# 2차 분석: 발화자 직업 및 한글 전사 정보의 고유값 분포 확인 및 CSV 저장
keys = ["media", "communication", "type", "domain", "organization"]
for k in keys:
    print(f"<{k}>")
    print(metadata_df[k].value_counts()) # 각 항목의 고유값 분포 출력
print()

# 발화자의 occupation의 고유값 분포 csv로 저장
speaker_df["occupation"].value_counts().to_csv('speaker_occupation_value_counts.csv', encoding="utf-8-sig", header=True)

# 발화내용 중 한글 전사된 숫자 정보 고유값 분포 csv 저장
hanguel_to_number_df[["hangeul", "number"]].value_counts().to_csv('ko_to_num_value_counts.csv', encoding="utf-8-sig", header=True)

# 발화내용 중 한글 전사된 영어 정보 고유값 분포 csv 저장
hanguel_to_english_df[["hangeul", "english"]].value_counts().to_csv('ko_to_eng_value_counts.csv', encoding="utf-8-sig", header=True)
