"""
AI Hub의 [주요 영역별 회의] 라벨링 데이터(JSON)의 본격적인 텍스트 처리 전 사전 작업
데이터셋에 사용된 숫자 표현과 이를 한글로 전사한 텍스트를 비교하여 적절한 표기 방식을 결정

- 한글 텍스트와 숫자 표기 간의 변환 규칙은 다음과 같음:
    1순위. 혼동 여지가 적은 확실한 케이스를 먼저 판별
        - 특수 용어 예외                           -> 숫자 (예: 코로나19)
        - 시간 표현 예외                           -> 숫자 (예: 시월 -> 10월, 유월 -> 6월)
        - 한글 텍스트에 오타가 난 경우               -> 숫자 (예: 새 개 -> 3개)
        - 한국어 고유의 숫자 표현                   -> 한글 (예: 너댓, 빵, 나흘)
        - 혼동할 여지가 적은 특수한 서수 키워드       -> 한글 (예: 하나, 한, 둘, 첫)
    2순위. 그 외의 경우, 기수/영어/서수 키워드 기반 판별을 수행
        - 서수 키워드가 포함된 경우              -> 한글 (예: 한 달)
            * 예외: 10 이상의 서수 표현         -> 숫자 (예: 열두살 -> 12살)
        - 기수 키워드가 포함된 경우             -> 숫자 (예: 일 회 -> 1회)
        - 영어 숫자 표현이 포함된 경우          -> 숫자 (예: 쓰리 -> 3)
        - 그 외                             -> 숫자
"""
import csv

def find_common_substring(str1, str2):
    """
    두 문자열간 가장 긴 공통 substring(부분 문자열) 찾는 함수.

    :param str1: 첫 번째 문자열, str
    :param str2: 두 번째 문자열, str
    :return: 가장 긴 공통 부분 문자열, str
    """
    m = len(str1)
    n = len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_length = 0
    end_index = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_length:
                    max_length = dp[i][j]
                    end_index = i

    return str1[end_index - max_length:end_index]

def processNumExceptionExp(kor, num):
    """
    숫자 예외 표현을 감지하고 변환 여부를 결정하는 함수.

    :param kor: 한글 표현, str
    :param num: 숫자 표현, str
    :return (bool, bool): 숫자/한글 표기 예외 해당 여부, tuple
        - 첫번째 bool: 숫자로 표기해야 할 예외에 해당하는지 여부
        - 두번째 bool: 한글로 표기해야 할 예외에 해당하는지 여부
    """

    # 숫자가 포함된 전문 용어 (예: 코로나19)
    term_exception = ["코로나"]
    # 월을 표현하는 단어 중 예외적인 표기 방식을 갖는 단어
    month_exception = ["시월", "유월", "시 월", "유 월"]
    # 한글 전사 텍스트 중 잘못된 표기 (오타) 예외
    typo_exception = [
        "새 개", "여덞", "심삽", "입곱", "쳔", "하는 가지가", "칩실", "삽심삽", "다슷", "내 개", "다 섯"
    ]

    # 숫자로 표기하는 게 더 적절한 예외 표현 처리
    for ex in month_exception + term_exception + typo_exception:
        if ex in kor:
            return True, False  # 숫자 표기를 선택

    # 문맥상 숫자로 바뀌면 어색할 수 있는 서수 표현 (형용사로 쓰이는 서수 표현 등)
    prior_ord_num = ["하나", "한", "첫", "두", "세", "네", "하난데"]
    # 한국어만의 특수한 숫자 표현 -> 숫자로 바꿔도 괜찮으나, 한국어 특성을 위해 한글로 유지할 예외로 처리
    num_count_exception = ["석", "서너", "넉", "여덜", "너댓", "빵", "나흘", "닷새", "댓"]

    # 한글로 표기하는 게 더 적절한 예외 표현 처리
    for ex in prior_ord_num + num_count_exception:
        if ex in kor:
            to_kor = True
            return False, True  # 한글 표기를 선택

    return False, False  # 예외 표현에 해당하지 않음

def chooseBetterNumExpByRule(kor, num):
    """
    한글 전사 방식과 숫자 표기 중 더 적절한 표현을 결정하는 함수.

    한글 표현과 숫자 표현에 대한 적합성을 각각 처리하는 이유는
    두 개 모두 적합한 경우(=케이스 분리가 잘못된 경우)를 분리하여 추가 처리하기 위함.

    다른 숫자 키워드는 혼동할 여지가 비교적 적지만,
    특히 '일', '이' 같은 기수 키워드는 혼동이 자주 발생하는 걸로 확인됨.

    :param kor: 한글 표현, str
    :param num: 숫자 표현, str
    :return (bool, bool): 숫자/한글 표기 적합 여부, tuple
        - 첫번째 bool: 숫자 표기에 적합한지 여부
        - 두번째 bool: 한글 표기에 적합한지 여부
    """
    # 10 이상의 서수 표현이 포함된 경우, 가독성을 위해 다른 조건을 고려하지 않고 숫자 표현 선택
    ord_num_over_ten = ["열", "스물", "스무", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]
    for ont in ord_num_over_ten:
        if ont in kor:
            to_number = True
            return True, False  # 숫자 표현을 선택

    to_kor = False  # 한글 표현 적합 여부
    to_number = False  # 숫자 표현 적합 여부

    # 영어 숫자 표현이나 기수 표현이 포함된 경우 숫자 표현이 적합
    eng_num = [
        "제로", "원", "투", "쓰리", "스리", "포", "파이브", "식스", "쎄븐", "세븐", "에잇", "에이트", "나인",
        "텐", "피프틴", "트웰브"
    ]
    card_num = [
        "영", "공", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구",
        "십", "백", "천", "만", "억", "조", "경", "해"
    ]
    for cn in card_num + eng_num:
        if cn in kor:
            to_number = True  # 숫자 처리에 적합
            break
            # 기수 키워드 일부('일', '이' 등..)가 숫자가 아닌 표현과 혼동될 수 있기 때문에 즉시 return 하지 않고 break
            # 숫자와 한글 모두 적합한 것으로 판단되었을 때는 케이스 분리가 잘못된 것 -> 추가 검사할 여지를 남김

    # 한 자리 서수 표현이 포함된 경우 한글 표현이 적합
    ordNum = ["둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉"]
    for on in ordNum:
        if on in kor:
            to_kor = True  # 한글 표현을 선택 (그러나 영어 표현도 적합 판정일 수 있음)
            return to_number, to_kor # (True, True) 또는 (False, True)

    return to_number, to_kor  # (True, False) 또는 (False, False)

# [한글-숫자] 표현 쌍 고유값 분석 CSV 파일 읽기
f = open('ko_to_num_value_counts.csv', 'r', encoding='utf-8-sig')
lines = list(csv.reader(f))
f.close()

# 한글/숫자 표기 방식 선택 결과를 저장할 'ko_to_eng_map.csv' 파일 열기
f = open('ko_to_num_map.csv', 'w', encoding='utf-8-sig', newline='')
wr = csv.writer(f)

# CSV 헤더 작성
wr.writerow(['kor', 'num', 'value_counts', 'to_convert', 'result'])

# 각 행을 처리하여 한글/숫자 변환 여부를 판단하고 결과 기록
# total_len = len(lines) - 1  # 데이터 길이 구하기 (헤더 제외하여 1 빼기)
for i, line in enumerate(lines[1:]):
    kor = line[0]  # 한글 표현
    num = line[1]  # 숫자 표현

    # 예외 및 특수 표현 여부 검사
    to_number, to_kor = processNumExceptionExp(kor, num)

    if to_kor or to_number:  # 예외 조건에 해당하는 경우
        answer = num if to_number else kor
    else:  # 예외에 포함되지 않으면
        # 한글-숫자 표현 간 공통 부분(예: 조사) 제거
        common_substr = find_common_substring(kor, num)
        kor_sub = kor.replace(common_substr, "").strip()
        num_sub = num.replace(common_substr, "").strip()

        # 공통 부분 제거한 부분 문자열로 숫자/한글 표기 적합성 판단
        to_number, to_kor = chooseBetterNumExpByRule(kor_sub, num_sub)

        if (to_kor or to_number) and not (to_kor and to_number):
            # 특정 케이스로 분리 성공한 경우(= 숫자 또는 한글 표기 적합)
            answer = num if to_number else kor
        else:
            # 정확한 케이스 분리에 실패한 경우(= 둘 다 적합 또는 모두 부적합)
            # 모호한 경우 숫자로 변환하는 것이 의미 전달에 이로우리라 판단.
            to_number = True
            to_kor = False
            answer = num

    line.append(to_number)  # (숫자로의) 변환 여부 기록
    line.append(answer)  # 변환값 기록

    print(line)  # 변환된 결과 출력

    wr.writerow(line)  # 수정한 행 데이터를 CSV에 기록

f.close()
