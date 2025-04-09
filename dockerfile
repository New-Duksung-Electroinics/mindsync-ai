# 1. Python 3.9 기반 이미지 사용
FROM python:3.9

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. .env.template을 컨테이너 내부로 복사 (실행 시 직접 .env 생성하도록 설정 필요)
COPY .env.template /app/.env.template

# 4. 의존성 파일 복사 및 설치
COPY ./Prompting/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. FastAPI 앱 및 스크립트 복사
COPY ./Prompting /app/Prompting
COPY ./scripts /app/scripts

# 6. entrypoint.sh 복사 및 실행 권한 부여
COPY ./Prompting/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 7. entrypoint 실행
CMD ["/app/entrypoint.sh"]