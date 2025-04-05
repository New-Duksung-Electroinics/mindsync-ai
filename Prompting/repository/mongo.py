from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 로드
MONGO_URI = os.getenv("MONGO_URI")  # 환경 변수에서 mongo db uri 읽기
MONGO_DB_NAME = "mindsync-fe"

client = AsyncIOMotorClient(MONGO_URI)
db: Database = client[MONGO_DB_NAME]