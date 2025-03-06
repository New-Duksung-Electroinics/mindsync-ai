# 1. Python 3.10 기반 이미지 사용
FROM python:3.9

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 복사 및 설치
COPY ./Prompting/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. FastAPI 앱 코드 복사
COPY ./Prompting /app/Prompting

# 5. Uvicorn 실행 (reload 포함)
CMD ["uvicorn", "Prompting.main:app", "--reload", "--host", "0.0.0.0", "--port", "7070"]
