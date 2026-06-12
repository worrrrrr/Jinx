import os
import glob
from typing import Any, Dict

# พยายามใช้ ddgs (ใหม่) ก่อน ถ้าไม่ได้ค่อยใช้ duckduckgo_search (เก่า)
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None  # ไม่มี module เลย

# กำหนด Path ข้อมูล
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def search_local_knowledge(query: str) -> str:
    """อ่านข้อมูลจากไฟล์ใน data/"""
    results = []
    search_path = os.path.join(DATA_DIR, "**", "*.*")
    for file_path in glob.glob(search_path, recursive=True):
        if file_path.endswith(('.md', '.txt', '.json')):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        results.append(f"[{os.path.basename(file_path)}]: {content[:150]}...")
            except Exception:
                continue
    return "\n".join(results) if results else ""

def search_web(query: str) -> str:
    """ออกไปหาข้อมูลจาก Google (ผ่าน DuckDuckGo/DDGS)"""
    if DDGS is None:
        return "Error: ไม่พบ module สำหรับค้นหาเว็บ (ติดตั้ง ddgs หรือ duckduckgo_search)"
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return f"No results found for '{query}'"
            formatted = [f"Web: {r['body']}" for r in results]
            return "\n".join(formatted)
    except Exception as e:
        return f"Error connecting to web: {str(e)}"

def search_handler(action: str = "search", query: str = "", entities: list = None, **kwargs) -> Dict[str, Any]:
    """Smart Orchestrator: ค้นหาในเครื่องก่อน ถ้าไม่เจอค่อยไปนอก
    รองรับทั้งการเรียกแบบ action-based และ query-based
    """
    # จัดการ input ให้ยืดหยุ่น
    if entities is None:
        entities = []
    
    # ถ้ามี action แต่ไม่มี query ให้ลองดึงจาก entities
    if not query and entities:
        query = " ".join(str(e) for e in entities)
    
    # ถ้ายังไม่มี query เลย
    if not query:
        query = "unknown query"
    
    print(f"🔍 Jinx กำลังหาข้อมูล: '{query}'")
    
    try:
        # 1. ค้นใน Local
        local_data = search_local_knowledge(query)
        if local_data:
            print("✅ พบข้อมูลใน Local")
            return {"status": "success", "result": f"พบข้อมูลในเครื่อง:\n{local_data}"}
        
        # 2. ค้นใน Web (Fallback)
        print("🌐 ไม่พบในเครื่อง! กำลังออกไปค้นหาข้อมูลจาก Web...")
        web_data = search_web(query)
        
        if web_data and "Error" not in web_data:
            return {"status": "success", "result": f"ไม่พบในเครื่อง แต่พบจาก Web:\n{web_data}"}
        else:
            return {
                "status": "partial", 
                "result": f"ไม่พบข้อมูลสำหรับ '{query}' ทั้งในเครื่องและบนเว็บ",
                "warning": web_data if "Error" in web_data else None
            }
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการค้นหา: {str(e)}")
        return {
            "status": "error",
            "result": f"เกิดข้อผิดพลาดในการค้นหาข้อมูล: {str(e)}",
            "error_type": type(e).__name__
        }

def get_tools():
    return {
        "search": search_handler,
        "answer_question": search_handler,
    }