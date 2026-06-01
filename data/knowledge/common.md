# Jinx — ความรู้ทั่วไป (Common Knowledge)

เอกสารนี้เป็นจุดเริ่มต้นสำหรับคำถามภาพรวม คำสั่งที่ใช้บ่อย และการชี้ไปยังความรู้เฉพาะทาง

---

## Jinx คืออะไร

Jinx (JINX) คือ **Personal AI Runtime** — ไม่ใช่แค่แชทบอท

ระบบทำงานตามลำดับ:

1. **Perception** — เข้าใจคำสั่งและ intent
2. **Reasoning** — วางแผนเลือกเครื่องมือ
3. **Execution** — รัน tool จริง (คณิต, ค้นหา, เขียนไฟล์)
4. **Response** — จัดรูปแบบคำตอบ

หลักสำคัญ:

- **Knowledge First** — ความจริงมาจาก `data/knowledge/` ก่อน
- **Tool First** — คำนวณและค้นหาต้องใช้ tool ไม่เดา
- **LLM Optional** — ใช้ LLM เป็นชั้นเสริมได้ ไม่บังคับ

---

## Knowledge Vault อยู่ที่ไหน

```text
data/knowledge/
```

ไฟล์ Markdown ในโฟลเดอร์นี้คือแหล่งความจริงหลัก (Ground Truth)  
ใช้ Obsidian จัดการได้

---

## Jinx ทำอะไรได้บ้าง

| ประเภท | ตัวอย่างคำสั่ง | เครื่องมือ / ไฟล์อ้างอิง |
|--------|----------------|-------------------------|
| คณิตศาสตร์ | `x-y=5, xy=24`, `3^x=x^9` | math (SymPy, Z3) |
| ถามความรู้ | `Python คืออะไร`, `ค้นหา intent` | search → vault |
| เขียนโค้ด | `สร้างไฟล์ scripts/demo.py` + code block | tools/file.py (workspace) |
| โน้ต Obsidian | สร้างโน้ต `.md` ใน vault | obsidian / vault tools |
| สร้างโปรเจกต์ | ตั้งโปรเจกต์ FastAPI | setup_project.md, python.md |

---

## คำสั่ง CLI

```bash
python main.py          # REPL โต้ตอบ
python realworld.py     # ชุดทดสอบสถานการณ์จริง
python -m pytest tests/ # ทดสอบระบบ
```

---

## คำพ้องและการค้นหา (Aliases)

ใช้ตารางนี้เมื่อผู้ใช้ถามคนละคำแต่หมายถึงหัวข้อเดียวกัน

| ผู้ใช้อาจพูด | ค้นหา / อ่านในไฟล์ |
|--------------|-------------------|
| Jinx, JINX, จิ๊กซ์, ระบบ | common.md (ไฟล์นี้) |
| Python, ไพธอน, py | python.md |
| intent, เจตนา, ความตั้งใจ | intent.md |
| vault, คลังความรู้, knowledge | common.md |
| ตั้งโปรเจกต์, สร้างโปรเจกต์, scaffold, FastAPI | setup_project.md |
| โจทย์, QA, ปัญญา, theory of mind | qa.md |
| emoji, อีโมจิ | emoji.md |
| สมการ, คณิต, แก้สมการ | qa.md, math (tool) |
| เขียนโค้ด, สร้างไฟล์ py | python.md, common.md |

---

## คำถามที่พบบ่อย (FAQ)

### ทำไมตอบไม่เจอ

- คำค้นหาไม่มีใน vault — เพิ่มหัวข้อใน `common.md` หรือไฟล์เฉพาะทาง
- พิมพ์ผิดมาก — ระบบใช้ fuzzy search ช่วยบางส่วน
- ถามเรื่องคณิต — ใช้รูปแบบสมการชัดเจน ไม่ต้องพึ่ง vault

### ความต่าง workspace กับ vault

- **vault** (`data/knowledge/`) = ความรู้ / โน้ต Obsidian
- **workspace** (โฟลเดอร์โปรเจกต์ Jinx) = โค้ด `.py` ที่รันและแก้ได้

### ใครเป็นคนสร้าง / ใช้ยังไง

Jinx เป็นโปรเจกต์ส่วนตัว (Personal AI Runtime) ออกแบบให้ทำงานได้โดยไม่พึ่ง LLM เป็นศูนย์กลาง

---

## ลิงก์ไปความรู้เฉพาะทาง

- [[python.md]] — Python, FastAPI, โครงสร้างโปรเจกต์
- [[setup_project.md]] — สคริปต์สร้างโปรเจกต์
- [[intent.md]] — ตาราง intent และคำสำคัญ
- [[qa.md]] — โจทย์และการวิเคราะห์เชิงตรรกะ
- [[emoji.md]] — การใช้ emoji กับ intent
