# database.py
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql+mysqlconnector://root:380956aa@localhost:3306/attendance_system"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

def connect():
    return engine.connect()
