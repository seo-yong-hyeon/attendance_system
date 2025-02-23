from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from utils.password_utils import hash_password
from database import connect
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

# JWT 설정
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 사용자 생성 요청 스키마
class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # student, teacher, admin

# 사용자 응답 스키마
class UserResponse(BaseModel):
    user_id: int
    username: str
    role: str

# ✅ 사용자 생성
@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    conn = connect()
    try:
        hashed_password = hash_password(user.password)

        query = text("""
            INSERT INTO users (username, password, role)
            VALUES (:username, :password, :role)
        """)

        conn.execute(query, {
            "username": user.username,
            "password": hashed_password,
            "role": user.role
        })

        conn.commit()

        user_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

        return {"user_id": user_id, "username": user.username, "role": user.role}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ✅ 사용자 정보 조회
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    conn = connect()
    try:
        query = text("SELECT user_id, username, role FROM users WHERE user_id = :user_id")
        result = conn.execute(query, {"user_id": user_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="사용자 없음")

        return {"user_id": result[0], "username": result[1], "role": result[2]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ✅ 사용자 정보 수정
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    conn = connect()
    try:
        hashed_password = hash_password(user.password)

        query = text("""
            UPDATE users
            SET username = :username, password = :password, role = :role
            WHERE user_id = :user_id
        """)

        conn.execute(query, {
            "username": user.username,
            "password": hashed_password,
            "role": user.role,
            "user_id": user_id
        })

        conn.commit()

        return {"user_id": user_id, "username": user.username, "role": user.role}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ✅ 사용자 삭제
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = connect()
    try:
        query = text("DELETE FROM users WHERE user_id = :user_id")
        result = conn.execute(query, {"user_id": user_id})

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="사용자 없음")

        conn.commit()
        return {"message": "사용자 삭제 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ✅ 모든 사용자 목록 조회
@router.get("/users")
def get_all_users():
    conn = connect()
    try:
        query = text("SELECT user_id, username, role FROM users")
        result = conn.execute(query).fetchall()

        users = [{"user_id": row[0], "username": row[1], "role": row[2]} for row in result]

        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
