from database import connect

try:
    connection = connect()
    print("✅ DB 연결 성공!")
    connection.close()
except Exception as e:
    print("❌ DB 연결 실패:", e)
