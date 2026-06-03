# main.py — Jinx Personal AI Runtime

import sys
import os
import argparse
import shutil
from pathlib import Path
from core.orchestrator import Orchestrator

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.completion import Completer, Completion

    _HAS_PT = True
except ImportError:
    _HAS_PT = False

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "data", ".cli_history")

SLASH_COMMANDS = {
    ".help": "แสดงคำสั่งที่ใช้ได้",
    ".ls [path]": "รายชื่อไฟล์/โฟลเดอร์",
    ".tree [path]": "โครงสร้างโฟลเดอร์แบบต้นไม้",
    ".clean": "ล้างไฟล์ขยะ (ยกเว้น .venv/.git/node_modules/__pycache__)",
    ".exit": "ออกจากโปรแกรม",
}


class DotCommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("."):
            for cmd, desc in SLASH_COMMANDS.items():
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text), display=cmd, display_meta=desc)


def _detect_vt100():
    """Force VT100 output for Git Bash / mintty"""
    if os.environ.get("TERM") == "xterm" and _HAS_PT:
        try:
            import fcntl, termios, struct, sys
            fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0))
            return True
        except Exception:
            pass
    return False


def main():
    parser = argparse.ArgumentParser(description="Jinx Personal AI Runtime")
    parser.add_argument("--cmd", "-c", type=str, help="รันคำสั่งเดียวแล้วออก")
    parser.add_argument("--ls", type=str, nargs="?", const=".", help="แสดงรายการไฟล์")
    parser.add_argument("--tree", type=str, nargs="?", const=".", help="แสดงโครงสร้างต้นไม้")
    parser.add_argument("--clean", action="store_true", help="ล้างไฟล์ขยะ")
    args = parser.parse_args()

    orc = Orchestrator()

    # ── CLI flags ──
    if args.cmd:
        print(orc.run(args.cmd))
        return

    if args.ls:
        _do_ls(args.ls)
        return

    if args.tree:
        _do_tree(args.tree)
        return

    if args.clean:
        _do_clean()
        return

    # ── REPL mode ──
    if orc.llm_core.available:
        providers = ", ".join(orc.llm_core.provider_names)
        print(f"🤖 LLM พร้อม: {providers}")
    else:
        print("🤖 โหมด offline — ไม่มี LLM")

    print(f"🧠 Jinx พร้อมทำงาน | session: {orc.session_id}")
    print("พิมพ์ .help เพื่อดูคำสั่ง หรือ exit/quit เพื่อออก\n")

    if _HAS_PT:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        if _detect_vt100():
            from prompt_toolkit.output import create_output
            session = PromptSession(
                history=FileHistory(HISTORY_FILE),
                completer=DotCommandCompleter(),
                complete_while_typing=True,
            )
        else:
            session = PromptSession(
                history=FileHistory(HISTORY_FILE),
                completer=DotCommandCompleter(),
                complete_while_typing=True,
            )
        _repl_pt(session, orc)
    else:
        _repl_basic(orc)


def _repl_pt(session, orc):
    while True:
        try:
            user_input = session.prompt("คุณ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            continue
        except Exception:
            break

        if not user_input:
            continue
        if _handle_slash(user_input, orc):
            continue
        if user_input.lower() in ("exit", "quit"):
            print("👋 บ๊ายบาย!")
            break

        response = orc.run(user_input)
        print(f"Jinx: {response}\n")


def _repl_basic(orc):
    while True:
        try:
            user_input = input("คุณ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if _handle_slash(user_input, orc):
            continue
        if user_input.lower() in ("exit", "quit"):
            print("👋 บ๊ายบาย!")
            break

        response = orc.run(user_input)
        print(f"Jinx: {response}\n")


def _handle_slash(user_input, orc):
    cmd = user_input.strip()
    if cmd == ".help":
        print("--- คำสั่งที่มี ---")
        for c, d in SLASH_COMMANDS.items():
            print(f"  {c:20s} {d}")
        print()
        return True
    if cmd == ".exit":
        print("👋 บ๊ายบาย!")
        sys.exit(0)
    if cmd.startswith(".ls"):
        parts = cmd.split(maxsplit=1)
        path = parts[1] if len(parts) > 1 else "."
        _do_ls(path)
        return True
    if cmd.startswith(".tree"):
        parts = cmd.split(maxsplit=1)
        path = parts[1] if len(parts) > 1 else "."
        _do_tree(path)
        return True
    if cmd == ".clean":
        _do_clean()
        return True
    return False


def _do_ls(path="."):
    root = Path(".")
    prefix = path
    if Path(path).exists():
        root = Path(path)
        prefix = ""
    items = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    shown = 0
    for p in items:
        if prefix and not p.name.lower().startswith(prefix.lower()):
            continue
        suffix = "/" if p.is_dir() else ""
        print(f"  {p.name}{suffix}")
        shown += 1
    if shown == 0 and prefix:
        print(f"  (ไม่มีไฟล์ขึ้นต้นด้วย '{prefix}')")
    print()


def _do_tree(path=".", prefix="", root_path=None):
    if root_path is None:
        root_path = Path(path)
        if not root_path.exists():
            print(f"❌ ไม่พบ: {path}")
            return
        print(f"  {root_path.name}/")
    try:
        entries = sorted(Path(path).iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return
    for i, p in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{p.name}")
        if p.is_dir():
            ext = "    " if is_last else "│   "
            _do_tree(str(p), prefix + ext, root_path)


SKIP_CLEAN = {".venv", ".git", "node_modules", "__pycache__", ".pytest_cache"}

def _do_clean():
    removed = 0
    for f in Path(".").iterdir():
        if f.name in SKIP_CLEAN or not f.is_dir():
            continue
        if f.name.endswith(".egg-info"):
            shutil.rmtree(f)
            print(f"  🗑️ {f.name}")
            removed += 1
            continue
        for pyc in f.rglob("*.pyc"):
            pyc.unlink(missing_ok=True)
            removed += 1
        for cache in f.rglob("__pycache__"):
            if cache.is_dir():
                shutil.rmtree(cache, ignore_errors=True)
                removed += 1
    if removed:
        print(f"  ✅ ล้าง {removed} รายการ")
    else:
        print("  ไม่มีอะไรต้องล้าง")
    print()


if __name__ == "__main__":
    main()
