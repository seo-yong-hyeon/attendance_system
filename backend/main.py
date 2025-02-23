import sys
import os
from fastapi import FastAPI, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# ✅ 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ FastAPI 앱 생성
app = FastAPI()

# ✅ 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ✅ 데이터베이스 URL
DATABASE_URL = "mysql+mysqlconnector://root:380956aa@localhost:3306/attendance_system"

# ✅ SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ 세션 가져오기 함수
def get_session():
    try:
        session = SessionLocal()
        return session
    except Exception as e:
        print(f"❌ 세션 생성 실패: {e}")
        return None

# ✅ 학교 와이파이 IP 대역 설정
ALLOWED_IP_PREFIXES = ["192.168.", "10.0.", "112.184.251."]

# ✅ 로그인 페이지
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ✅ 로그인 처리
@app.api_route("/login", methods=["GET", "POST"], response_class=HTMLResponse)
def login(request: Request, username: str = Form(None), password: str = Form(None)):
    session = get_session()
    if session is None:
        return templates.TemplateResponse("login.html", {"request": request, "error": "❌ 데이터베이스 연결 실패"})

    try:
        query = text("SELECT username, password, role FROM users WHERE username = :username")
        result = session.execute(query, {"username": username}).fetchone()

        if result:
            db_username, db_password, role = result
            if password == db_password:
                if role == 'teacher':
                    return templates.TemplateResponse("teacher_dashboard.html", {"request": request, "username": db_username})
                else:
                    return templates.TemplateResponse("student_dashboard.html", {"request": request, "username": db_username})
            else:
                return templates.TemplateResponse("login.html", {"request": request, "error": "❌ 비밀번호가 일치하지 않습니다."})
        else:
            return templates.TemplateResponse("login.html", {"request": request, "error": "❌ 사용자 없음"})
    finally:
        session.close()

# ✅ 출석 체크 API
@app.post("/attendance")
def mark_attendance(request: Request, username: str = Form(...)):
    client_ip = request.client.host
    print(f"✅ 출석 체크 시도 - IP: {client_ip}, 사용자: {username}")

    if not username:
        raise HTTPException(status_code=400, detail="❌ username 필드가 필요합니다.")

    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    session = get_session()
    try:
        query = text("SELECT user_id FROM users WHERE username = :username")
        result = session.execute(query, {"username": username}).fetchone()

        if result:
            user_id = result[0]

            check_query = text("SELECT * FROM attendance WHERE user_id = :user_id AND date = :current_date")
            existing_attendance = session.execute(check_query, {"user_id": user_id, "current_date": current_date}).fetchone()

            if existing_attendance:
                return {"message": "❗ 이미 출석 처리됨"}

            insert_query = text("""
                INSERT INTO attendance (user_id, date, status, check_in_time)
                VALUES (:user_id, :current_date, '출석', :current_time)
            """)
            session.execute(insert_query, {"user_id": user_id, "current_date": current_date, "current_time": current_time})
            session.commit()

            return {"message": "✅ 출석이 성공적으로 기록되었습니다."}
        else:
            return {"message": "❌ 사용자 없음"}
    finally:
        session.close()

# ✅ 출결 현황 조회 (교사용)
@app.get("/attendance_list", response_class=HTMLResponse)
def view_attendance(request: Request):
    session = get_session()

    try:
        query = text("""
            SELECT a.attendance_id, u.username, a.date, a.status, a.check_in_time
            FROM attendance a
            JOIN users u ON a.user_id = u.user_id
            ORDER BY a.date DESC
        """)
        results = session.execute(query).fetchall()

        return templates.TemplateResponse("attendance_list.html", {"request": request, "records": results})
    finally:
        session.close()

# ✅ 출결 수정 페이지
@app.get("/edit_attendance/{attendance_id}", response_class=HTMLResponse)
def edit_attendance(request: Request, attendance_id: int):
    session = get_session()
    query = text("SELECT * FROM attendance WHERE attendance_id = :attendance_id")
    result = session.execute(query, {"attendance_id": attendance_id}).fetchone()
    session.close()

    if not result:
        raise HTTPException(status_code=404, detail="출결 기록을 찾을 수 없습니다.")

    return templates.TemplateResponse("edit_attendance.html", {
        "request": request,
        "attendance": result
    })

# ✅ 출결 수정 처리
@app.post("/update_attendance/{attendance_id}")
def update_attendance(attendance_id: int, status: str = Form(...), check_in_time: str = Form(...)):
    session = get_session()
    update_query = text("""
        UPDATE attendance
        SET status = :status, check_in_time = :check_in_time
        WHERE attendance_id = :attendance_id
    """)
    session.execute(update_query, {
        "status": status,
        "check_in_time": check_in_time,
        "attendance_id": attendance_id
    })
    session.commit()
    session.close()
    return RedirectResponse(url="/attendance_list", status_code=303)

# ✅ 출결 삭제 처리
@app.delete("/delete_attendance/{attendance_id}")
def delete_attendance(attendance_id: int):
    session = get_session()
    delete_query = text("DELETE FROM attendance WHERE attendance_id = :attendance_id")
    session.execute(delete_query, {"attendance_id": attendance_id})
    session.commit()
    session.close()
    return {"message": "✅ 출결 기록이 삭제되었습니다."}

# ✅ 학생 출결 현황 조회 (학생용)
@app.get("/my_attendance", response_class=HTMLResponse)
def my_attendance(request: Request, username: str = Query(None)):
    if not username:
        raise HTTPException(status_code=400, detail="❌ username 파라미터가 필요합니다.")

    session = get_session()
    try:
        query = text("""
            SELECT date, status, check_in_time
            FROM attendance a
            JOIN users u ON a.user_id = u.user_id
            WHERE u.username = :username
            ORDER BY date DESC
        """)
        results = session.execute(query, {"username": username}).fetchall()

        return templates.TemplateResponse("my_attendance.html", {
            "request": request,
            "records": results,
            "username": username
        })
    finally:
        session.close()

# ✅ 학생 대시보드
@app.get("/student_dashboard", response_class=HTMLResponse)
def student_dashboard(request: Request, username: str = Query(None)):
    if not username:
        raise HTTPException(status_code=400, detail="❌ username 파라미터가 필요합니다.")
    
    return templates.TemplateResponse("student_dashboard.html", {
        "request": request,
        "username": username
    })
