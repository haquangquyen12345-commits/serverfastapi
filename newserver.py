import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Smart Home API")

# Mở cửa CORS cho Live Server (Giữ nguyên của Tài)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "dbname": "duaniot",
    "user": "postgres",
    "password": "hqqbg1234",
    "host": "127.0.0.1"
}

class SensorData(BaseModel):
    lux: float

# =========================================================
# CỔNG 1: NHẬN DỮ LIỆU TỪ ESP32 (Đã ghép thêm Cảnh báo của bạn)
# =========================================================
@app.post("/api/data")
async def save_data(data: SensorData):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 1. Lưu số liệu
        insert_query = "INSERT INTO sensor_data (lux, timestamp) VALUES (%s, %s)"
        cursor.execute(insert_query, (data.lux, datetime.now()))
        
        # 2. Kiểm tra ngưỡng (Logic của Quyền)
        if data.lux > 100.0:
            insert_alarm_query = "INSERT INTO alarms (alert_type, is_resolved) VALUES (%s, %s)"
            cursor.execute(insert_alarm_query, (f"Quá sáng: {data.lux} Lux", False))
            
        conn.commit()
        return {"message": "Đã lưu thành công!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# =========================================================
# CỔNG 2: XUẤT 30 DỮ LIỆU CHO WEB VẼ BIỂU ĐỒ (Của Tài - Đã sửa lỗi tên cột)
# =========================================================
@app.get("/api/data")
async def get_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # ĐÃ SỬA: Dùng cột 'timestamp' cho khớp với Database của Quyền
    query = "SELECT lux, timestamp FROM sensor_data ORDER BY id DESC LIMIT 30"
    cursor.execute(query)
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Định dạng lại dữ liệu
    # Dùng [::-1] để đảo ngược list (để trên biểu đồ, điểm cũ nằm bên trái, điểm mới nằm bên phải)
    formatted_data = [
        {
            "lux": r[0], 
            "timestamp": r[1].strftime("%d/%m %H:%M:%S") if r[1] else "N/A" 
        } for r in records
    ][::-1] 
    
    return formatted_data
