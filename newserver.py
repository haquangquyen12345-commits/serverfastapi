from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
# [MỚI] Thêm thư viện để cấp phép cho trình duyệt truy cập API
from fastapi.middleware.cors import CORSMiddleware 

# =====================================================================
# 1. CẤU HÌNH KẾT NỐI POSTGRESQL (GIỮ NGUYÊN)
# =====================================================================
DATABASE_URL = "postgresql://postgres:hqqbg1234@127.0.0.1:5432/duaniot"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =====================================================================
# 2. ĐỊNH NGHĨA BẢNG TRONG DATABASE (GIỮ NGUYÊN)
# =====================================================================
class SensorRecord(Base):
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    lux = Column(Float, nullable=False)                
    button = Column(Integer, nullable=False)           
    timestamp = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

# =====================================================================
# 3. KHỞI TẠO FASTAPI VÀ CẤU TRÚC JSON
# =====================================================================
app = FastAPI(title="IOT Server - PostgreSQL")

# [MỚI] CẤU HÌNH CORS: Cho phép trang Web (Frontend) gọi vào Server này
# Nếu không có đoạn này, trình duyệt sẽ chặn không cho Web lấy dữ liệu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép tất cả các địa chỉ (bao gồm Live Server của Tài)
    allow_credentials=True,
    allow_methods=["*"], # Cho phép GET, POST, v.v.
    allow_headers=["*"],
)

class SensorData(BaseModel):
    lux: float
    button: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================================
# 4. CÁC CỔNG DỮ LIỆU (API ENDPOINTS)
# =====================================================================

# --- CỔNG 1: NHẬN DỮ LIỆU TỪ ESP32 (GIỮ NGUYÊN) ---
@app.post("/api/data")
async def receive_data(data: SensorData, db: Session = Depends(get_db)):
    new_record = SensorRecord(
        lux=data.lux,
        button=data.button,
        timestamp=datetime.now()
    )
    
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    print("=" * 40)
    print(f" ĐÃ LƯU VÀO DATABASE THÀNH CÔNG:")
    print(f" -> Độ rọi  : {data.lux} Lux")
    print(f" -> Nút nhấn: {data.button}")
    print(f" -> ID bản ghi: {new_record.id}")
    print("=" * 40)
    
    return {"status": "success", "message": "Đã lưu vào PostgreSQL"}

# --- [MỚI] CỔNG 2: XUẤT DỮ LIỆU CHO TRANG WEB (API GET) ---
@app.get("/api/data")
async def get_sensor_data(db: Session = Depends(get_db)):
    # Lấy 30 bản ghi mới nhất từ Database, sắp xếp ID từ lớn đến bé
    records = db.query(SensorRecord).order_by(SensorRecord.id.desc()).limit(30).all()
    
    # Trả về danh sách đã được định dạng để Web dễ đọc
    return [
        {
            "id": r.id,
            "lux": r.lux,
            "button": r.button,
            "timestamp": r.timestamp.strftime("%H:%M:%S") # Định dạng lại thời gian cho đẹp
        } for r in records
    ]
