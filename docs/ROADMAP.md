# ROADMAP

## Vision

สร้าง Personal AI Runtime ที่ใช้ Knowledge เป็น Ground Truth และใช้ Tools ในการแก้ปัญหาจริง

เป้าหมายไม่ใช่ Chatbot

เป้าหมายคือ Runtime ที่สามารถ

* รับรู้
* เข้าใจ
* วางแผน
* ลงมือทำ
* ตอบกลับ

ได้อย่างตรวจสอบย้อนกลับได้

---

# Current Status

Stage: Foundation ✅ — Core Pipeline เสร็จสมบูรณ์

Progress: กำลังขยาย Knowledge Vault + Test Coverage

Architecture:

```
User
↓
Perception
↓
Reasoning
↓
Execution
↓
Response
↓
User
```

---

# Phase 1 — Core Runtime ✅

Goal: สร้าง Runtime ที่สามารถรับคำสั่งและเรียก Tool ได้

Tasks:

[x] Project Structure
[x] Knowledge Vault
[x] Core Documentation
[x] Perception Engine — intent detection, Thai NLP, math extraction
[x] Reasoning Engine — strategy selection, context rules
[x] Execution Engine — tool routing, security blocking
[x] Response Engine — template selection, formatting
[x] Orchestrator — pipeline integration

---

# Phase 2 — Knowledge System ✅

Goal: เชื่อม Runtime เข้ากับ Knowledge Vault

Tasks:

[x] Markdown Loader — อ่านไฟล์ .md จาก vault
[x] File Scanner — list ไฟล์ใน vault
[x] Search Engine — fuzzy matching ด้วย rapidfuzz
[x] Fuzzy Matching — ค้นหาแม้พิมพ์ผิด
[x] Context Extraction — ดึง snippet จากไฟล์
[x] Knowledge Ranking — เรียงคะแนนความเกี่ยวข้อง

---

# Phase 3 — Tool Ecosystem ⬜

Goal: สร้างชุดเครื่องมือหลักของระบบ

Tasks:

[x] Calculator Tool — tools/math.py (numeric eval)
[x] Symbolic Math Tool — tools/math.py (SymPy + Z3)
[x] File Tool — tools/file.py (read/write/list/patch/run)
[x] Search Tool — tools/search.py (fuzzy knowledge search)
[x] Obsidian Tool — tools/obsidian.py (create/append/link notes)
[x] Vault Utils — tools/utils.py (vault read/write/list)
[x] Ba Zi Tool — tools/bazi.py (Chinese astrology, standalone)
[x] Arch Generator — tools/arch_generator.py (scaffolding, standalone)
[ ] HTML Tool — สร้างเว็บจากคำอธิบาย
[ ] Data Analysis Tool — วิเคราะห์ข้อมูล (CSV, JSON)

---

# Phase 4 — Memory ⬜

Goal: เพิ่มความสามารถในการจดจำ

Tasks:

[x] Session Memory — core/memory.py (history + variables)
[ ] User Preferences — จดจำค่าที่ผู้ใช้ตั้ง
[ ] Fact Storage — เก็บความจริงข้าม session
[ ] Cache Layer — ลดการคำนวณซ้ำ

---

# Phase 5 — Evaluation ⬜

Goal: ตรวจสอบคุณภาพของระบบ

Tasks:

[x] Tool Tests — math, file, search มี unit tests
[x] Integration Tests — orchestator E2E scenarios
[x] Benchmark Suite — llm_compare.py + benchmark_cases.json
[ ] Engine Tests — unit tests สำหรับ perception, reasoning, execution, response
[ ] Self Evaluation — ระบบตรวจสอบคำตอบตัวเอง

---

# Phase 6 — LLM Integration ⬜

Goal: เพิ่ม LLM เป็น Optional Layer

Tasks:

[x] Ollama Integration — core/llm_core.py::OllamaProvider
[x] Groq Integration — core/llm_core.py::GroqProvider
[x] Claude Integration — core/llm_core.py::ClaudeProvider
[ ] Gemini Integration
[ ] Answer Comparison — เทียบผล tool vs LLM
[ ] LLM Review — ใช้ LLM ตรวจสอบคำตอบ

---

# Future

[ ] Knowledge Graph
[ ] Multi-Agent Collaboration
[ ] Autonomous Planning
[ ] Self Improvement
[ ] Personal Operating System

---

# Definition of Success

JINX สามารถ

1. อ่าน Knowledge ได้
2. เข้าใจคำสั่งได้
3. เลือกวิธีแก้ปัญหาได้
4. ใช้ Tool ได้
5. ตรวจสอบผลลัพธ์ได้
6. ตอบกลับได้

โดยไม่จำเป็นต้องพึ่ง LLM เป็นศูนย์กลางของระบบ
