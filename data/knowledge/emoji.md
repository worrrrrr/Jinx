# 📖 คลังความหมาย Emoji สำหรับ Jinx AI

ตารางนี้ใช้แมป Emoji → Intent, Domain, Action, TopicHint, และตัวเลือกเสริมต่างๆ  
เรียงลำดับจาก Emoji ยาวสุดไปสั้นสุด เพื่อให้ regex จับได้ถูกต้อง

> **คำอธิบายคอลัมน์**  
> - `Emoji` : ลำดับอิโมจิที่ผู้ใช้พิมพ์นำหน้า  
> - `Intent` : ความตั้งใจหลัก (`solve`, `query`, `create`, `search`, `execute`, `confirm`, `delete`, `navigate`, `summarize`, `translate`, `remind`, `schedule`)  
> - `Domain` : ขอบเขตของงาน (`math`, `web`, `code`, `file`, `system`, `knowledge`, `communication`, `media`, `utility`)  
> - `Action` : การกระทำที่ engine ต้องทำ (`solve_with_steps`, `compute`, `explain`, `retrieve`, `run_bot`, `remove`, `accept`, `help`, `generate`, `translate`, `summarize`, `remind`, `schedule`, `navigate`)  
> - `TopicHint` : หัวข้อเริ่มต้น (ถ้าผู้ใช้ไม่พิมพ์อะไรเพิ่ม)  
> - `ShowSteps` : ต้องแสดงวิธีทำหรือไม่ (true/false)  
> - `Note` : คำอธิบายภาษาไทย

---

## 🧮 กลุ่มคำนวณและคณิตศาสตร์

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| 🔢📝 | solve | math | solve_with_steps | equation_solving | true | คำนวณพร้อมแสดงวิธีทำทีละขั้น |
| 🔢 | solve | math | compute | calculation | false | คำนวณอย่างเดียว (ไม่ต้องแสดงวิธี) |
| 📐🧮 | solve | math | geometry | geometry_calculation | false | คำนวณเรขาคณิต |
| 📊📈 | solve | math | statistics | data_analysis | false | วิเคราะห์สถิติ / กราฟ |
| 🧮🔢 | solve | math | arithmetic | basic_math | false | คิดเลขพื้นฐาน (+ - × ÷) |
| ∫∑ | solve | math | calculus | calculus_problem | true | แคลคูลัส (อินทิเกรต/ซัมเมชัน) |

---

## 🌐 กลุ่มค้นหาและเว็บ

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| 🔍 | search | web | retrieve | search_query | false | ค้นหาข้อมูลทั่วไป |
| 🌐🔍 | search | web | deep_search | web_search | false | ค้นหาแบบเจาะลึก (deep search) |
| 📚🔍 | search | knowledge | lookup | knowledge_base | false | ค้นหาในฐานความรู้ของตัวเอง |
| 🗺️🔍 | search | web | map_search | location_query | false | ค้นหาแผนที่ / สถานที่ |
| 🎬🔍 | search | media | find_media | movie_or_music | false | ค้นหาหนัง / เพลง |

---

## 📝 กลุ่มสร้างและเขียน

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| ✍️📝 | create | code | write_code | code_generation | false | เขียนโค้ดให้ |
| ✍️📄 | create | file | write_document | document_creation | false | สร้างเอกสาร / โน้ต |
| 🎨✍️ | create | design | generate_image | art_generation | false | สร้างภาพ / ออกแบบ |
| 📝 | query | general | explain | explanation | false | ขอคำอธิบาย (ทั่วไป) |
| 📋 | create | utility | make_list | checklist | false | สร้างรายการ / เช็คลิสต์ |

---

## 🤖 กลุ่มระบบและควบคุมบอท

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| 🤖 | execute | system | run_bot | assistant | false | เรียกใช้บอท |
| 🗑️ | delete | file | remove | deletion | false | ลบไฟล์ / ข้อมูล |
| 👍 | confirm | system | accept | confirmation | false | ยืนยัน / ตกลง |
| 👎 | reject | system | decline | rejection | false | ปฏิเสธ / ไม่เอา |
| ❓ | query | system | help | help | false | ขอความช่วยเหลือ |
| ⚙️🔧 | execute | system | configure | settings | false | ตั้งค่าระบบ |
| 🔄 | execute | system | restart | reload | false | รีสตาร์ท / โหลดใหม่ |

---

## 📞 กลุ่มสื่อสาร

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| 📤 | send | communication | dispatch | message | false | ส่งข้อความ |
| 📞 | call | communication | dial | phone_call | false | โทรศัพท์ |
| 📧 | send | communication | email | email_compose | false | ส่งอีเมล |
| 💬 | query | communication | chat | conversation | false | พูดคุย / ถามตอบ |
| 🔔 | execute | utility | notify | reminder | false | ตั้งการแจ้งเตือน |

---

## 🗂️ กลุ่มจัดการไฟล์และความรู้

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| 📂🗑️ | delete | file | remove_folder | folder_deletion | false | ลบโฟลเดอร์ |
| 📄✏️ | create | file | edit_file | file_edit | false | แก้ไขไฟล์ |
| 💾 | save | file | store | save_file | false | บันทึกข้อมูล |
| 📁🔍 | search | file | find_file | file_search | false | ค้นหาไฟล์ |
| 🧠📚 | query | knowledge | recall | memory_retrieval | false | ทบทวนความจำ / ดึงความรู้ |

---

## ⏰ กลุ่มเตือนความจำและเวลา

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| ⏰🔔 | remind | utility | set_reminder | time_event | false | ตั้งเตือนเวลา |
| 📅 | schedule | utility | plan | calendar_event | false | จัดการปฏิทิน / นัดหมาย |
| ⏱️ | query | utility | timer | countdown | false | จับเวลา / นับถอยหลัง |
| 🕒 | query | utility | what_time | current_time | false | เวลาเท่าไหร่ |

---

## 🎨 กลุ่มสร้างสรรค์และความบันเทิง

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| 🎨 | create | design | draw | art | false | วาดรูป |
| 🎵 | play | media | play_music | song | false | เล่นเพลง |
| 🎬 | play | media | play_video | movie | false | เล่นหนัง / ซีรีส์ |
| 🎮 | execute | media | launch_game | game | false | เปิดเกม |
| 📸 | create | media | take_photo | photography | false | ถ่ายรูป |

---

## 💬 กลุ่มอารมณ์และการสนทนาทั่วไป (ใช้เป็น intent หลักหรือเสริม)

| Emoji | Intent | Domain | Action | TopicHint | Note |
|-------|--------|--------|--------|-----------|------|
| 😊 | query | general | express_happy | happy_feeling | ดีใจ / ชอบใจ |
| 😢 | query | general | express_sad | sad_feeling | เศร้า / เสียใจ |
| 😠 | query | general | express_angry | angry_feeling | โกรธ |
| 😨 | query | general | express_fear | fear | กลัว |
| 😲 | query | general | express_surprise | surprise | ตกใจ |
| 🤔 | query | general | express_confused | confusion | งง / คิดไม่ตก |
| 😅 | query | general | express_embarrass | embarrassed | เขิน / เก้อ |
| 🥱 | query | general | express_tired | tired | เหนื่อย / เบื่อ |
| 🫡 | execute | system | acknowledge | salute | รับทราบ / รับคำสั่ง |
| 🙏 | query | general | request | please | ขอความกรุณา |

---

## 🧩 Emoji ที่มีความหมายพิเศษ (ใช้ร่วมกับคำสั่งอื่น)

| Emoji | ฟังก์ชันเสริม | ตัวอย่างการใช้ |
|-------|----------------|----------------|
| 🔁 | ทำซ้ำ / รันอีกครั้ง | `🔁 🔢📝 2+2` → คำนวณซ้ำ |
| 🔀 | สุ่ม / เปลี่ยนลำดับ | `🔀 🎵` → สุ่มเพลง |
| 🚫 | ยกเลิก / ห้าม | `🚫 🗑️` → ยกเลิกการลบ |
| ⭐ | บันทึกเป็นรายการโปรด | `⭐ 🔍 cat` → บันทึกคำค้นหา |

---

## 📌 หมายเหตุการใช้งาน

1. **Emoji ซ้อนกันได้** – ผู้ใช้สามารถพิมพ์ `🔢📝 3^x=x^9` หรือ `🔍🔢 10*20` ได้ (ระบบจะจับคู่จากยาวสุดก่อน)
2. **ถ้าไม่เจอ Emoji ที่แมป** – ระบบจะ fallback ไปใช้ keyword matching ปกติ
3. **กรณีมีหลาย Emoji ในข้อความ** – จะจับเฉพาะชุดแรกที่ขึ้นต้นเท่านั้น (ส่วนที่เหลือถือเป็นส่วนหนึ่งของพารามิเตอร์)
4. **การแสดงวิธีทำ (`ShowSteps`)** – ใช้ในกลุ่ม solve เป็นหลัก ถ้าเป็น true engine ต้องแสดงรายละเอียดการแก้ปัญหา
5. **สามารถเพิ่มแถวใหม่ได้ทุกเมื่อ** – ระบบโหลดไฟล์นี้ตอนเริ่มต้น ถ้าอยากโหลดใหม่แบบ real-time ให้ implement hot-reload

---

## 🔧 ตัวอย่างการเพิ่ม Emoji ใหม่ (สำหรับนักพัฒนา)

ถ้าต้องการเพิ่ม Emoji `🧪🔬` สำหรับการทดลองทางวิทยาศาสตร์ ให้เพิ่มหนึ่งแถวในตาราง:

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| 🧪🔬 | solve | science | experiment | lab_calculation | true | คำนวณผลทดลอง |

จากนั้นระบบจะจับ `🧪🔬` ได้ทันที (ต้อง restart โปรแกรมหากไม่มีการ reload อัตโนมัติ)

---

**สร้างโดย Jinx Perception Team**  
อัปเดตล่าสุด: 2026-05-31


## MBTI Face Emoji Mapping (สำหรับจับบุคลิกผู้ใช้)

| Emoji | Intent | Domain | Action | TopicHint | ShowSteps | Note |
|-------|--------|--------|--------|-----------|-----------|------|
| 🧐 | personality | mbti | set_user_type | INTJ | false | ตั้งว่าผู้ใช้เป็น INTJ |
| 🤓 | personality | mbti | set_user_type | INTP | false | ตั้งว่าผู้ใช้เป็น INTP |
| 😤 | personality | mbti | set_user_type | ENTJ | false | ตั้งว่าผู้ใช้เป็น ENTJ |
| 😏 | personality | mbti | set_user_type | ENTP | false | ตั้งว่าผู้ใช้เป็น ENTP |
| 🥺 | personality | mbti | set_user_type | INFJ | false | ตั้งว่าผู้ใช้เป็น INFJ |
| 😇 | personality | mbti | set_user_type | INFP | false | ตั้งว่าผู้ใช้เป็น INFP |
| 🤗 | personality | mbti | set_user_type | ENFJ | false | ตั้งว่าผู้ใช้เป็น ENFJ |
| 😜 | personality | mbti | set_user_type | ENFP | false | ตั้งว่าผู้ใช้เป็น ENFP |
| 😐 | personality | mbti | set_user_type | ISTJ | false | ตั้งว่าผู้ใช้เป็น ISTJ |
| 🥰 | personality | mbti | set_user_type | ISFJ | false | ตั้งว่าผู้ใช้เป็น ISFJ |
| 😠 | personality | mbti | set_user_type | ESTJ | false | ตั้งว่าผู้ใช้เป็น ESTJ |
| 😊 | personality | mbti | set_user_type | ESFJ | false | ตั้งว่าผู้ใช้เป็น ESFJ |
| 😎 | personality | mbti | set_user_type | ISTP | false | ตั้งว่าผู้ใช้เป็น ISTP |
| 😌 | personality | mbti | set_user_type | ISFP | false | ตั้งว่าผู้ใช้เป็น ISFP |
| 😈 | personality | mbti | set_user_type | ESTP | false | ตั้งว่าผู้ใช้เป็น ESTP |
| 🤪 | personality | mbti | set_user_type | ESFP | false | ตั้งว่าผู้ใช้เป็น ESFP |