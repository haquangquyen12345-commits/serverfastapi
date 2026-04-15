import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel
# [PHẦN THÊM MỚI] - Thư viện để cấp phép cho trình duyệt truy cập
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

# [PHẦN THÊM MỚI] - Cấu hình CORS
# Giúp file Web (Live Server) có thể gọi được vào Server (Uvicorn)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thông tin kết nối (Giữ nguyên của bạn cùng nhóm)
DB_CONFIG = {
    "dbname": "duaniot",
    "user": "postgres",
    "password": "hqqbg1234",
    "host": "127.0.0.1"
}

class SensorData(BaseModel):
    lux: float

# =====================================================================
# CỔNG NHẬN DỮ LIỆU TỪ ESP32 (GIỮ NGUYÊN CỦA BẠN CÙNG NHÓM)
# =====================================================================
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

# =====================================================================
# [PHẦN THÊM MỚI] - CỔNG XUẤT DỮ LIỆU CHO WEB (API GET)
# =====================================================================
@app.get("/api/data")
async def get_data():
    # 1. Kết nối vào DB
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 2. Lấy 30 bản ghi mới nhất
    # Lưu ý: Tài hãy bảo bạn cùng nhóm đảm bảo bảng 'sensor_data' có cột thời gian (ví dụ: created_at)
    query = "SELECT lux, created_at FROM sensor_data ORDER BY id DESC LIMIT 30"
    cursor.execute(query)
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # 3. Định dạng lại dữ liệu để gửi cho file Web
    return [
        {
            "lux": r[0], 
            "timestamp": r[1].strftime("%H:%M:%S") if r[1] else "N/A"
        } for r in records
    ]
