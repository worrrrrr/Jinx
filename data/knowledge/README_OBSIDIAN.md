# 📚 Jinx Knowledge Vault — คู่มือ Obsidian

โฟลเดอร์นี้คือ **Knowledge Vault** สำหรับระบบ Jinx และใช้งานกับ Obsidian ได้ทันที

## 🏗️ โครงสร้างไฟล์

```
data/knowledge/
├── README_OBSIDIAN.md      # ไฟล์นี้ (คู่มือการใช้งาน)
├── INDEX.md                # ดัชนีลิงก์ไฟล์ทั้งหมด
├── common.md               # ความรู้ทั่วไปเกี่ยวกับ Jinx
├── intent.md               # ตาราง Intent และ Keywords
├── python.md               # Python Best Practices
├── ...                     # ไฟล์ความรู้อื่นๆ
├── obital/                 # ความรู้ด้านโหราศาสตร์/จิตวิทยา
│   ├── bazi.md
│   ├── cognitivefn.md
│   └── ...
└── Clippings/              // คลิปโน้ตเพิ่มเติม
    ├── AI Automation Project Strategy.md
    └── INFJ5w4.md
```

## ✨ ฟีเจอร์ที่เพิ่มแล้วสำหรับ Obsidian

### 1. Wikilinks `[[ ]]`
ทุกไฟล์มีการเชื่อมโยงกันด้วย Obsidian Wikilinks:
- `[[python]]` → ลิงก์ไปไฟล์ `python.md`
- `[[intent]]` → ลิงก์ไปไฟล์ `intent.md`
- `[[setup_project]]` → ลิงก์ไปไฟล์ `setup_project.md`

### 2. Frontmatter
ทุกไฟล์มี YAML Frontmatter สำหรับ Obsidian:
```yaml
---
title: ชื่อหัวข้อ
tags: [knowledge, vault, หมวดหมู่]
aliases: [ชื่อไฟล์]
---
```

### 3. ดัชนีกลาง (INDEX.md)
ไฟล์ `INDEX.md` รวมลิงก์ทั้งหมด แบ่งตามหมวดหมู่:
- **General** — ความรู้ทั่วไป
- **obital** — โหราศาสตร์และจิตวิทยา
- **Clippings** — คลิปโน้ต

## 🔍 การค้นหาใน Obsidian

1. **Graph View** — ดูความเชื่อมโยงของโน้ตทั้งหมด
2. **Search** — ค้นหาด้วยคำสำคัญ
3. **Tags** — กรองด้วย `#knowledge`, `#vault`, `#obital`
4. **Backlinks** — ดูว่าไฟล์ไหนอ้างอิงถึงไฟล์นี้

## 📝 หมวดหมู่ความรู้

### 💻 Programming
- [[python]] — Python Best Practices
- [[javascript]] — JavaScript
- [[typescript]] — TypeScript
- [[rust]] — Rust
- [[go]] — Go
- [[sql]] — SQL
- [[programming_concepts]] — แนวคิดการเขียนโปรแกรม
- [[algorithms]] — อัลกอริทึม
- [[database_basics]] — ฐานข้อมูล
- [[web_basics]] — เว็บพื้นฐาน
- [[os_networking]] — ระบบปฏิบัติการและเครือข่าย

### 🧮 Mathematics
- [[math_algebra]] — พีชคณิต
- [[math_calculus]] — แคลคูลัส
- [[math_geometry]] — เรขาคณิต
- [[math_statistics]] — สถิติ

### 🌍 General Knowledge
- [[world_history]] — ประวัติศาสตร์โลก
- [[world_geography]] — ภูมิศาสตร์โลก
- [[physics_basics]] — ฟิสิกส์พื้นฐาน
- [[chemistry_basics]] — เคมีพื้นฐาน
- [[biology_basics]] — ชีววิทยาพื้นฐาน
- [[economics_basics]] — เศรษฐศาสตร์พื้นฐาน
- [[planets]] — ดาวเคราะห์

### 🇹🇭 ภาษาและวัฒนธรรมไทย
- [[thai_history]] — ประวัติศาสตร์ไทย
- [[thai_culture]] — วัฒนธรรมไทย
- [[thai_grammar]] — ไวยากรณ์ไทย
- [[thai_numerology]] — เลขศาสตร์ไทย

### 🔮 โหราศาสตร์และจิตวิทยา (Obital)
- [[bazi]] — ปาจื้อ (สี่เสา)
- [[cognitivefn]] — Cognitive Functions
- [[mbti]] — MBTI
- [[numerology]] — เลขศาสตร์
- [[name_analy]] — วิเคราะห์ชื่อ
- [[ac]] — Agentic Cognitive

### 🤖 Jinx System
- [[common]] — ความรู้ทั่วไปเกี่ยวกับ Jinx
- [[intent]] — ตาราง Intent
- [[qa]] — โจทย์และการวิเคราะห์
- [[setup_project]] — การสร้างโปรเจกต์
- [[prompt]] — Prompt Engineering
- [[emoji]] — การใช้ Emoji

## 🛠️ เคล็ดลับการใช้งาน

### สร้างลิงก์ใหม่
พิมพ์ `[[` แล้วเริ่มพิมพ์ชื่อไฟล์ Obsidian จะแนะนำไฟล์ที่มีอยู่

### ดู Graph
กด `G` ใน Obsidian เพื่อดู Graph View ของโน้ตทั้งหมด

### ค้นหาด้วย Tags
- `#knowledge` — ทุกไฟล์ความรู้
- `#vault` — ไฟล์ในคลัง
- `#obital` — ด้านโหราศาสตร์

## 📊 สถิติ

- **ไฟล์ทั้งหมด:** 45+ ไฟล์
- **หมวดหมู่:** 3 หมวด (General, obital, Clippings)
- **รูปแบบ:** Markdown พร้อม Wikilinks

---

*สร้างโดย Jinx Auto-Organizer สำหรับใช้งานกับ Obsidian*
