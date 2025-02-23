from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from database import connect
from datetime import datetime
import pandas as pd
from fastapi.responses import FileResponse
import os

router = APIRouter()

# 출석 요청 스키마
class Attendance(BaseModel):
    student_id: int
    status: str  # 출석, 지각, 결석 등

# ✅ 출석 체크 API
@router.post("/attendance")
def mark_attendance(attendance: Attendance):
    conn = connect()
    try:
        query = text("""
            INSERT INTO attendance (student_id, date, status, check_in_time)
            VALUES (:student_id, :date, :status, :check_in_time)
        """)
        conn.execute(query, {
            "student_id": attendance.student_id,
            "date": datetime.now().date(),
            "status": attendance.status,
            "check_in_time": datetime.now().time()
        })
        conn.commit()
        return {"message": "✅ 출석 체크 완료!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ✅ 전체 출석 현황 조회
@router.get("/attendance/daily")
def get_daily_attendance():
    conn = connect()
    try:
        query = text("SELECT student_id, date, status, check_in_time FROM attendance WHERE date = :date")
        result = conn.execute(query, {"date": datetime.now().date()}).fetchall()

        attendance_list = [{
            "student_id": row[0],
            "date": str(row[1]),
            "status": row[2],
            "check_in_time": str(row[3])
        } for row in result]

        return {"attendance": attendance_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ✅ 출석 통계 조회
@router.get("/attendance/statistics")
def get_attendance_statistics():
    conn = connect()
    try:
        query = text("""
            SELECT 
                student_id,
                COUNT(*) AS total_days,
                SUM(CASE WHEN status = '출석' THEN 1 ELSE 0 END) AS attendance_days,
                SUM(CASE WHEN status = '지각' THEN 1 ELSE 0 END) AS tardy_days,
                SUM(CASE WHEN status = '결석' THEN 1 ELSE 0 END) AS absent_days,
                ROUND(SUM(CASE WHEN status = '출석' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS attendance_rate
            FROM attendance
            GROUP BY student_id;
        """)
        result = conn.execute(query).fetchall()

        statistics = [{
            "student_id": row[0],
            "total_days": row[1],
            "attendance_days": row[2],
            "tardy_days": row[3],
            "absent_days": row[4],
            "attendance_rate": row[5]
        } for row in result]

        return {"statistics": statistics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ✅ 출석 리포트 다운로드 (Excel)
@router.get("/attendance/report/excel")
def download_attendance_excel():
    conn = connect()
    try:
        query = text("SELECT * FROM attendance")
        result = conn.execute(query).fetchall()

        data = [{
            "attendance_id": row[0],
            "student_id": row[1],
            "date": str(row[2]),
            "status": row[3],
            "check_in_time": str(row[4])
        } for row in result]

        df = pd.DataFrame(data)
        file_path = "attendance_report.xlsx"
        df.to_excel(file_path, index=False)

        return FileResponse(path=file_path, filename="attendance_report.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# ✅ 출석 리포트 다운로드 (PDF) — 선택사항
@router.get("/attendance/report/pdf")
def download_attendance_pdf():
    from fpdf import FPDF

    conn = connect()
    try:
        query = text("SELECT * FROM attendance")
        result = conn.execute(query).fetchall()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Attendance Report", ln=True, align='C')

        for row in result:
            pdf.cell(200, 10, txt=f"Student ID: {row[1]}, Date: {row[2]}, Status: {row[3]}", ln=True)

        file_path = "attendance_report.pdf"
        pdf.output(file_path)

        return FileResponse(path=file_path, filename="attendance_report.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
