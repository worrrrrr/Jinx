"""
Base utilities for all tools
"""
from typing import Dict, Any, Optional
import re

def sanitize_input(text: str, allowed_chars: str = None) -> str:
    """ล้างอักขระอันตรายจาก input"""
    if allowed_chars:
        return "".join(c for c in text if c in allowed_chars)
    # Default: ลบ control characters
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

def safe_eval(expr: str, safe_dict: Dict = None) -> Any:
    """eval อย่างปลอดภัย"""
    if safe_dict is None:
        safe_dict = {"__builtins__": None}
    return eval(expr, safe_dict)

def format_result(value: Any, precision: int = 6) -> Any:
    """จัดรูปแบบผลลัพธ์ให้อ่านง่าย"""
    if isinstance(value, float):
        return round(value, precision) if abs(value) < 1e10 else value
    return value

def get_tools():
    """Export utilities as tools (optional)"""
    return {
        "sanitize": sanitize_input,
        "format": format_result
    }