# main.py — Jinx Personal AI Runtime

import sys
from core.orchestrator import Orchestrator


def main():
    orc = Orchestrator()

    if orc.llm_core.available:
        provider_names = ", ".join(orc.llm_core.provider_names)
        print(f"🤖 LLM พร้อม: {provider_names}")
    else:
        print("🤖 โหมด offline — ไม่มี LLM")

    print(f"🧠 Jinx พร้อมทำงาน | session: {orc.session_id}")
    print("พิมพ์ exit หรือ quit เพื่อออก\n")

    while True:
        try:
            user_input = input("คุณ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("👋 บ๊ายบาย!")
            break

        response = orc.run(user_input)
        print(f"Jinx: {response}")
        print()


if __name__ == "__main__":
    main()
