# ARCHITECTURE

## High Level Flow

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

หน้าที่

* รับ Input
* ทำความเข้าใจ Intent
* แยก Parameters
* สร้าง Structured Request

ผลลัพธ์

```python
{
    "intent": "create",
    "target": "html",
    "topic": "house"
}
```

---

### Reasoning

หน้าที่

* เลือกวิธีแก้ปัญหา
* เลือก Tool
* สร้างแผนการทำงาน

ผลลัพธ์

```python
{
    "tool": "html",
    "action": "generate"
}
```

---

### Execution

หน้าที่

* เรียก Tool
* จัดการ Error
* รวมผลลัพธ์

---

### Response

หน้าที่

* สร้างคำตอบ
* จัดรูปแบบผลลัพธ์
* สื่อสารกับผู้ใช้

---

### Knowledge

ตำแหน่ง

```text
data/knowledge/
```

ใช้เป็น Ground Truth ของระบบ

---

### Memory

ใช้เก็บ

* Session
* Context
* Preferences
* Cached Results

---

### Tools

ใช้สำหรับการทำงานจริง

ตัวอย่าง

* Math
* Search
* File
* HTML
* Markdown

---

### LLM Layer

เป็น Optional Component

ใช้เมื่อ

* ต้องการเปรียบเทียบคำตอบ
* ต้องการสรุป
* ต้องการตรวจสอบ

LLM ไม่ใช่ส่วนบังคับของ Runtime
