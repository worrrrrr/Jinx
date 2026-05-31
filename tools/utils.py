# tools/utils.py

import os
import re
import datetime
from typing import Dict, Any, List, Callable

# กำหนดโฟลเดอร์เก็บเอกสารซึ่งทำหน้าที่เป็น Obsidian Vault
VAULT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge"
)


def get_tools() -> Dict[str, Callable]:
    """
    ส่งคืนพจนานุกรมคีย์เครื่องมือสำหรับลงทะเบียนใน ExecutionEngine
    """
    return {
        "update_file": handle_vault_write,
        "create_file": handle_vault_write,
        "read_file": handle_vault_read,
        "list_file": handle_vault_list,
        "file": handle_vault_list
    }


def handle_vault_write(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    สร้างหรือเขียนทับโน้ตลงใน Obsidian Vault (data/knowledge/) อย่างปลอดภัย
    """
    # 1. สร้างโฟลเดอร์ Vault กรณีที่ยังไม่มีในระบบ
    os.makedirs(VAULT_DIR, exist_ok=True)

    # 2. ค้นหาชื่อไฟล์เป้าหมายจาก Entities (เช่น ตรวจจับ ยินดีต้อนรับ.md)
    filename = "note.md"
    for ent in entities:
        if ent.endswith((".md", ".txt")):
            filename = ent
            break
            
    # ตรวจสอบส่วนขยายไฟล์ บังคับให้เป็นไฟล์ Markdown เสมอเพื่อความเข้ากันได้ของ Obsidian
    if not filename.endswith(".md"):
        filename = f"{os.path.splitext(filename)[0]}.md"

    # 3. ตรวจสอบความปลอดภัยป้องกันการโจมตี Directory Traversal
    safe_path = os.path.abspath(os.path.join(VAULT_DIR, filename))
    if not safe_path.startswith(os.path.abspath(VAULT_DIR)):
        return {"status": "fail", "message": "ปฏิเสธการดำเนินการ: ตรวจพบความเสี่ยงด้านความปลอดภัยของพิกัดไฟล์"}

    # 4. คัดกรองเนื้อหาหลักที่จะบันทึก (คัดเอาคำคีย์เวิร์ดการสั่งออก)
    content = inp.strip()
    # ดึงคีย์การสั่งงานที่เป็นภาษาไทยและชื่อไฟล์ออกจากเนื้อหาหลักของโน้ต
    content = re.sub(r"สร้างไฟล์|สร้างโน้ต|เขียนไฟล์|บันทึก", "", content, flags=re.IGNORECASE)
    content = content.replace(filename, "").strip()

    if not content:
        content = "โน้ตเปล่าที่สร้างโดยระบบอัตโนมัติ"

    # 5. จัดแต่งหน้าเอกสารพร้อมแทรก Frontmatter ของ Obsidian
    today_str = datetime.date.today().isoformat()
    note_title = os.path.splitext(filename)[0]
    
    # หากเนื้อหายังไม่มีการจัดโครงสร้าง ให้จัดรูปแบบ Frontmatter ให้อัตโนมัติ
    if not content.startswith("---"):
        obsidian_note = (
            f"---\n"
            f"created: {today_str}\n"
            f"author: Jinx Agent\n"
            f"tags: [jinx-auto, vault-note]\n"
            f"---\n\n"
            f"# {note_title}\n\n"
            f"{content}\n"
        )
    else:
        obsidian_note = content

    try:
        # บันทึกไฟล์ลงฮาร์ดดิสก์แบบปลอดภัย
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(obsidian_note)
            
        return {
            "status": "success",
            "result": f"บันทึกไฟล์สืบค้น Obsidian สำเร็จแล้ว พิกัด: {os.path.relpath(safe_path)}",
            "filename": filename
        }
    except Exception as e:
        return {"status": "fail", "message": f"ไม่สามารถเขียนไฟล์ได้: {type(e).__name__} - {str(e)}"}


def handle_vault_read(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    อ่านเนื้อหาไฟล์ Markdown จาก Obsidian Vault
    """
    filename = ""
    for ent in entities:
        if ent.endswith((".md", ".txt")):
            filename = ent
            break
            
    if not filename:
        return {"status": "fail", "message": "ไม่ระบุชื่อไฟล์ที่ต้องการอ่าน"}

    # ป้องกัน Directory Traversal
    safe_path = os.path.abspath(os.path.join(VAULT_DIR, filename))
    if not safe_path.startswith(os.path.abspath(VAULT_DIR)):
        return {"status": "fail", "message": "ปฏิเสธการดำเนินการ: เส้นทางระบุไฟล์มีความเสี่ยงทางความปลอดภัย"}

    if not os.path.exists(safe_path):
        return {"status": "fail", "message": f"ไม่พบไฟล์ชื่อ '{filename}' ในระบบฐานความรู้"}

    try:
        with open(safe_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "status": "success",
            "result": content,
            "filename": filename
        }
    except Exception as e:
        return {"status": "fail", "message": f"ไม่สามารถอ่านไฟล์ได้: {str(e)}"}


def handle_vault_list(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    ดึงรายชื่อไฟล์ทั้งหมดที่จัดเก็บอยู่ภายใน Obsidian Vault
    """
    if not os.path.exists(VAULT_DIR):
        return {"status": "success", "result": "ไม่พบคลังข้อมูล Obsidian Vault (ยังว่างอยู่)"}

    try:
        files = [f for f in os.listdir(VAULT_DIR) if f.endswith(".md")]
        if not files:
            return {"status": "success", "result": "ไม่มีไฟล์โน้ต Markdown อยู่ใน Obsidian Vault"}
            
        formatted_list = "\n".join(f"- 📄 {f}" for f in files)
        return {
            "status": "success",
            "result": f"พบไฟล์เอกสารใน Obsidian Vault ทั้งหมด {len(files)} รายการดังนี้:\n{formatted_list}"
        }
    except Exception as e:
        return {"status": "fail", "message": f"ไม่สามารถดึงรายชื่อไฟล์ได้: {str(e)}"}