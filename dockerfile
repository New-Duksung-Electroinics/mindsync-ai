# 1. Python 3.10 기반 이미지 사용
FROM python:3.9

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. .env.template을 컨테이너 내부로 복사 (EC2에서 이 파일을 수정해 직접 .env 생성)
COPY .env.template /app/.env.template

# 5. 의존성 파일 복사 및 설치
COPY ./Prompting/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. FastAPI 앱 코드 복사
COPY ./Prompting /app/Prompting

# 7. Uvicorn 실행 (reload 포함)
CMD ["uvicorn", "Prompting.main:app", "--reload"]
