"""
AI Hub의 [주요 영역별 회의] 라벨링 데이터(JSON)의 본격적인 텍스트 처리 전 사전 작업
데이터셋에 사용된 영어 표현과 이를 한글로 전사한 텍스트를 비교하여 적절한 표기 방식을 결정

- 한글 텍스트와 숫자 표기 간의 변환을 Gemma2 모델에게 맡기기
- 한국어를 잘 처리하는 오픈소스 LLM Gemma2 모델이 둘 중 더 자연스러운 표현을 고르도록 프롬프팅

* 주의 - 이 코드 대신 [2.ko_to_num.py]를 활용할 것:
    - RAM 32GB + RTX 4070 Ti 12GB 환경에서 실행해본 결과, 2B/9B 모델 모두 라벨링에 쓰기에는 지나치게 오랜 시간 소요.
        - 테스트 결과 2B 활용시 최소 6시간, 9B 활용시 최소 9시간 이상 소요되리라 예상됨.
    - 단어 쌍 분류를 한 쌍씩 따로 처리할 때, 최소 189402개의 요청을 처리해야하기 때문
    - 단어 쌍 분류를 병렬로 처리하는 등의 최적화도 어렵다고 판단하여 결국 활용 X
"""
import csv
import ollama

model_size = '9b'  # Gemma2 모델 크기 지정 (2b, 9b)

def chooseBetterNumExpWithGemma2(kor, num):
    """
    한글 전사 방식과 숫자 표기 중 더 적절한 표현 선택을 Gemma2에게 요청하는 함수.
    2B 또는 9B 모델 활용.

    :param kor: 한글 표현, str
    :param num: 숫자 표현, str
    :return: 요청에 따른 Gemma2의 답변, str
    """
    # 적절한 한글/숫자 표현 선택 프롬프팅
    response = ollama.chat(model=f'gemma2:{model_size}', messages=[
        # 태스크 설명 및 사전 지식 제공
        {
            'role': 'user',
            'content': "지금부터 한국어 숫자 표현에서 더 자연스러운 표기방식 고르기를 할 거야. 근데 먼저 숙지해야할 점이 있어. " +
                       "한국어에선 '하나(한)', '둘(두)', '셋(세)'처럼 숫자를 읽는 방식과 '일', '이', '삼'처럼 읽는 방식이 존재하는데 " +
                       "전자의 경우는 발음대로 표기하는 방식이 더 자연스럽고, 후자의 경우는 숫로 표기하는 방식이 더 자연스러워. " +
                       "또 년도, 월, 일, 시, 분과 같은 시간과 날짜와 관련된 표현은 숫자를 기반으로 표현하는 게 더 유용하지. " +
                       "이런 점을 감안하고 다음 문제를 해결해줘. :"
        },
        # 문제 제시 및 답변 형식 제한
        {
            'role': 'user',
            'content': f"한국어 문장에서 '{num}' 단어를 텍스트로 작성할 때, " +
                       f"한국어 발음대로 '{kor}'처럼 표기하는 게 더 자연스러운지, " +
                       f"'{num}'처럼 숫자로 표기하는 게 더 자연스러운지 알려줘. " +
                       "부연설명 없이 둘 중 더 자주 쓰이는 표기 방식만 선택해 답으로 돌려줘."
        }
    ]
    )
    return response['message']['content'].strip()  # 모델의 응답을 반환

def isBetterToUseNumber(kor, num):
    """
    Gemma2의 응답을 바탕으로 한글 전사 방식보다 숫자 표기가 더 적절한지 판별하는 함수.

    :param kor: 한글 표현, str
    :param num: 숫자 표현, str
    :return: 숫자 표기가 더 적절한지 여부, bool
    """
    answer = ""  # Gemma2의 답변을 저장할 변수

    # Gemma2가 형식에 맞는 답변을 줄 때까지 요청을 반복
    while (answer == "") or (not ((elem.isdigit() for elem in answer) or (answer in kor))):
        answer = chooseBetterNumExpWithGemma2(kor, num) # 요청
        print(f"Gemma2's Answer: {answer}") # 답변 출력

    # Gemma2가 숫자 표기를 더 적합하다고 판별했는지 확인하여 결과 전달
    if any(elem.isdigit() for elem in answer):
        return True
    return False

# [한글-숫자] 표현 쌍 고유값 분석 CSV 파일 읽기
f = open('ko_to_num_value_counts.csv', 'r', encoding="utf-8-sig")
lines = list(csv.reader(f))
f.close()

# 한글/숫자 표기 방식 선택 결과를 저장할 'ko_to_eng_map.csv' 파일 열기
f = open(f'ko_to_num_map_by_gemma{model_size}.csv', 'w', encoding="utf-8-sig", newline='')
wr = csv.writer(f)

# CSV 헤더 작성
wr.writerow(['kor','num','value_counts','to_convert', 'result'])

# 각 행을 처리하여 한글/숫자 변환 여부를 판단하고 결과 기록
# total_len = len(lines) - 1  # 데이터 길이 구하기 (헤더 제외하여 1 빼기)
for i, line in enumerate(lines[1:]):
    # print(f"{i+1}/{total_len}")  # 처리 진행도 출력
    to_number = isBetterToUseNumber(line[0], line[1])  # 한글/숫자 변환 여부 결정
    answer = line[1] if to_number else line[0]  # 판단 결과에 따라 변환할 값 선택

    line.append(to_number)  # (숫자로의) 변환 여부 기록
    line.append(answer)  # 변환값 기록

    print(line)  # 변환된 결과 출력

    wr.writerow(line)  # 수정한 행 데이터를 CSV에 기록

f.close()