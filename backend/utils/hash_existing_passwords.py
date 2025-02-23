import sys
import os
from sqlalchemy import text
from database import connect
from password_utils import hash_password  # ✅ 파일명 변경 반영

# 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def encrypt_existing_passwords():
    conn = connect()
    try:
        # ✅ text() 사용
        query = text("SELECT user_id, password FROM users")
        users = conn.execute(query).fetchall()

        for user in users:
            user_id, plain_password = user
            hashed_password = hash_password(plain_password)

            # ✅ 업데이트 쿼리도 text() 사용
            update_query = text("UPDATE users SET password = :password WHERE user_id = :user_id")
            conn.execute(update_query, {"password": hashed_password, "user_id": user_id})

        conn.commit()
        print("✅ 모든 비밀번호가 암호화되었습니다.")
    except Exception as e:
        print("❌ 암호화 실패:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    encrypt_existing_passwords()
