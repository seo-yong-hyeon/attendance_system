from passlib.context import CryptContext

# bcrypt 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ 비밀번호 해시화 함수
def hash_password(password: str) -> str:
    """
    입력된 비밀번호를 bcrypt를 사용해 해시화합니다.
    """
    return pwd_context.hash(password)

# ✅ 비밀번호 검증 함수
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력된 평문 비밀번호와 해시된 비밀번호를 비교합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)

# ✅ 직접 실행용 (비밀번호 암호화)
if __name__ == "__main__":
    new_password = input("새 비밀번호를 입력하세요: ")
    hashed = hash_password(new_password)
    print("암호화된 비밀번호:", hashed)
