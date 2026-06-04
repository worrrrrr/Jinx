# ใช้ Python 3.10 เป็นฐาน
FROM python:3.10-slim

# ตั้งค่า Working Directory
WORKDIR /app

# ติดตั้ง System Dependencies ที่จำเป็นสำหรับ Library เฉพาะทาง
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# คัดลอกไฟล์ requirements.txt และติดตั้ง Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมดเข้า Container
COPY . .

# สร้างโฟลเดอร์สำหรับเก็บ Log และ Database เฉพาะกิจ
RUN mkdir -p logs data/storage

# ตั้งค่า Environment Variables เบื้องต้น
ENV PYTHONUNBUFFERED=1
ENV JINX_ENV=production

# เปิด Port สำหรับ FastAPI
EXPOSE 8000

# รัน API Server เป็นโปรแกรมหลัก
CMD ["python", "api_server.py"]
