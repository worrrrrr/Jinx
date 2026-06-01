#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def run(cmd, cwd=None, silent=False):
    if not silent: print(f"> {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=silent)
    if result.returncode != 0 and not silent:
        sys.exit(f"Command failed: {cmd}")
    return result

def ask(question, default=""):
    val = input(f"\n{question} [{default}]: ").strip()
    return val or default

def ask_choice(question, options, default="1"):
    print(f"\n{question}")
    for i, (key, desc) in enumerate(options.items(), 1):
        print(f" {i}. {key} - {desc}")
    while True:
        choice = input(f"เลือก 1-{len(options)} [{default}]: ").strip() or default
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            selected = list(options.keys())[int(choice)-1]
            print(f"เลือก: {selected}")
            return selected
        print("เลือกใหม่")

def main():
    print("=== BestSystem Project Generator v4 (Fully Fixed) ===")

    project_name = ask("ชื่อโปรเจค", "bestsystem-api").replace(" ", "-").lower()
    pkg = project_name.replace('-', '_')

    project_type = ask_choice("โปรเจคประเภทไหน:", {
        "API": "FastAPI REST API ธรรมดา",
        "AI-Service": "FastAPI + LangChain/Ollama ทำ Chatbot/RAG",
        "Fullstack": "FastAPI + Next.js ในโปรเจคเดียว",
        "Worker": "Celery Background Job",
        "CLI": "Typer Command Line Tool"
    })

    db_type = "None"
    if project_type in ["API", "AI-Service", "Fullstack"]:
        db_type = ask_choice("Database:", {
            "SQLite": "ไฟล์เดียว เริ่มง่าย dev/test ใช้ได้เลย",
            "PostgreSQL": "Production ใช้ตัวนี้ รองรับ concurrent",
            "MongoDB": "NoSQL เก็บ JSON ยืดหยุ่น",
            "None": "ไม่ใช้ DB"
        })

    auth_type = "None"
    if project_type in ["API", "AI-Service", "Fullstack"] and db_type != "None":
        auth_type = ask_choice("ระบบ Login:", {
            "JWT": "มาตรฐาน Frontend/Mobile เก็บ token",
            "Session": "Cookie แบบเก่า ใช้กับ Web ล้วน",
            "API-Key": "Header X-API-Key สำหรับ service-to-service",
            "None": "Public API ไม่ล็อกอิน"
        })

    use_redis = False
    if project_type in ["API", "AI-Service", "Fullstack", "Worker"]:
        use_redis = ask_choice("ใช้ Redis ไหม:", {
            "Yes": "ทำ Cache + Rate limit + Celery Queue",
            "No": "ไม่ใช้"
        }) == "Yes"

    use_cors = False
    if project_type in ["API", "AI-Service", "Fullstack"]:
        use_cors = ask_choice("เปิด CORS:", {
            "Yes": "อนุญาตทุก origin",
            "No": "ไม่เปิด"
        }) == "Yes"

    use_ci = ask_choice("เพิ่ม GitHub Actions CI:", {
        "Yes": "สร้าง .github/workflows/ci.yml",
        "No": "ไม่เอา"
    }) == "Yes"

    use_docker = ask_choice("ทำ Dockerfile:", {
        "Yes": "ได้ docker-compose",
        "No": "รันด้วย uv อย่างเดียว"
    }) == "Yes"

    deploy = "None"
    if use_docker:
        deploy = ask_choice("จะ Deploy ที่ไหน:", {
            "Railway": "Deploy ง่ายสุด",
            "Fly.io": "ฟรี tier ดี",
            "VPS": "Docker ธรรมดา",
            "None": "ยังไม่ deploy"
        })

    print(f"\n{'='*50}")
    print(f"Project Plan: {project_name}")
    print(f"{'='*50}")
    print(f"Type    : {project_type}")
    print(f"Database: {db_type}")
    print(f"Auth    : {auth_type}")
    print(f"Redis   : {use_redis}")
    print(f"CORS    : {use_cors}")
    print(f"CI      : {use_ci}")
    print(f"Docker  : {use_docker}")
    print(f"Deploy  : {deploy}")
    print(f"{'='*50}")

    if ask("ยืนยันสร้างตามนี้? y/n", "y").lower() != 'y':
        return

    # --- สร้างโปรเจค ---
    run(f"uv init {project_name}")
    os.chdir(project_name)
    run("uv python pin 3.11")

    # สร้างโครงสร้างโฟลเดอร์
    dirs = [f"src/{pkg}/api", f"src/{pkg}/models", f"src/{pkg}/core", "tests", "logs"]
    if db_type != "None": dirs.append("migrations")
    if project_type == "AI-Service": dirs.append(f"src/{pkg}/ai")
    if project_type == "Fullstack": dirs.append("frontend")

    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        if "src" in d:
            Path(d, "__init__.py").touch()

    Path("logs/.gitkeep").touch()
    Path(".env.example").write_text(
        "SECRET_KEY=change-me-in-production\n"
        "DATABASE_URL=sqlite:///database.db\n"
        "REDIS_URL=redis://localhost:6379\n"
        "CORS_ORIGINS=http://localhost:3000,http://localhost:8000\n"
    )
    Path(".gitignore").write_text(
        "__pycache__/\n*.pyc\n.env\ndatabase.db\nlogs/\n.ruff_cache/\n.pytest_cache/\n"
    )
    Path(".dockerignore").write_text(
        "__pycache__\n.env\ndatabase.db\n.git\n.gitignore\nlogs\n*.pyc\n.ruff_cache\n.pytest_cache\n"
    )

    # dependencies
    base = ["fastapi", "uvicorn[standard]", "loguru", "python-dotenv", "pydantic-settings"]
    dev = ["pytest", "pytest-asyncio", "httpx", "ruff", "pre-commit"]

    if db_type == "SQLite": base.extend(["sqlmodel", "aiosqlite", "alembic"])
    if db_type == "PostgreSQL": base.extend(["sqlmodel", "psycopg2-binary", "alembic"])
    if db_type == "MongoDB": base.extend(["beanie", "motor"])
    if auth_type == "JWT": base.extend(["python-jose[cryptography]", "passlib[bcrypt]"])
    if use_redis: base.extend(["redis", "celery"])
    if project_type == "AI-Service": base.extend(["langchain", "langchain-community", "chromadb"])
    if project_type == "CLI": base.extend(["typer[all]"])

    run(f"uv add {' '.join(base)}", silent=True)
    run(f"uv add --dev {' '.join(dev)}", silent=True)
    print("✅ Dependencies installed")

    # --- สร้าง core/config.py ---
    config_content = '''from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from loguru import logger
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///database.db"
    SECRET_KEY: str = "change-me"
    REDIS_URL: str = "redis://localhost:6379"
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

settings = Settings()
logger.add(BASE_DIR / "logs/app.log", rotation="10 MB", retention="7 days", level="INFO")
'''
    Path(f"src/{pkg}/core/config.py").write_text(config_content)

    # --- สร้าง main.py แบบไม่มี syntax error ---
    main_lines = []
    main_lines.append("from contextlib import asynccontextmanager")
    main_lines.append("from fastapi import FastAPI")
    main_lines.append("from fastapi.middleware.cors import CORSMiddleware")
    main_lines.append("from core.config import logger, settings")
    
    if db_type in ["SQLite", "PostgreSQL"]:
        main_lines.append("from core.db import engine")
        main_lines.append("from sqlmodel import SQLModel")
    
    main_lines.append("")
    main_lines.append("@asynccontextmanager")
    main_lines.append("async def lifespan(app: FastAPI):")
    main_lines.append("    logger.info(\"Starting up...\")")
    if db_type in ["SQLite", "PostgreSQL"]:
        main_lines.append("    SQLModel.metadata.create_all(engine)")
    main_lines.append("    yield")
    main_lines.append("    logger.info(\"Shutting down...\")")
    main_lines.append("")
    main_lines.append(f"app = FastAPI(title=\"{project_name}\", lifespan=lifespan)")
    main_lines.append("")
    
    if use_cors:
        main_lines.append("app.add_middleware(")
        main_lines.append("    CORSMiddleware,")
        main_lines.append("    allow_origins=settings.CORS_ORIGINS,")
        main_lines.append("    allow_credentials=True,")
        main_lines.append("    allow_methods=[\"*\"],")
        main_lines.append("    allow_headers=[\"*\"],")
        main_lines.append(")")
        main_lines.append("")
    
    main_lines.append("@app.get(\"/health\")")
    main_lines.append("def health():")
    main_lines.append(f"    return {{\"status\": \"ok\", \"type\": \"{project_type}\"}}")
    main_lines.append("")
    
    # เพิ่ม example endpoint ถ้ามี DB
    if db_type in ["SQLite", "PostgreSQL"]:
        main_lines.append("from fastapi import Depends")
        main_lines.append("from sqlmodel import Session")
        main_lines.append("from core.db import get_session")
        main_lines.append("")
        main_lines.append("@app.get(\"/example\")")
        main_lines.append("def example_endpoint(session: Session = Depends(get_session)):")
        main_lines.append("    return {\"message\": \"DB session ready\"}")
    
    Path(f"src/{pkg}/main.py").write_text("\n".join(main_lines))

    # --- สร้าง core/db.py ถ้ามี SQLModel ---
    if db_type in ["SQLite", "PostgreSQL"]:
        db_py = '''from sqlmodel import SQLModel, create_engine, Session
from core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session
'''
        Path(f"src/{pkg}/core/db.py").write_text(db_py)

        user_model = '''from sqlmodel import SQLModel, Field
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int
    created_at: datetime
'''
        Path(f"src/{pkg}/models/user.py").write_text(user_model)

    # --- Docker ---
    if use_docker:
        dockerfile = f'''FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml .
RUN uv lock
RUN uv sync --no-dev
COPY . .
CMD ["uv", "run", "uvicorn", "src.{pkg}.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        Path("Dockerfile").write_text(dockerfile)

        compose_services = '''services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env'''

        if db_type == 'PostgreSQL':
            compose_services += '''
    depends_on: [db]
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: dbname
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]'''

        if use_redis:
            if 'depends_on' not in compose_services:
                compose_services += '''
    depends_on: [redis]'''
            else:
                compose_services = compose_services.replace('depends_on: [db]', 'depends_on: [db, redis]')
            compose_services += '''
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]'''

        if db_type == 'PostgreSQL':
            compose_services += '\n\nvolumes:\n  pgdata:'
        Path("docker-compose.yml").write_text(compose_services)

    # --- Pre-commit ---
    precommit_config = '''repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
'''
    Path(".pre-commit-config.yaml").write_text(precommit_config)

    # --- GitHub Actions ---
    if use_ci:
        github_dir = Path(".github/workflows")
        github_dir.mkdir(parents=True, exist_ok=True)
        ci_yml = '''name: CI

on: [push, pull_request]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --dev
      - run: uv run ruff check src
      - run: uv run pytest -v
'''
        Path(".github/workflows/ci.yml").write_text(ci_yml)

    # --- Makefile ---
    docker_line = "docker-up:\n\tdocker-compose up --build\n" if use_docker else ""
    makefile = f'''dev:
\tuv run uvicorn src.{pkg}.main:app --reload
test:
\tuv run pytest -v
lint:
\tuv run ruff check src
format:
\tuv run ruff format src
precommit:
\tuv run pre-commit run --all-files
{docker_line}'''
    Path("Makefile").write_text(makefile)

    # --- Test file ---
    if project_type not in ["CLI", "Worker"]:
        test_content = f'''from fastapi.testclient import TestClient
from src.{pkg}.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200
'''
    else:
        test_content = '''def test_placeholder():
    assert True
'''
    Path("tests/test_main.py").write_text(test_content)

    # --- Alembic init ---
    if db_type in ["SQLite", "PostgreSQL"]:
        run("uv run alembic init migrations", silent=True)

    # --- README.md ---
    docker_help_line = "\nmake docker-up # start Docker" if use_docker else ""
    readme = f'''# {project_name}
Generated by BestSystem Wizard v4

## Stack
- Type: {project_type}
- DB: {db_type}
- Auth: {auth_type}
- Redis: {use_redis}
- CORS: {use_cors}
- CI: {use_ci}
- Docker: {use_docker}

## Quick Start
```bash
make dev      # run dev server
make test     # run tests
make lint     # ruff check
make format   # auto format
make precommit# run pre-commit hooks{docker_help_line}
```

## Environment
Copy `.env.example` to `.env` and adjust values.
'''
    Path("README.md").write_text(readme)

    # --- สรุปผล ---
    print(f"\n{'='*50}")
    print(f"✅ เสร็จแล้ว! cd {project_name}")
    print(f"{'='*50}")
    print("คำสั่งที่ใช้บ่อย:")
    print("make dev     - รันเซิร์ฟเวอร์")
    print("make test    - รันเทส")
    print("make lint    - ตรวจสอบโค้ด")
    print("make format  - จัดรูปแบบโค้ดอัตโนมัติ")
    print("make precommit - รัน pre-commit ทุกตัว")
    if use_docker:
        print("make docker-up - รัน Docker")
    if use_ci:
        print("GitHub Actions จะทำงานเมื่อ push")
    print("\nเริ่มต้นด้วยการตั้งค่า pre-commit:")
    print(f"cd {project_name}")
    print("uv run pre-commit install")
    if deploy != "None":
        print(f"\nDeploy: {deploy} - ดู docker-compose.yml")

if __name__ == "__main__":
    main()
