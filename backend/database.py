from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import logging

# ✅ 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ 데이터베이스 URL
DATABASE_URL = "mysql+mysqlconnector://root:380956aa@localhost:3306/attendance_system"

# ✅ SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ✅ 메타데이터 객체
metadata = MetaData()

# ✅ 세션 메이커 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ DB 연결 함수
def connect():
    try:
        connection = engine.connect()
        logger.info("✅ 데이터베이스 연결 성공")
        return connection
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {e}")
        return None

# ✅ 세션 가져오기 함수
def get_session():
    try:
        session = SessionLocal()
        logger.info("✅ 세션 생성 성공")
        return session
    except Exception as e:
        logger.error(f"❌ 세션 생성 실패: {e}")
        return None
