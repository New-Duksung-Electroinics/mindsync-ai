#!/bin/bash

# 1. .env 생성
echo "⚙️ Setting .env file..."
cp /app/.env.template /app/.env
sed -i "s|REPLACE_WITH_GEMINI_API_KEY|${GEMINI_API_KEY}|g" /app/.env
sed -i "s|REPLACE_WITH_MONGO_URI|${MONGO_URI}|g" /app/.env
chmod 400 /app/.env

# 2. 테스트 데이터 삽입 (이미 존재 시 건너뜀)
echo "📦 Checking test data..."
PYTHONPATH=/app python /app/Prompting/scripts/insert_test_data.py

# 3. FastAPI 서버 실행
echo "🚀 Starting FastAPI server..."
exec uvicorn Prompting.main:app --host 0.0.0.0 --port 8000
