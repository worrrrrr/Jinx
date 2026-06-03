# tools/decision_tree.py — Decision Tree Engine

import json
import os
import re
from typing import Dict, Any, List, Callable, Optional


def get_tools() -> Dict[str, Callable]:
    return {
        "decision_tree": decision_tree_handler,
        "tree": decision_tree_handler,
    }


TREES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "trees"
)


def decision_tree_handler(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    เดิน tree ตามเงื่อนไข
    รูปแบบ: "tree_name" หรือ "tree_name คำตอบ1, คำตอบ2" หรือ "tree_name --reset"
    """
    parts = inp.strip().split(maxsplit=1)
    tree_name = parts[0] if parts else ""
    user_input = parts[1] if len(parts) > 1 else ""

    if not tree_name:
        return {"status": "fail", "message": "ไม่ระบุชื่อ decision tree"}

    if user_input.strip().lower() in ("--reset", "-r"):
        _clear_state(tree_name)
        return {"status": "success", "result": f"รีเซ็ต tree '{tree_name}' เรียบร้อย"}

    tree = _load_tree(tree_name)
    if tree is None:
        return {"status": "fail", "message": f"ไม่พบ decision tree '{tree_name}'"}

    state = _load_state(tree_name)
    current_node_id = state.get("node", tree.get("start", "start"))
    node = _find_node(tree, current_node_id)

    if node is None:
        return {"status": "fail", "message": f"tree '{tree_name}' ไม่สมบูรณ์: ไม่พบ node '{current_node_id}'"}

    # ถ้ามี input และ node มี choices
    if user_input and "choices" in node:
        choice = _match_choice(node["choices"], user_input)
        if choice is None:
            options = [c.get("label", c.get("id", "?")) for c in node["choices"]]
            return {
                "status": "success",
                "result": f"ไม่รู้จัก '{user_input}' — ตัวเลือก: {', '.join(options)}",
            }
        next_id = choice.get("next")
        if not next_id:
            return {"status": "success", "result": choice.get("result", "จบ")}
        state["node"] = next_id
        _save_state(tree_name, state)
        next_node = _find_node(tree, next_id)
        if next_node and "question" in next_node:
            return {
                "status": "success",
                "result": f"{next_node['question']}\n{_format_choices(next_node.get('choices', []))}",
                "node": next_id,
            }
        if next_node and "result" in next_node:
            _clear_state(tree_name)
            return {"status": "success", "result": next_node["result"]}

    # แสดง node ปัจจุบัน
    if "question" in node:
        return {
            "status": "success",
            "result": f"{node['question']}\n{_format_choices(node.get('choices', []))}",
            "node": current_node_id,
        }
    if "result" in node:
        _clear_state(tree_name)
        return {"status": "success", "result": node["result"]}

    return {"status": "success", "result": f"node '{current_node_id}' ไม่มีข้อมูล"}


def _load_tree(name: str) -> Optional[Dict[str, Any]]:
    """โหลด tree definition จาก data/trees/<name>.json"""
    os.makedirs(TREES_DIR, exist_ok=True)
    path = os.path.join(TREES_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_state(name: str) -> Dict[str, Any]:
    path = os.path.join(TREES_DIR, f"_state_{name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_state(name: str, state: Dict[str, Any]):
    os.makedirs(TREES_DIR, exist_ok=True)
    path = os.path.join(TREES_DIR, f"_state_{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def _clear_state(name: str):
    path = os.path.join(TREES_DIR, f"_state_{name}.json")
    if os.path.exists(path):
        os.remove(path)


def _find_node(tree: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
    for node in tree.get("nodes", []):
        if node.get("id") == node_id:
            return node
    return None


def _match_choice(choices: List[Dict[str, Any]], user_input: str) -> Optional[Dict[str, Any]]:
    inp_lower = user_input.strip().lower()
    for choice in choices:
        label = choice.get("label", "").lower()
        keywords = choice.get("keywords", [])
        if label == inp_lower:
            return choice
        if inp_lower in [k.lower() for k in keywords]:
            return choice
        if any(kw.lower() in inp_lower for kw in keywords):
            return choice
    return None


def _format_choices(choices: List[Dict[str, Any]]) -> str:
    if not choices:
        return ""
    return "\n".join(f"  • {c.get('label', c.get('id', '?'))}" for c in choices)
