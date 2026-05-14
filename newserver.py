import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="HUST IoT Smart Home API")

# Cấu hình CORS: Cho phép Web (Live Server) truy cập vào API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thông tin kết nối Database của Tài
DB_CONFIG = {
    "dbname": "duaniot",
    "user": "postgres",
    "password": "hqqbg1234",
    "host": "127.0.0.1"
}

class SensorData(BaseModel):
    lux: float

# =========================================================
# CỔNG 1: NHẬN DỮ LIỆU TỪ ESP32 & KIỂM TRA CẢNH BÁO
# =========================================================
@app.post("/api/data")
async def save_data(data: SensorData):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        # 1. Lưu số liệu ánh sáng
        insert_query = "INSERT INTO sensor_data (lux, timestamp) VALUES (%s, %s)"
        cursor.execute(insert_query, (data.lux, datetime.now()))
        
        # 2. Logic cảnh báo: Nếu quá sáng (>100) thì ghi vào bảng alarms
        if data.lux > 100.0:
            insert_alarm_query = "INSERT INTO alarms (alert_type, is_resolved) VALUES (%s, %s)"
            cursor.execute(insert_alarm_query, (f"Cảnh báo: {data.lux} Lux", False))
            
        conn.commit()
        return {"message": "Dữ liệu đã được ghi vào SQL!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# =========================================================
# CỔNG 2: XUẤT 30 DỮ LIỆU MỚI NHẤT CHO BIỂU ĐỒ
# =========================================================
@app.get("/api/data")
async def get_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "SELECT lux, timestamp FROM sensor_data ORDER BY id DESC LIMIT 30"
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    # Đảo ngược mảng để biểu đồ chạy từ trái sang phải (Cũ -> Mới)
    return [
        {
            "lux": r[0], 
            "timestamp": r[1].strftime("%H:%M:%S") if r[1] else "N/A"
        } for r in records
    ][::-1]

# =========================================================
# CỔNG 3: TRUY XUẤT DỮ LIỆU THEO GIÁ TRỊ LUX CHÍNH XÁC
# =========================================================
@app.get("/api/search")
async def search_data(lux: float):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "SELECT lux, timestamp FROM sensor_data WHERE lux = %s ORDER BY timestamp DESC"
    cursor.execute(query, (lux,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"lux": r[0], "timestamp": r[1].strftime("%d/%m %H:%M:%S")} for r in records]

# =========================================================
# CỔNG 4: BỘ LỌC DỮ LIỆU NHỎ HƠN NGƯỠNG
# =========================================================
@app.get("/api/filter")
async def filter_data(max_lux: float):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "SELECT lux, timestamp FROM sensor_data WHERE lux < %s ORDER BY timestamp DESC LIMIT 100"
    cursor.execute(query, (max_lux,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"lux": r[0], "timestamp": r[1].strftime("%d/%m %H:%M:%S")} for r in records]
