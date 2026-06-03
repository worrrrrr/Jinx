# tools/state_manager.py — State Machine for multi-step workflows

import json
import os
from typing import Dict, Any, List, Callable, Optional


def get_tools() -> Dict[str, Callable]:
    return {
        "state_machine": state_machine_handler,
        "state": state_machine_handler,
    }


MACHINES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "machines"
)


def state_machine_handler(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    จัดการ state machine
    รูปแบบ: "machine_name" — แสดงสถานะปัจจุบัน
            "machine_name event_name" — ส่ง event เพื่อเปลี่ยนสถานะ
            "machine_name --reset" — รีเซ็ต
            "machine_name --show" — แสดงแผนภาพ
    """
    parts = inp.strip().split(maxsplit=1)
    machine_name = parts[0] if parts else ""
    arg = parts[1] if len(parts) > 1 else ""

    if not machine_name:
        return {"status": "fail", "message": "ไม่ระบุชื่อ state machine"}

    machine = _load_machine(machine_name)
    if machine is None:
        return {"status": "fail", "message": f"ไม่พบ state machine '{machine_name}'"}

    if arg.strip().lower() in ("--reset", "-r"):
        _reset_state(machine_name, machine)
        state = _load_state(machine_name)
        return {
            "status": "success",
            "result": f"รีเซ็ต '{machine_name}' เรียบร้อย สถานะ: {state.get('current', '?')}",
        }

    if arg.strip().lower() in ("--show", "-s"):
        return {
            "status": "success",
            "result": _format_diagram(machine),
        }

    state = _load_state(machine_name)
    current = state.get("current", machine.get("start", "idle"))

    if arg:
        event = arg.strip()
        result = _transition(machine, current, event)
        if result is None:
            return {
                "status": "fail",
                "message": f"จากสถานะ '{current}' ไม่มี transition สำหรับ event '{event}'",
            }
        state["current"] = result
        _save_state(machine_name, state)
        return {
            "status": "success",
            "result": f"Event '{event}': {current} → {result}",
            "from": current,
            "to": result,
            "event": event,
        }

    return {
        "status": "success",
        "result": f"สถานะปัจจุบันของ '{machine_name}': {current}",
        "current": current,
    }


def _load_machine(name: str) -> Optional[Dict[str, Any]]:
    os.makedirs(MACHINES_DIR, exist_ok=True)
    path = os.path.join(MACHINES_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_state(name: str) -> Dict[str, Any]:
    path = os.path.join(MACHINES_DIR, f"_state_{name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_state(name: str, state: Dict[str, Any]):
    os.makedirs(MACHINES_DIR, exist_ok=True)
    path = os.path.join(MACHINES_DIR, f"_state_{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def _clear_state(name: str):
    path = os.path.join(MACHINES_DIR, f"_state_{name}.json")
    if os.path.exists(path):
        os.remove(path)


def _reset_state(name: str, machine: Dict[str, Any]):
    state = {"current": machine.get("start", "idle")}
    _save_state(name, state)


def _transition(machine: Dict[str, Any], current: str, event: str) -> Optional[str]:
    for t in machine.get("transitions", []):
        if t.get("from") == current and t.get("event") == event:
            # ตรวจสอบ guard (optional)
            return t.get("to")
        if t.get("from") == "*" and t.get("event") == event:
            return t.get("to")
    return None


def _format_diagram(machine: Dict[str, Any]) -> str:
    lines = [f"📍 State Machine: {machine.get('name', 'unknown')}"]
    lines.append(f"  Start: {machine.get('start', 'idle')}")
    for t in machine.get("transitions", []):
        guard = f" [guard: {t['guard']}]" if "guard" in t else ""
        lines.append(f"  {t['from']} --({t['event']})--> {t['to']}{guard}")
    return "\n".join(lines)
