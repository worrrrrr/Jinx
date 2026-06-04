# ใช้ Python 3.10-slim
FROM python:3.10-slim

# สร้าง User ใหม่เพื่อให้รันบน Hugging Face ได้อย่างปลอดภัย
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# ติดตั้ง Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# คัดลอก requirements และติดตั้ง
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมด
COPY --chown=user . .

# สร้างโฟลเดอร์สำหรับข้อมูล
RUN mkdir -p logs data/storage

# เปิด Port 7860 (Hugging Face Spaces บังคับใช้ port นี้)
EXPOSE 7860

# รัน API Server (ชี้ไปที่ port 7860)
CMD ["python", "api_server.py"]