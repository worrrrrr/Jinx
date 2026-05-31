# core/memory.py

from typing import Dict, Any, List, Optional
import collections


class SessionMemory:
    """
    Short-Term Context & Variable Memory: ระบบจดจำประวัติสนทนาและจำค่าตัวแปรคณิตศาสตร์
    """
    
    def __init__(self, max_history: int = 10):
        # คิวประวัติการสนทนา (จำกัดความยาวเพื่อประหยัดหน่วยความจำ)
        self.history: collections.deque = collections.deque(maxlen=max_history)
        
        # คลังจดจำค่าตัวแปรจากการคำนวณ (เช่น x = 9.6, y = 2.4)
        self.variables: Dict[str, Any] = {}
        
        # สถานะการตอบกลับล่าสุดและข้อมูลบริบท (Context States)
        self.context: Dict[str, Any] = {}

    def add_turn(self, user_message: str, agent_response: str):
        """
        บันทึกคู่ประวัติการสนทนา (Turn)
        """
        self.history.append({
            "user": user_message.strip(),
            "jinx": agent_response.strip()
        })

    def store_variables(self, new_vars: Dict[str, Any]):
        """
        จดจำค่าตัวแปรที่คำนวณได้ เช่น x, y เพื่อใช้อ้างอิงใน Turn ถัดไป
        """
        for k, v in new_vars.items():
            # เก็บเฉพาะคีย์ตัวแปรที่เป็นตัวอักษรภาษาอังกฤษเดี่ยวตามมาตรฐานคณิตศาสตร์
            if isinstance(k, str) and k.strip().isalpha() and len(k.strip()) == 1:
                self.variables[k.strip()] = v

    def get_variable(self, name: str) -> Optional[Any]:
        """
        ดึงค่าตัวแปรที่บันทึกไว้
        """
        return self.variables.get(name.strip())

    def update_context(self, key: str, value: Any):
        """
        อัปเดตค่าสถานะบริบท เช่น สถานะพิกัดไฟล์ หรือคำค้นหาล่าสุด
        """
        self.context[key] = value

    def get_context(self, key: str, default: Optional[Any] = None) -> Any:
        return self.context.get(key, default)

    def get_all_variables_str(self) -> str:
        """
        แปลงค่าตัวแปรที่จดจำทั้งหมดในระบบความทรงจำออกมาในรูปแบบ String
        """
        if not self.variables:
            return ""
        return ", ".join(f"{k} = {v}" for k, v in self.variables.items())

    def get_history_summary(self) -> List[Dict[str, str]]:
        """
        สกัดข้อมูลประวัติการสนทนาในรูปแบบ List
        """
        return list(self.history)

    def clear(self):
        """
        ลบความจำในระบบทั้งหมด
        """
        self.history.clear()
        self.variables.clear()
        self.context.clear()