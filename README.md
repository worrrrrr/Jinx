# JINX

Personal AI Runtime

---

## Vision

JINX คือระบบ AI ส่วนตัวที่ใช้ข้อมูลภายในเป็นแหล่งความจริงหลัก (Ground Truth)

เป้าหมายคือสร้าง AI ที่สามารถ:

* เข้าใจคำสั่งของผู้ใช้
* ค้นหาความรู้จาก Knowledge Vault
* วางแผนการทำงาน
* เรียกใช้เครื่องมือจริง (Tools)
* สร้างคำตอบที่ถูกต้องและตรวจสอบได้

โดยไม่พึ่งพา LLM เป็นศูนย์กลางของระบบ

LLM สามารถถูกเรียกใช้เป็นผู้ช่วยหรือผู้ตรวจสอบได้ แต่ไม่ใช่แหล่งความจริงหลักของระบบ

---

## Core Principles

### Knowledge First

ข้อมูลใน Vault คือแหล่งความจริงหลัก

```text
data/knowledge/
```

ทุกการตอบควรอ้างอิงจากข้อมูลภายในก่อน

---

### Tool First

งานที่ต้องคำนวณหรือประมวลผลจริง ต้องใช้ Tool

ตัวอย่าง:

* คณิตศาสตร์
* วิเคราะห์ข้อมูล
* ค้นหาไฟล์
* สร้างเอกสาร
* สร้าง HTML

ห้ามให้โมเดลเดาคำตอบแทนการคำนวณ

---

### Deterministic First

ระบบควรให้ผลลัพธ์เหมือนเดิมเมื่อได้รับข้อมูลเดียวกัน

หลีกเลี่ยงการเดาหรือสุ่มโดยไม่จำเป็น

---

### LLM Optional

LLM เป็นส่วนเสริม

ตัวอย่าง:

* อธิบายผลลัพธ์
* เปรียบเทียบคำตอบ
* ตรวจสอบคุณภาพ
* สรุปข้อมูล

ไม่ใช่ส่วนหลักของระบบ

---

## Project Structure

```text
JINX/

core/
├─ orchestrator.py
├─ memory.py
└─ llm_core.py

engines/
├─ perception.py
├─ reasoning.py
├─ execution.py
└─ response.py

tools/

data/
└─ knowledge/

main.py

README.md
CONTEXT.md
RULES.md
ARCHITECTURE.md
ROADMAP.md
```

---

## System Flow

```text
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

## Components

### Perception

ทำหน้าที่รับรู้และทำความเข้าใจข้อมูลจากผู้ใช้

ตัวอย่าง

```text
สร้างเว็บบ้าน
```

ถูกแปลงเป็น

```python
{
    "intent": "create",
    "target": "web",
    "topic": "house"
}
```

---

### Reasoning

วางแผนว่าต้องใช้วิธีใดในการแก้ปัญหา

ตัวอย่าง

```python
{
    "tool": "html",
    "action": "generate"
}
```

---

### Execution

เรียกใช้ Tool ที่เหมาะสม

ตัวอย่าง

```python
html_tool.run(...)
math_tool.run(...)
search_tool.run(...)
```

---

### Response

แปลงผลลัพธ์ให้อยู่ในรูปแบบที่ผู้ใช้เข้าใจง่าย

---

### Memory

เก็บข้อมูลระยะสั้นและระยะยาวของระบบ

---

### LLM Core

ชั้นเชื่อมต่อกับโมเดลภายนอก

ตัวอย่าง

* Claude
* Gemini
* Groq
* Ollama

ใช้สำหรับงานเสริมเท่านั้น

---

## Knowledge Vault

Knowledge Vault อยู่ที่

```text
data/knowledge/
```

ใช้ Obsidian เป็นเครื่องมือจัดการข้อมูล

ตัวอย่าง

```text
knowledge/
├─ ai/
├─ math/
├─ programming/
├─ projects/
└─ notes/
```

ระบบสามารถค้นหาและดึงข้อมูลจากไฟล์ Markdown ได้โดยตรง

---

## Tools

Tools คือความสามารถที่ลงมือทำงานจริง

ตัวอย่าง

```text
tools/
├─ math.py
├─ symbolic.py
├─ search.py
├─ html.py
├─ markdown.py
└─ file.py
```

หน้าที่ของ Tool คือ

* รับ Input
* ประมวลผล
* ส่งคืนผลลัพธ์

โดยไม่ต้องรู้ว่าผู้ใช้คือใครหรือมาจาก Intent ใด

---

## Current Goal

Phase 1

* Intent Detection
* Knowledge Search
* Tool Routing
* Basic Response Generation

---

## Future Goal

Phase 2

* Memory System
* Knowledge Ranking
* Knowledge Graph
* Self Evaluation

---

Phase 3

* Multi-Agent Collaboration
* Autonomous Planning
* LLM Review Layer
* Continuous Learning

---

## Philosophy

JINX ไม่ได้พยายามสร้าง LLM อีกตัวหนึ่ง

JINX พยายามสร้าง Runtime ที่สามารถ:

* เข้าใจ
* คิด
* ลงมือทำ
* ตอบกลับ

โดยใช้ความรู้ภายในและเครื่องมือจริงเป็นแกนหลักของระบบ
