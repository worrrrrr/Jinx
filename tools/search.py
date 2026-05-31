# tools/search.py

import os
import re
from typing import Dict, Any, List, Callable

# กำหนดตำแหน่งโฟลเดอร์เก็บข้อมูลความรู้หลัก (Knowledge Base)
DEFAULT_KNOWLEDGE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge"
)


def get_tools() -> Dict[str, Callable]:
    """
    ส่งคืนพจนานุกรมของเครื่องมือสำหรับการลงทะเบียนเข้าสู่ ExecutionEngine
    """
    return {
        "web_search": search_local_knowledge,
        "search": search_local_knowledge,
    }


def search_local_knowledge(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    ค้นหาข้อมูลเชิงลึกในระบบไฟล์ความรู้โลคัล (.md) จำลองกลไกการสืบค้น (Grep-based Search)
    """
    # 1. กำหนดคำค้นหาหลัก (Query Extraction)
    query = inp.strip() if inp else ""
    if not query and entities:
        query = entities[0].strip()

    if not query:
        return {"status": "fail", "message": "ไม่พบระบุคำค้นหา (Query)"}

    # ตรวจหาตำแหน่งโฟลเดอร์ (Resilient Fallback)
    kb_dir = DEFAULT_KNOWLEDGE_DIR
    if not os.path.exists(kb_dir):
        kb_dir = os.path.join("data", "knowledge")
        if not os.path.exists(kb_dir):
            return {"status": "fail", "message": f"ไม่พบโฟลเดอร์ฐานข้อมูลความรู้ที่กำหนด: {kb_dir}"}

    results = []
    try:
        # 2. ค้นหาไฟล์เอกสาร Markdown ทั้งหมดในโฟลเดอร์ย่อย
        for root, _, files in os.walk(kb_dir):
            for file in files:
                if file.endswith((".md", ".txt", ".json")):
                    file_path = os.path.join(root, file)
                    matches = _grep_file(file_path, query)
                    if matches:
                        results.extend(matches)

        # 3. ส่งคืนผลลัพธ์การค้นหา
        if results:
            return {
                "status": "success",
                "result": results[:5],  # จำกัดผลลัพธ์การแสดงผลสูงสุด 5 รายการที่ตรงที่สุด
                "query": query,
                "engine": "local_grep"
            }
        else:
            return {
                "status": "success",
                "result": f"ไม่พบข้อมูลที่ตรงกับคำค้นหา '{query}' ในระบบฐานความรู้",
                "query": query,
                "engine": "local_grep"
            }

    except Exception as e:
        return {"status": "fail", "message": f"Search Error: {type(e).__name__} - {str(e)}"}


def _grep_file(file_path: str, query: str) -> List[Dict[str, Any]]:
    """
    สแกนข้อความในไฟล์เป้าหมายทีละบรรทัด พร้อมสกัดเนื้อหาบริบทโดยรอบ (Context Snippet)
    """
    matches = []
    filename = os.path.basename(file_path)
    
    try:
        # เปิดอ่านไฟล์อย่างปลอดภัยด้วย UTF-8
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            # ตรวจจับข้อความแบบไม่สนใจตัวพิมพ์เล็กพิมพ์ใหญ่ (Case-Insensitive Search)
            if re.search(re.escape(query), line, re.IGNORECASE):
                # สกัดบริบทโดยรอบบรรทัดที่เจอ (ก่อนหน้า 1 บรรทัด และหลัง 2 บรรทัด)
                start_idx = max(0, idx - 1)
                end_idx = min(len(lines), idx + 2)
                snippet_lines = [l.strip() for l in lines[start_idx:end_idx] if l.strip()]
                snippet = " ... ".join(snippet_lines)
                
                matches.append({
                    "title": filename,
                    "snippet": snippet,
                    "source": os.path.relpath(file_path),
                    "line_number": idx + 1
                })
                
                # เก็บผลลัพธ์สูงสุดไม่เกิน 2 รายการต่อ 1 ไฟล์ เพื่อความกระชับ
                if len(matches) >= 2:
                    break
                    
    except Exception:
        pass  # ข้ามไฟล์ที่ไม่สามารถเปิดอ่านระบบความปลอดภัยได้
        
    return matches