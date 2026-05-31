# tools/obsidian.py

import os
import re
import datetime
from typing import Dict, Any, List, Callable

# กำหนดพิกัดความปลอดภัยของ Obsidian Vault (data/knowledge)
VAULT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge"
)


def get_tools() -> Dict[str, Callable]:
    """
    ส่งคืนพจนานุกรมของเครื่องมือสำหรับลงทะเบียนใน ExecutionEngine
    """
    return {
        "create_note": create_obsidian_note,
        "append_note": append_obsidian_note,
        "link_notes": link_obsidian_notes,
    }


def create_obsidian_note(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    สร้างโน้ต Markdown ใหม่ พร้อมจัดฟอร์แมต Obsidian Frontmatter อัตโนมัติ
    """
    os.makedirs(VAULT_DIR, exist_ok=True)
    
    filename = _extract_md_filename(entities, inp)
    safe_path = _get_safe_path(filename)
    if not safe_path:
        return {"status": "fail", "message": "ปฏิเสธการเข้าถึง: ตรวจพบความเสี่ยงด้านความปลอดภัยของพาธระบุไฟล์"}

    # คัดกรองเนื้อหาหลัก
    content = _clean_math_and_commands(inp, filename)
    
    # จัดรูปโครงสร้าง Frontmatter ของ Obsidian
    today_str = datetime.date.today().isoformat()
    title = os.path.splitext(filename)[0]
    
    formatted_note = (
        f"---\n"
        f"created: {today_str}\n"
        f"tags: [jinx-agent, automatic-note]\n"
        f"status: draft\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"{content}\n"
    )

    try:
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(formatted_note)
        return {
            "status": "success",
            "result": f"สร้างโน้ต Obsidian สำเร็จแล้ว: [[{title}]] ที่พิกัด '{os.path.relpath(safe_path)}'",
            "filename": filename
        }
    except Exception as e:
        return {"status": "fail", "message": f"ไม่สามารถสร้างโน้ตได้: {str(e)}"}


def append_obsidian_note(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    ต่อเติมเนื้อหาลงในโน้ตเป้าหมายเดิม พร้อมบันทึกตราประทับเวลา (Timestamp Logging)
    """
    os.makedirs(VAULT_DIR, exist_ok=True)
    
    filename = _extract_md_filename(entities, inp)
    safe_path = _get_safe_path(filename)
    if not safe_path:
        return {"status": "fail", "message": "ปฏิเสธการเข้าถึง: พาธเป้าหมายไม่ปลอดภัย"}

    if not os.path.exists(safe_path):
        # หากไม่พบไฟล์เดิมในระบบ ให้สลับไปสร้างไฟล์ใหม่แทนเพื่อป้องกันความเสียหาย
        return create_obsidian_note(action, inp, entities)

    content_to_append = _clean_math_and_commands(inp, filename)
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        # บันทึกแบบต่อท้ายไฟล์ (Append Mode)
        with open(safe_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n### 📝 บันทึกเมื่อ {timestamp_str}\n- {content_to_append}\n")
        
        title = os.path.splitext(filename)[0]
        return {
            "status": "success",
            "result": f"ต่อเติมข้อมูลลงในโน้ต [[{title}]] เรียบร้อยแล้ว",
            "filename": filename
        }
    except Exception as e:
        return {"status": "fail", "message": f"ไม่สามารถแก้ไขไฟล์ได้: {str(e)}"}


def link_obsidian_notes(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    เชื่อมโยงความสัมพันธ์ของโน้ตหลักไปยังโน้ตเป้าหมายย่อยด้วยรูปแบบ [[Note Name]]
    """
    # ตรวจสอบชื่อไฟล์ทั้งสองไฟล์ (ต้องส่งมาในรูปของ Entities 2 ตัวขึ้นไป)
    md_files = [e for e in entities if e.endswith(".md")]
    if len(md_files) < 2:
        # พยายามดึงคีย์ชื่อไฟล์จากตัวอักษรภาษาอังกฤษเปรียบเทียบกรณีไม่มี entity สมบูรณ์
        found_files = re.findall(r"\b[a-zA-Z0-9_\-.]+\.md\b", inp)
        md_files.extend(found_files)
        md_files = list(set(md_files))

    if len(md_files) < 2:
        return {"status": "fail", "message": "กรุณาระบุชื่อโน้ตต้นทางและโน้ตปลายทางที่ต้องการสร้างลิงก์เชื่อมโยง"}

    source_file = md_files[0]
    target_note_name = os.path.splitext(md_files[1])[0]

    safe_path = _get_safe_path(source_file)
    if not safe_path or not os.path.exists(safe_path):
        return {"status": "fail", "message": f"ไม่พบไฟล์ต้นทางชื่อ '{source_file}' ในระบบฐานข้อมูล"}

    try:
        # เปิดไฟล์เพื่อทำการแทรกลิงก์ที่ท้ายเอกสาร
        with open(safe_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n**ลิงก์เชื่อมโยง**: [[{target_note_name}]]\n")
            
        source_title = os.path.splitext(source_file)[0]
        return {
            "status": "success",
            "result": f"สร้างสะพานเชื่อมโยงความรู้เรียบร้อยแล้ว: [[{source_title}]] $\\rightarrow$ [[{target_note_name}]]"
        }
    except Exception as e:
        return {"status": "fail", "message": f"ไม่สามารถสร้างลิงก์ได้: {str(e)}"}


# ==========================================
# ฟังก์ชันช่วยเหลือภายในคลาส (Internal Helpers)
# ==========================================

def _extract_md_filename(entities: List[str], inp: str) -> str:
    """สกัดค้นหาชื่อไฟล์ Markdown จาก Entities หรือสตริงประโยคนำเข้า"""
    for ent in entities:
        if ent.endswith(".md"):
            return ent
            
    # หากไม่พบใน Entities ให้ใช้ Regex มองหาในประโยค
    found = re.search(r"\b([a-zA-Z0-9_\-.]+)\.md\b", inp)
    if found:
        return found.group(0)
        
    # หากยังไม่พบเลย ให้ใช้ชื่อเริ่มต้นตามเวลาเซสชันปัจจุบันเพื่อเลี่ยงปัญหาตัวแปรว่าง
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"note_{timestamp}.md"


def _get_safe_path(filename: str) -> Optional[str]:
    """สแกนตรวจสอบพาธจริงเพื่อป้องกันการโจมตี Directory Traversal"""
    safe_path = os.path.abspath(os.path.join(VAULT_DIR, filename))
    if safe_path.startswith(os.path.abspath(VAULT_DIR)):
        return safe_path
    return None


def _clean_math_and_commands(text: str, filename: str) -> str:
    """ขจัดคีย์สั่งและคำเฉพาะทางที่ไม่เกี่ยวข้องออกจากเนื้อหาเพื่อความสะอาด"""
    clean = re.sub(r"สร้างไฟล์|สร้างโน้ต|เขียนไฟล์|บันทึก|บันทึกทับ|ต่อเติม|เขียนโน้ต", "", text)
    clean = clean.replace(filename, "").strip()
    return clean