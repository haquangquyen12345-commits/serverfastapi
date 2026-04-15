import psycopg2
from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()

# Thông tin kết nối
DB_CONFIG = {
    "dbname": "duaniot",
    "user": "postgres",
    "password": "hqqbg1234",
    "host": "127.0.0.1"
}

class SensorData(BaseModel):
    lux: float

@app.post("/api/data")
async def save_data(data: SensorData):
    # 1. Kết nối vào DB đã có sẵn
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 2. Chỉ thực hiện lệnh INSERT vào bảng đã tạo thủ công
    insert_query = "INSERT INTO sensor_data (lux) VALUES (%s)"
    cursor.execute(insert_query, (data.lux,))
    
    # 3. Chốt dữ liệu và đóng kết nối
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"message": "Đã lưu thành công!"}
