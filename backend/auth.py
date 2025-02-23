from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from database import connect
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

router = APIRouter()

# 비밀번호 해시용
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 요청 데이터 스키마
class UserLogin(BaseModel):
    username: str
    password: str

# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 비밀번호 해시화
def get_password_hash(password):
    return pwd_context.hash(password)

# JWT 토큰 생성
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ 로그인 API
@router.post("/login")
def login(user: UserLogin):
    conn = connect()
    try:
        query = text("SELECT * FROM users WHERE username = :username")
        result = conn.execute(query, {"username": user.username}).fetchone()

        if not result:
            raise HTTPException(status_code=400, detail="❌ 사용자 없음")

        user_id, username, hashed_password, role = result

        if not verify_password(user.password, hashed_password):
            raise HTTPException(status_code=400, detail="❌ 비밀번호 불일치")

        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": username, "role": role})
        return {"access_token": access_token, "token_type": "bearer", "role": role}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
