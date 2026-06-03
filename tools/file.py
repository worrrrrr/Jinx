# tools/file.py — Workspace file operations (โปรเจกต์ Jinx ไม่รวม data/knowledge vault)

import os
import re
from typing import Dict, Any, List, Callable, Optional, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DIR = os.path.join(PROJECT_ROOT, "data", "knowledge")

CODE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".json", ".yaml", ".yml", ".toml", ".html", ".css"}
TEXT_EXTENSIONS = CODE_EXTENSIONS | {".md", ".txt", ".ini", ".cfg", ".env.example"}
BLOCKED_PARTS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}
BLOCKED_FILES = {".env"}

CODE_FENCE_RE = re.compile(r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
FILENAME_RE = re.compile(
    r"([a-zA-Z0-9_\-./\\]+(?:\.(?:py|ts|tsx|js|json|md|txt|yaml|yml|toml|html|css)))"
)
PATH_FILE_RE = re.compile(
    r"(?:[\w\-]+/)+[\w\-\.]+\.(?:py|ts|tsx|js|json|md|txt|yaml|yml|toml|html|css)"
    r"|[\w\-\.]+\.(?:py|ts|tsx|js|json|md|txt|yaml|yml|toml|html|css)",
    re.IGNORECASE,
)


def get_tools() -> Dict[str, Callable]:
    return {
        "write_code": workspace_write,
        "create_code": workspace_write,
        "update_code": workspace_write,
        "read_code": workspace_read,
        "read_workspace": workspace_read,
        "list_workspace": workspace_list,
        "list_dir": workspace_list,
        "apply_patch": workspace_apply_patch,
        "run_script": workspace_run_script,
        "debug_code": workspace_read,
    }


def resolve_workspace_path(relative_path: str) -> Tuple[Optional[str], Optional[str]]:
    """คืน (absolute_path, error_message)."""
    if not relative_path or not str(relative_path).strip():
        return None, "ไม่ระบุ path ไฟล์"

    rel = str(relative_path).strip().replace("\\", "/").lstrip("/")
    if ".." in rel.split("/"):
        return None, "ปฏิเสธ path: ห้ามใช้ .."

    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, rel))
    root = os.path.normpath(PROJECT_ROOT)
    vault = os.path.normpath(VAULT_DIR)

    if not abs_path.startswith(root):
        return None, "ปฏิเสธ path: อยู่นอก workspace"

    # ห้ามเขียนทับ vault ผ่าน workspace tool (ใช้ obsidian/utils แทน)
    if abs_path.startswith(vault):
        return None, "ใช้ vault tools สำหรับ data/knowledge/"

    rel_parts = rel.split("/")
    if any(part in BLOCKED_PARTS for part in rel_parts):
        return None, "ปฏิเสธ path: โฟลเดอร์ระบบ"

    if os.path.basename(abs_path) in BLOCKED_FILES:
        return None, "ปฏิเสธ path: ไฟล์นี้ห้ามแก้ไข"

    ext = os.path.splitext(abs_path)[1].lower()
    if ext and ext not in TEXT_EXTENSIONS:
        return None, f"ปฏิเสธนามสกุลไฟล์: {ext}"

    return abs_path, None


def pick_filename(entities: List[str], inp: str) -> Optional[str]:
    candidates: List[str] = []
    text = inp or ""

    for m in PATH_FILE_RE.finditer(text):
        candidates.append(m.group(0).replace("\\", "/").lstrip("/"))

    for match in FILENAME_RE.findall(text):
        if not match.startswith("http"):
            candidates.append(match.replace("\\", "/").lstrip("/"))

    for ent in entities:
        if not isinstance(ent, str) or ent in ("/", "\\", "."):
            continue
        if "." in ent and not ent.startswith("http"):
            candidates.append(ent.replace("\\", "/").lstrip("/"))

    if not candidates:
        return None
    return max(candidates, key=len)


def extract_code_content(inp: str, filename: str) -> str:
    if not inp:
        return ""
    m = CODE_FENCE_RE.search(inp)
    if m:
        return m.group(1).strip()

    text = inp.strip()
    for ent in [filename] + list(FILENAME_RE.findall(text)):
        text = text.replace(ent, "")
    strip_prefixes = [
        r"^(?:สร้าง|เขียน|แก้ไข|อัปเดต|create|write|update|edit)\s*(?:ไฟล์|file|โค้ด|code)?\s*",
        r"^(?:ให้|with|content|เนื้อหา)\s*",
    ]
    for pat in strip_prefixes:
        text = re.sub(pat, "", text, flags=re.IGNORECASE).strip()

    return text.strip()


def workspace_write(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    filename = pick_filename(entities, inp)
    if not filename:
        return {"status": "fail", "message": "ไม่พบชื่อไฟล์ (เช่น scripts/hello.py)"}

    safe_path, err = resolve_workspace_path(filename)
    if err:
        return {"status": "fail", "message": err}

    content = extract_code_content(inp, filename)
    if not content:
        return {"status": "fail", "message": "ไม่พบเนื้อหาโค้ด — ใส่ใน ```python ... ``` หรือหลังชื่อไฟล์"}

    os.makedirs(os.path.dirname(safe_path), exist_ok=True)
    existed = os.path.exists(safe_path)
    try:
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")
        rel = os.path.relpath(safe_path, PROJECT_ROOT)
        verb = "อัปเดต" if existed else "สร้าง"
        return {
            "status": "success",
            "result": f"{verb}ไฟล์ {rel} ({len(content)} ตัวอักษร)",
            "path": rel,
            "bytes": len(content.encode("utf-8")),
        }
    except OSError as e:
        return {"status": "fail", "message": f"เขียนไฟล์ไม่สำเร็จ: {e}"}


def workspace_read(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    filename = pick_filename(entities, inp) or (inp.strip() if inp else None)
    if not filename:
        return {"status": "fail", "message": "ไม่ระบุไฟล์ที่ต้องการอ่าน"}

    safe_path, err = resolve_workspace_path(filename)
    if err:
        return {"status": "fail", "message": err}

    if not os.path.isfile(safe_path):
        return {"status": "fail", "message": f"ไม่พบไฟล์: {os.path.relpath(safe_path, PROJECT_ROOT)}"}

    try:
        with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        rel = os.path.relpath(safe_path, PROJECT_ROOT)
        preview = content if len(content) <= 2000 else content[:2000] + "\n... (ตัดทอน)"
        return {
            "status": "success",
            "result": preview,
            "path": rel,
            "lines": content.count("\n") + (1 if content else 0),
        }
    except OSError as e:
        return {"status": "fail", "message": f"อ่านไฟล์ไม่สำเร็จ: {e}"}


def workspace_list(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    sub = ""
    if entities:
        sub = entities[0]
    elif inp:
        m = re.search(r"(?:ใน|in|folder|โฟลเดอร์)\s+([^\s]+)", inp, re.IGNORECASE)
        sub = m.group(1) if m else inp.strip()
        # ถ้า inp ลงท้ายด้วย " ." หรือ " . " ให้ใช้ "." เป็น target
        if sub and re.search(r"\s\.\s*$", sub):
            sub = "."

    target = sub or "."
    safe_path, err = resolve_workspace_path(target if target != "." else ".")
    if err and target != ".":
        return {"status": "fail", "message": err}
    base = PROJECT_ROOT if target in (".", "") else safe_path

    if not os.path.isdir(base):
        return {"status": "fail", "message": "ไม่ใช่โฟลเดอร์"}

    try:
        entries = []
        for name in sorted(os.listdir(base))[:50]:
            if name in BLOCKED_PARTS:
                continue
            full = os.path.join(base, name)
            kind = "📁" if os.path.isdir(full) else "📄"
            entries.append(f"{kind} {name}")
        rel = os.path.relpath(base, PROJECT_ROOT)
        if not entries:
            return {"status": "success", "result": f"โฟลเดอร์ {rel} ว่าง"}
        return {
            "status": "success",
            "result": f"รายการใน {rel}:\n" + "\n".join(entries),
        }
    except OSError as e:
        return {"status": "fail", "message": str(e)}


def workspace_apply_patch(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """
    รูปแบบ: ไฟล์ path.py แล้ว OLD|||NEW หรือบรรทัดแรกเป็น path
    """
    filename = pick_filename(entities, inp)
    if not filename:
        return {"status": "fail", "message": "ไม่ระบุไฟล์สำหรับ patch"}

    safe_path, err = resolve_workspace_path(filename)
    if err:
        return {"status": "fail", "message": err}

    if not os.path.isfile(safe_path):
        return {"status": "fail", "message": "ไม่พบไฟล์เป้าหมาย"}

    body = extract_code_content(inp, filename) or inp
    if "|||" not in body:
        return {"status": "fail", "message": "ใช้รูปแบบ: ข้อความเดิม|||ข้อความใหม่"}

    old, new = body.split("|||", 1)
    try:
        with open(safe_path, "r", encoding="utf-8") as f:
            text = f.read()
        if old not in text:
            return {"status": "fail", "message": "ไม่พบข้อความเดิมในไฟล์"}
        updated = text.replace(old, new, 1)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(updated)
        rel = os.path.relpath(safe_path, PROJECT_ROOT)
        return {"status": "success", "result": f"แก้ไข {rel} สำเร็จ (แทนที่ 1 จุด)"}
    except OSError as e:
        return {"status": "fail", "message": str(e)}


def workspace_run_script(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    """รันไฟล์ .py ใน workspace (จำกัด — ไม่รับ argument จาก shell)."""
    import subprocess
    import sys

    filename = pick_filename(entities, inp)
    if not filename or not filename.endswith(".py"):
        return {"status": "fail", "message": "ระบุไฟล์ .py ที่ต้องการรัน"}

    safe_path, err = resolve_workspace_path(filename)
    if err:
        return {"status": "fail", "message": err}

    if not os.path.isfile(safe_path):
        return {"status": "fail", "message": "ไม่พบไฟล์สคริปต์"}

    try:
        proc = subprocess.run(
            [sys.executable, safe_path],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = (proc.stdout or "").strip()
        err_out = (proc.stderr or "").strip()
        combined = out
        if err_out:
            combined = f"{out}\n[stderr]\n{err_out}".strip() if out else err_out
        status = "success" if proc.returncode == 0 else "fail"
        return {
            "status": status,
            "result": combined or f"(exit code {proc.returncode})",
            "exit_code": proc.returncode,
            "path": os.path.relpath(safe_path, PROJECT_ROOT),
        }
    except subprocess.TimeoutExpired:
        return {"status": "fail", "message": "รันเกิน 30 วินาที"}
    except OSError as e:
        return {"status": "fail", "message": str(e)}
