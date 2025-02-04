"""
AI Hub의 [주요 영역별 회의] 라벨링 데이터(JSON)의 본격적인 텍스트 처리 전 사전 작업
데이터셋에 사용된 영어 표현과 이를 한글로 전사한 텍스트를 비교하여 적절한 표기 방식을 결정

- 한글 텍스트와 영어 표기 간의 변환 규칙은 다음과 같음:
    - idiom으로 분류된 회의 관용어는 예외 처리            -> 한글 (예: 회의를 재개합니다.)
    - 한글 표기가 익숙한 특수 용어는 예외 처리             -> 한글 (예: 코로나)
    - 알파벳 대문자로만 이루어진 용어는 약어로 간주         -> 영어 (예: OECD)
    - 숫자와 알파벳이 조합된 표현은 약어나 전문용어로 간주   -> 영어 (예: G7)
    - 알파벳을 그대로 읽는 용어                         -> 영어 (예: imf = 아이엠에프)
    - 그 외                                         -> 한글
"""
import re
from itertools import product
import csv

# 알파벳에 해당하는 한글 발음 대응 사전
alphabet_to_ko_pron = {
    "A": "에이",
    "B": "비",
    "C": ["씨", "시"],
    "D": "디",
    "E": "이",
    "F": "에프",
    "G": ["쥐", "지"],
    "H": "에이치",
    "I": "아이",
    "J": "제이",
    "K":"케이",
    "L": "엘",
    "M": "엠",
    "N": ["엔", "앤"],
    "O": "오",
    "P": "피",
    "Q": "큐",
    "R": "알",
    "S": "에스",
    "T": "티",
    "U": "유",
    "V": ["브이", "비"],
    "W": "더블유",
    "X": "엑스",
    "Y": "와이",
    "Z": ["지", "제트"],
    "&": "앤"
}

# 예외 처리: 한글로 표기된 특수 용어 리스트 (예: '코로나'는 한글로 사용)
term_exception = ["코로나"]

def isBetterToUseEnglish(kor, eng):
    """
    한글 전사 방식과 영어 표기 중 더 적절한 표현을 결정하는 함수.

    :param kor: 한글 표현, str
    :param eng: 영어 표현, str
    :return: 영어로 표기하는 게 더 적절한지 여부, bool
    """
    # 회의 관용어 예외에 해당하는지 확인
    if eng == 'idiom':
        return False

    # 예외 용어에 해당하는지 확인 (예: '코로나'는 한글로 처리)
    for term in term_exception:
        if term in kor:
            return False

    # 영어 표기 텍스트에서 알파벳만 추출 (불필요한 조사 등을 제거)
    alphabet_only = ''.join(re.findall(r'[a-zA-Z&]', eng))

    if alphabet_only.isupper():  # 모든 문자가 대문자이면 영어로 처리 (=약어로 간주)
        return True

    alphabet_only = alphabet_only.upper()  # 대소문자 구분을 없애기 위해 대문자로 통일

    if re.search(r'[0-9]', eng):
        # 숫자가 섞이면 영어로 처리 (=약어나 전문 용어로 간주)
        return True
    else:
        # 알파벳을 그대로 읽는 용어인지(=약어인지) 검사하여 약어라면 영어로 처리
        alphabet_ko_prons = []
        for ab in alphabet_only:
            if ab in alphabet_to_ko_pron:
                alphabet_ko_prons.append(alphabet_to_ko_pron[ab])

        # 리스트가 아닌 항목은 리스트로 변환
        processed_list = [item if isinstance(item, list) else [item] for item in alphabet_ko_prons]

        # 알파벳 조합으로부터 가능한 모든 한글 발음 조합을 생성
        results = [''.join(combo) for combo in product(*processed_list)]

        # 생성된 조합 중 한글 표기와 일치하는 것이 있으면 영어로 변환
        for r in results:
            if r in kor.replace(' ', ''):
                return True

    return False # 영어로 표기하는 모든 조건에 해당하지 않으면 한글로 처리

# [한글-영어] 표현 쌍 고유값 분석 CSV 파일 읽기
f = open('ko_to_eng_value_counts.csv', 'r', encoding="utf-8-sig")
lines = list(csv.reader(f))
f.close()

# 한글/영어 표기 방식 선택 결과를 저장할 'ko_to_eng_map.csv' 파일 열기
f = open('ko_to_eng_map.csv', 'w', encoding="utf-8-sig", newline='')
wr = csv.writer(f)

# CSV 헤더 작성
wr.writerow(['kor','eng','value_counts','to_convert', 'result'])

# 각 행을 처리하여 한글/영어 변환 여부를 판단하고 결과 기록
for line in lines[1:]:
    to_english = isBetterToUseEnglish(line[0], line[1])  # 한글/영어 변환 여부 결정
    answer = line[1] if to_english else line[0]  # 판단 결과에 따라 변환할 값 선택

    line.append(to_english)  # (영어로의) 변환 여부 기록
    line.append(answer)  # 변환값 기록

    print(line)  # 변환된 결과 출력

    wr.writerow(line)  # 수정한 행 데이터를 CSV에 기록

f.close()
