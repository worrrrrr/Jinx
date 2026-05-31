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

Stage: Foundation

Progress: In Development

Architecture:

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

---

# Phase 1 - Core Runtime

Goal:

สร้าง Runtime ที่สามารถรับคำสั่งและเรียก Tool ได้

Tasks:

[x] Project Structure

[x] Knowledge Vault

[x] Core Documentation

[ ] Perception Engine

[ ] Reasoning Engine

[ ] Execution Engine

[ ] Response Engine

[ ] Orchestrator

Success Criteria:

* รับ Input ได้
* วิเคราะห์ Intent ได้
* เรียก Tool ได้
* ส่งผลลัพธ์กลับได้

---

# Phase 2 - Knowledge System

Goal:

เชื่อม Runtime เข้ากับ Knowledge Vault

Tasks:

[ ] Markdown Loader

[ ] File Scanner

[ ] Search Engine

[ ] Fuzzy Matching

[ ] Context Extraction

[ ] Knowledge Ranking

Success Criteria:

* ค้นหาไฟล์ได้
* ดึงข้อมูลได้
* จัดอันดับข้อมูลได้

---

# Phase 3 - Tool Ecosystem

Goal:

สร้างชุดเครื่องมือหลักของระบบ

Tasks:

[ ] Calculator Tool

[ ] Symbolic Math Tool

[ ] File Tool

[ ] Markdown Tool

[ ] Search Tool

[ ] HTML Tool

[ ] Data Analysis Tool

Success Criteria:

* Tool ทุกตัวมี Test
* Tool ทุกตัวเรียกผ่าน Execution ได้

---

# Phase 4 - Memory

Goal:

เพิ่มความสามารถในการจดจำ

Tasks:

[ ] Session Memory

[ ] User Preferences

[ ] Fact Storage

[ ] Cache Layer

Success Criteria:

* จำ Context การสนทนาได้
* เก็บข้อมูลสำคัญได้

---

# Phase 5 - Evaluation

Goal:

ตรวจสอบคุณภาพของระบบ

Tasks:

[ ] Tool Tests

[ ] Engine Tests

[ ] Integration Tests

[ ] Benchmark Suite

[ ] Self Evaluation

Success Criteria:

* ทุก Component มีการทดสอบ
* สามารถระบุจุดผิดพลาดได้

---

# Phase 6 - LLM Integration

Goal:

เพิ่ม LLM เป็น Optional Layer

Tasks:

[ ] Ollama Integration

[ ] Groq Integration

[ ] Gemini Integration

[ ] Claude Integration

[ ] Answer Comparison

[ ] LLM Review

Success Criteria:

* Runtime ทำงานได้โดยไม่ต้องใช้ LLM
* LLM ใช้เป็นที่ปรึกษาได้

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
