---
title: setup_project
tags: [knowledge, vault]
aliases: [setup_project]
---
ได้เลย ทำแบบ wizard ถามทีละชั้น เลือก 1 2 3 ต่อกันไปเรื่อยๆ พร้อมคำแนะนำแต่ละแบบ

เอาไฟล์นี้ไปทับ `setup_project.py` เดิม รัน `python [[setup_project]].py` ได้เลย

### `setup_project.py` เวอร์ชัน Wizard
```python
#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def run(cmd, cwd=None):
    print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode!= 0:
        sys.exit(f"Command failed: {cmd}")

def ask_choice(question, options):
    print(f"\n{question}")
    for i, (key, desc) in enumerate(options.items(), 1):
        print(f"{i}. {key} - {desc}")
    while True:
        choice = input(f"เลือก 1-{len(options)}: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return list(options.keys())[int(choice) - 1]
        print("เลือกใหม่")

def main():
    print("=== BestSystem Project Generator ===")
    project_name = input("ชื่อโปรเจค: ").strip().replace(" ", "-").lower()
    if not project_name:
        sys.exit("ต้องใส่ชื่อโปรเจค")

    pkg = project_name.replace('-', '_')

    # Step 1: เลือกประเภทโปรเจค
    project_type = ask_choice("โปรเจคประเภทไหน:", {
        "API": "FastAPI ทำ REST API ให้ Frontend/Mobile ยิง",
        "AI-Service": "FastAPI + LangChain/Ollama ทำ AI chatbot/RAG",
        "Worker": "Background job ใช้ Celery/RQ รัน cron/queue",
        "CLI": "Command line tool ใช้ Typer"
    })

    # Step 2: เลือก Database
    if project_type in ["API", "AI-Service"]:
        db_type = ask_choice("ใช้ Database อะไร:", {
            "SQLite": "ไฟล์เดียว เริ่มง่ายสุด เหมาะกับ dev/test",
            "PostgreSQL": "Production จริง รองรับ concurrent เยอะ",
            "None": "ไม่ใช้ DB เก็บใน memory/ไฟล์"
        })
    else:
        db_type = "None"

    # Step 3: เลือก Auth
    if project_type in ["API", "AI-Service"] and db_type!= "None":
        auth_type = ask_choice("ระบบ Login:", {
            "JWT": "มาตรฐาน Token 7 วัน Frontend/Mobile ใช้ได้หมด",
            "API-Key": "ง่ายสุด ส่ง header X-API-Key เหมาะ service-to-service",
            "None": "ไม่ต้อง login API public"
        })
    else:
        auth_type = "None"

    # สรุป
    print(f"\n=== สรุป ===")
    print(f"Project: {project_name}")
    print(f"Type: {project_type} | DB: {db_type} | Auth: {auth_type}")
    if input("ยืนยันสร้าง? y/n: ").lower()!= 'y':
        return

    # เริ่มสร้าง
    run(f"uv init {project_name}")
    os.chdir(project_name)
    run("uv python pin 3.11")

    # สร้างโครงสร้าง
    dirs = [f"src/{pkg}/api", f"src/{pkg}/models", f"src/{pkg}/core", "tests", "logs"]
    if db_type!= "None":
        dirs.append("migrations")
    if project_type == "AI-Service":
        dirs.append(f"src/{pkg}/ai")

    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        Path(d, "__init__.py").touch()

    Path("logs/.gitkeep").touch()

    # ติดตั้ง deps
    base = ["fastapi", "uvicorn[standard]", "loguru"]
    dev = ["pytest", "pytest-asyncio", "httpx", "ruff"]

    if db_type == "SQLite":
        base.extend(["sqlmodel", "aiosqlite", "alembic"])
    if db_type == "PostgreSQL":
        base.extend(["sqlmodel", "psycopg2-binary", "alembic"])
    if auth_type == "JWT":
        base.extend(["python-jose[cryptography]", "passlib[bcrypt]"])
    if project_type == "AI-Service":
        base.extend(["langchain", "ollama"])
    if project_type == "Worker":
        base.extend(["celery", "redis"])
    if project_type == "CLI":
        base.extend(["typer[all]"])

    run(f"uv add {' '.join(base)}")
    run(f"uv add --dev {' '.join(dev)}")

    # เขียนไฟล์ core/config.py
    config_content = f'''from pathlib import Path
from loguru import logger

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
{"DATABASE_URL = f'sqlite:///{BASE_DIR}/database.db'" if db_type == "SQLite" else ""}
{"DATABASE_URL = 'postgresql://user:pass@localhost/dbname'" if db_type == "PostgreSQL" else ""}

logger.add(BASE_DIR / "logs/app.log", rotation="10 MB", retention="7 days", level="INFO")

SECRET_KEY = "change-me"
ALGORITHM = "HS256"
'''
    Path(f"src/{pkg}/core/config.py").write_text(config_content)

    # เขียน main.py ตาม type
    if project_type in ["API", "AI-Service"]:
        if db_type!= "None":
            db_py = '''from sqlmodel import SQLModel, create_engine, Session
from.config import DATABASE_URL
engine = create_engine(DATABASE_URL)
def get_session():
    with Session(engine) as session:
        yield session
'''
            Path(f"src/{pkg}/core/db.py").write_text(db_py)

        main_py = f'''from fastapi import FastAPI
from.core.config import logger
{"from.core.db import engine; from sqlmodel import SQLModel" if db_type!= "None" else ""}

app = FastAPI(title="{project_name}")

{"@app.on_event('startup')" if db_type!= "None" else ""}
{"async def startup(): SQLModel.metadata.create_all(engine); logger.info('DB ready')" if db_type!= "None" else ""}

@app.get("/health")
def health():
    return {{"status": "ok"}}
'''
    elif project_type == "CLI":
        main_py = '''import typer
app = typer.Typer()

@app.command()
def hello(name: str):
    print(f"Hello {name}")

if __name__ == "__main__":
    app()
'''
    else: # Worker
        main_py = '''from celery import Celery
app = Celery("worker", broker="redis://localhost:6379")

@app.task
def add(x, y):
    return x + y
'''

    Path(f"src/{pkg}/main.py").write_text(main_py)

    # Test
    test_content = f'''from fastapi.testclient import TestClient
from src.{pkg}.main import app
client = TestClient(app)
def test_health():
    assert client.get("/health").status_code == 200
'''
    Path("tests/test_main.py").write_text(test_content)

    # pyproject.toml scripts
    pyproject = Path("pyproject.toml").read_text()
    if project_type in ["API", "AI-Service"]:
        pyproject += f'\n[project.scripts]\ndev = "uvicorn src.{pkg}.main:app --reload"\ntest = "pytest -v"\n'
    elif project_type == "CLI":
        pyproject += f'\n[project.scripts]\n{pkg} = "src.{pkg}.main:app"\n'
    Path("pyproject.toml").write_text(pyproject)

    # Alembic ถ้าใช้ DB
    if db_type!= "None":
        run("uv run alembic init migrations")
        env = Path("migrations/env.py").read_text()
        env = env.replace("target_metadata = None", f"from src.{pkg}.core.db import SQLModel; target_metadata = SQLModel.metadata")
        Path("migrations/env.py").write_text(env)
        ini = Path("alembic.ini").read_text()
        db_url = "sqlite:///database.db" if db_type == "SQLite" else "postgresql://user:pass@localhost/dbname"
        ini = ini.replace("sqlalchemy.url = driver://user:pass@localhost/dbname", f"sqlalchemy.url = {db_url}")
        Path("alembic.ini").write_text(ini)

    print(f"\n=== เสร็จแล้ว ===")
    print(f"cd {project_name}")
    if project_type in ["API", "AI-Service"]:
        print("uv run dev # รันเซิร์ฟเวอร์")
    print("uv run pytest # รันเทส")
    print("cat logs/app.log # ดู log")

if __name__ == "__main__":
    main()
```

### ตัวอย่างตอนรัน
```
=== BestSystem Project Generator ===
ชื่อโปรเจค: bestsystem-ai

โปรเจคประเภทไหน:
1. API - FastAPI ทำ REST API ให้ Frontend/Mobile ยิง
2. AI-Service - FastAPI + LangChain/Ollama ทำ AI chatbot/RAG
3. Worker - Background job ใช้ Celery/RQ รัน cron/queue
4. CLI - Command line tool ใช้ Typer
เลือก 1-4: 2

ใช้ Database อะไร:
1. SQLite - ไฟล์เดียว เริ่มง่ายสุด เหมาะกับ dev/test
2. PostgreSQL - Production จริง รองรับ concurrent เยอะ
3. None - ไม่ใช้ DB เก็บใน memory/ไฟล์
เลือก 1-3: 1

ระบบ Login:
1. JWT - มาตรฐาน Token 7 วัน Frontend/Mobile ใช้ได้หมด
2. API-Key - ง่ายสุด ส่ง header X-API-Key เหมาะ service-to-service
3. None - ไม่ต้อง login API public
เลือก 1-3: 1

=== สรุป ===
Project: bestsystem-ai
Type: AI-Service | DB: SQLite | Auth: JWT
ยืนยันสร้าง? y/n: y
```

**ข้อดีแบบนี้:**
1. **ไม่ต้องจำคำสั่ง** - ตอบ 1 2 3 ได้โปรเจคเลย
2. **มีคำแนะนำ** - แต่ละตัวเลือกบอกเลยว่าใช้ตอนไหน
3. **ต่อยอดง่าย** - อยากเพิ่ม Docker ก็เพิ่ม step 4 ถามต่อได้

อยากให้เพิ่ม step 4 ถามเรื่อง Docker, Redis, หรือ Deploy ขึ้น Railway ต่อมั้ย?