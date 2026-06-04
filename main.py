#!/usr/bin/env python3
import sys
import os
import logging
from datetime import datetime

# UI & Terminal Enhancement
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from rich.theme import Theme

# Prompt & Autocomplete
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style as ToolkitStyle

# Core Logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from core.orchestrator import Orchestrator
except ImportError:
    # สำหรับกรณีที่ยังไม่ได้สร้าง Folder core
    class Orchestrator:
        def run(self, text): return f"Echo: {text}"
        def get_stats(self): return {"total_requests": 0, "success_rate_percent": 100, "avg_latency_ms": 0}
        def reset_memory(self): pass

# --- Configuration ---
LOG_FILE = "jinx_agent.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "jinx": "bold magenta"
})

console = Console(theme=custom_theme)

SLASH_COMMANDS = {
    "/help": "แสดงคัมภีร์คำสั่งทั้งหมด",
    "/stats": "ตรวจสอบ Performance ของระบบ",
    "/reset": "ล้างสถานะหน่วยความจำ (Brain Wash)",
    "/clear": "ล้างหน้าจอ Terminal",
    "/exit": "จบการทำงาน",
    "/astro": "วิเคราะห์ดวงชะตา (Bazi/Thai)",
    "/mbti": "วิเคราะห์บุคลิกภาพเชิงลึก",
    "/math": "แก้โจทย์คำนวณซับซ้อน",
}

AUTOCOMPLETE_WORDS = list(SLASH_COMMANDS.keys()) + [
    "วิเคราะห์", "คำนวณ", "INFJ", "INTJ", "ดวงรายวัน", "ขอบคุณ"
]

pt_style = ToolkitStyle.from_dict({
    "prompt": "bold #00ff00",
})

# --- UI Functions ---
def display_welcome():
    os.system("cls" if os.name == "nt" else "clear")
    welcome_text = """
      ██╗██╗███╗   ██╗██╗  ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗
      ██║██║████╗  ██║╚██╗██╔╝    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
      ██║██║██╔██╗ ██║ ╚███╔╝     ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
 ██   ██║██║██║╚██╗██║ ██╔██╗     ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
 ╚█████╔╝██║██║ ╚████║██╔╝ ██╗    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
  ╚════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
    """
    console.print(Panel(welcome_text, title="v2.0 Extreme", border_style="magenta"))
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Command", style="dim", width=12)
    table.add_column("Description")
    for cmd, desc in SLASH_COMMANDS.items():
        table.add_row(cmd, desc)
    console.print(table)

def handle_command(cmd, arg, jinx):
    if cmd == "/help":
        display_welcome()
    elif cmd == "/stats":
        s = jinx.get_stats()
        stats_table = Table(title="System Performance")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        stats_table.add_row("Requests", str(s.get('total_requests', 0)))
        stats_table.add_row("Success Rate", f"{s.get('success_rate_percent', 0)}%")
        stats_table.add_row("Avg Latency", f"{s.get('avg_latency_ms', 0)}ms")
        console.print(stats_table)
    elif cmd == "/reset":
        jinx.reset_memory()
        console.print("[success]🔄 Memory has been wiped clean.[/success]")
    elif cmd == "/clear":
        os.system("cls" if os.name == "nt" else "clear")
    elif cmd in ["/astro", "/mbti", "/math"]:
        prompt_map = {"/astro": "🔮 วันเดือนปีเกิด: ", "/mbti": "🧠 ข้อความวิเคราะห์: ", "/math": "🔢 สมการ: "}
        final_input = arg if arg else console.input(f"[bold yellow]{prompt_map[cmd]}[/bold yellow]")
        return f"{SLASH_COMMANDS[cmd].split()[0]} {final_input}"
    return None

# --- Main Logic ---
def main():
    display_welcome()
    
    try:
        jinx = Orchestrator()
    except Exception as e:
        console.print(f"[error]CRITICAL ERROR:[/error] Cannot start Orchestrator: {e}")
        logging.error(f"Initialization failed: {e}")
        return

    session = PromptSession(
        history=FileHistory(os.path.expanduser("~/.jinx_history")),
        auto_suggest=AutoSuggestFromHistory(),
        completer=WordCompleter(AUTOCOMPLETE_WORDS, ignore_case=True),
        style=pt_style,
    )

    while True:
        try:
            timestamp = datetime.now().strftime("%H:%M")
            user_input = session.prompt(f"[{timestamp}] Jinx ❯ ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["/exit", "exit", "quit"]:
                console.print("[jinx]Sayonara! บ๊ายบายครับ... 🙏[/jinx]")
                break

            # 1. Command Routing
            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else None
                
                # Check if command exists
                if cmd not in SLASH_COMMANDS:
                    console.print(f"[error]❌ ไม่รู้จักคำสั่ง {cmd}[/error]")
                    continue
                
                # Process internal commands
                processed_input = handle_command(cmd, arg, jinx)
                if processed_input:
                    user_input = processed_input
                else:
                    continue # Finished internal cmd

            # 2. AI Processing with Spinner
            logging.info(f"User Request: {user_input}")
            with Live(Spinner("dots", text="[jinx] Jinx is thinking...[/jinx]", style="magenta"), refresh_per_second=10) as live:
                response = jinx.run(user_input)
                live.update(f"[success]✅ Success[/success]")

            # 3. Output Response
            console.print(Panel(response, title="[bold magenta]Jinx AI[/bold magenta]", border_style="cyan"))

        except KeyboardInterrupt:
            console.print("\n[warning]⚠️ กด /exit เพื่อออกจากโปรแกรมอย่างปลอดภัย[/warning]")
            continue
        except EOFError:
            break
        except Exception as e:
            console.print(f"[error]‼️ เกิดข้อผิดพลาดไม่คาดคิด: {e}[/error]")
            logging.error(f"Runtime error: {e}", exc_info=True)

if __name__ == "__main__":
    main()