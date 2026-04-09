from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime

# =====================================================================
# 1. CẤU HÌNH KẾT NỐI POSTGRESQL (Mở cửa nhà kho)
# =====================================================================
# Cấu trúc: postgresql://[user]:[password]@[host]:[port]/[database_name]
DATABASE_URL = "postgresql://postgres:hqqbg1234@127.0.0.1:5432/duaniot"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =====================================================================
# 2. ĐỊNH NGHĨA BẢNG TRONG DATABASE (SQLAlchemy Model)
# =====================================================================
# Đây là cách chúng ta thiết kế các cột trong cuốn sổ cái
class SensorRecord(Base):
    __tablename__ = "sensor_data" # Tên bảng
    
    id = Column(Integer, primary_key=True, index=True) # Cột số thứ tự (tự tăng)
    lux = Column(Float, nullable=False)                # Cột độ rọi
    button = Column(Integer, nullable=False)           # Cột trạng thái nút
    timestamp = Column(DateTime, default=datetime.now) # Cột thời gian

# Lệnh này sẽ tự động chạy vào PostgreSQL và tạo cái bảng trên nếu nó chưa tồn tại
Base.metadata.create_all(bind=engine)

# =====================================================================
# 3. KHỞI TẠO FASTAPI VÀ CẤU TRÚC JSON
# =====================================================================
app = FastAPI(title="IOT Server - PostgreSQL")

# Đây là định dạng gói hàng mà ESP32 bắt buộc phải tuân thủ khi gửi lên
class SensorData(BaseModel):
    lux: float
    button: int

# Hàm hỗ trợ: Mở kết nối Database khi có khách gọi, xong việc thì tự đóng lại
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================================
# 4. MỞ CỔNG ĐÓN DỮ LIỆU (API Endpoint)
# =====================================================================
@app.post("/api/data")
async def receive_data(data: SensorData, db: Session = Depends(get_db)):
    # Bóc gói hàng JSON và chuyển thành một dòng dữ liệu (Record) chuẩn bị lưu
    new_record = SensorRecord(
        lux=data.lux,
        button=data.button,
        timestamp=datetime.now()
    )
    
    # Ra lệnh cất vào kho và chốt sổ (commit)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    # In ra Terminal để kỹ sư dễ theo dõi
    print("=" * 40)
    print(f" ĐÃ LƯU VÀO DATABASE THÀNH CÔNG:")
    print(f" -> Độ rọi  : {data.lux} Lux")
    print(f" -> Nút nhấn: {data.button}")
    print(f" -> ID bản ghi: {new_record.id}")
    print("=" * 40)
    
    return {"status": "success", "message": "Đã lưu vào PostgreSQL!"}