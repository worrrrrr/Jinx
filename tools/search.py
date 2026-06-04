import os
import glob
from typing import Any, Dict
from duckduckgo_search import DDGS

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
    """ออกไปหาข้อมูลจาก Google (ผ่าน DuckDuckGo)"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            formatted = [f"Web: {r['body']}" for r in results]
            return "\n".join(formatted)
    except Exception as e:
        return f"Error connecting to web: {str(e)}"

def search_handler(query: str, **kwargs) -> Dict[str, Any]:
    """Smart Orchestrator: ค้นหาในเครื่องก่อน ถ้าไม่เจอค่อยไปนอก"""
    print(f"🔍 Jinx กำลังหาข้อมูล: '{query}'")
    
    # 1. ค้นใน Local
    local_data = search_local_knowledge(query)
    if local_data:
        print("✅ พบข้อมูลใน Local")
        return {"status": "success", "result": f"พบข้อมูลในเครื่อง:\n{local_data}"}
    
    # 2. ค้นใน Web (Fallback)
    print("🌐 ไม่พบในเครื่อง! กำลังออกไปค้นหาข้อมูลจาก Web...")
    web_data = search_web(query)
    return {"status": "success", "result": f"ไม่พบในเครื่อง แต่พบจาก Web:\n{web_data}"}

def get_tools():
    return {
        "search": search_handler,
        "answer_question": search_handler,
    }