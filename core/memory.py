# core/memory.py

import collections
import json
import os
import re
from typing import Dict, Any, List, Optional


PERSISTENCE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "session_memory.json"
)


class SessionMemory:
    """
    Short-Term Context & Variable Memory: ระบบจดจำประวัติสนทนาและจำค่าตัวแปรคณิตศาสตร์
    """
    
    def __init__(self, max_history: int = 10, persist_path: Optional[str] = None):
        self.persist_path = persist_path
        
        # คิวประวัติการสนทนา (จำกัดความยาวเพื่อประหยัดหน่วยความจำ)
        self.history: collections.deque = collections.deque(maxlen=max_history)
        
        # คลังจดจำค่าตัวแปรจากการคำนวณ (เช่น x = 9.6, y = 2.4)
        self.variables: Dict[str, Any] = {}
        
        # สถานะการตอบกลับล่าสุดและข้อมูลบริบท (Context States)
        self.context: Dict[str, Any] = {}
        
        # โหลดประวัติจากไฟล์ถ้ามี
        self._load_persistent()

    def _load_persistent(self):
        if not self.persist_path or not os.path.exists(self.persist_path):
            return
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for turn in data.get("history", []):
                self.history.append(turn)
            self.variables.update(data.get("variables", {}))
            self.context.update(data.get("context", {}))
        except (json.JSONDecodeError, OSError):
            pass

    def _save_persistent(self):
        if not self.persist_path:
            return
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
        data = {
            "history": list(self.history),
            "variables": {k: v for k, v in self.variables.items() if isinstance(v, (int, float, str))},
            "context": self.context,
        }
        try:
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def add_turn(self, user_message: str, agent_response: str):
        """
        บันทึกคู่ประวัติการสนทนา (Turn)
        """
        self.history.append({
            "user": user_message.strip(),
            "jinx": agent_response.strip()
        })
        self._save_persistent()

    def store_variables(self, new_vars: Dict[str, Any]):
        """
        จดจำค่าตัวแปรที่คำนวณได้ เช่น x, y เพื่อใช้อ้างอิงใน Turn ถัดไป
        """
        for k, v in new_vars.items():
            # เก็บเฉพาะคีย์ตัวแปรที่เป็นตัวอักษรภาษาอังกฤษเดี่ยวตามมาตรฐานคณิตศาสตร์
            var_name = _var_name_from_key(k) if not isinstance(k, str) else (
                k.strip() if len(k.strip()) == 1 and k.strip().isalpha() else None
            )
            if var_name:
                self.variables[var_name] = _normalize_var_value(v)
        self._save_persistent()

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
        self._save_persistent()

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
        self._save_persistent()


def _var_name_from_key(key: Any) -> Optional[str]:
    if isinstance(key, str) and len(key.strip()) == 1 and key.strip().isalpha():
        return key.strip()
    sym_name = getattr(key, "name", None)
    if isinstance(sym_name, str) and len(sym_name) == 1 and sym_name.isalpha():
        return sym_name
    return None


def _normalize_var_value(val: Any) -> Any:
    if hasattr(val, "evalf") and callable(val.evalf):
        try:
            return float(val.evalf())
        except (TypeError, ValueError):
            pass
    return val


def extract_variables_from_result(result: Any) -> Dict[str, Any]:
    """
    ดึงค่าตัวแปรตัวอักษรเดี่ยวจากผลลัพธ์เครื่องมือคณิต (dict / list ของ dict)
    """
    found: Dict[str, Any] = {}

    if isinstance(result, dict):
        for key, val in result.items():
            name = _var_name_from_key(key)
            if name and val is not None:
                found[name] = _normalize_var_value(val)
        return found

    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict):
                branch = extract_variables_from_result(item)
                if branch:
                    return branch
        return found

    return found


def substitute_variables_in_text(text: str, variables: Dict[str, Any]) -> str:
    """แทนที่ตัวแปรที่จำไว้ในสมการ (เฉพาะตัวอักษรเดี่ยว) ก่อนส่งให้เครื่องมือคณิต."""
    if not text or not variables:
        return text
    out = text
    for name, value in variables.items():
        if not (isinstance(name, str) and len(name) == 1 and name.isalpha()):
            continue
        out = re.sub(rf"\b{re.escape(name)}\b", str(value), out)
    return out