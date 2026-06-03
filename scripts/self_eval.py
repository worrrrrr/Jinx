#!/usr/bin/env python3
"""
Self-Eval: ระบบทดสอบ Jinx แบบ end-to-end อัตโนมัติ
รัน: uv run python scripts/self_eval.py
"""

import sys
import time
import json
import os

# เพิ่ม project root ใน path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import Orchestrator


TEST_CASES = [
    # (ชื่อ, input, เช็ค string ในผลลัพธ์, domain ที่คาดหวัง)
    ("คณิตศาสตร์พื้นฐาน", "5 + 3", ["8"], "math"),
    ("คณิตศาสตร์สมการ", "x + 5 = 10", ["= 5", "5"], "math"),
    ("BaZi ดูดวง", "ดูดวง 8/8/1992 16.49", ["ลิง", "มังกร"], "general"),
    ("ค้นหาความรู้", "Python คืออะไร", ["Python"], "qa"),
    ("HTML Generator", "สร้าง html ชื่อเรื่อง ทดสอบ", ["<!DOCTYPE html>", "ทดสอบ"], "general"),
    ("Decision Tree เริ่มต้น", "tree food", ["อาหาร", "ประเภท"], "general"),
    ("State Machine แสดงสถานะ", "state coffee", ["idle"], "general"),
    ("Chat ทักทาย", "สวัสดี", ["สวัสดี", "ดี"], "conversation"),
    ("File list", "list_dir .", ["core", "tools"], "general"),
    ("วิเคราะห์ข้อมูล", "analyze data [{\"x\":1,\"y\":2}]", ["x", "y"], "general"),
    ("Web search fallback", "ค้นหา ดาวอังคาร", ["ดาวอังคาร"], "web"),
]

REQUIRED_TOOLS = [
    "compute_math", "web_search", "create_note", "bazi",
    "generate_html", "decision_tree", "state_machine",
    "analyze_data", "vault_read", "vault_search",
]


def test_tools_registered(orc: Orchestrator) -> dict:
    missing = []
    for tool in REQUIRED_TOOLS:
        if tool not in orc.execution.tools:
            missing.append(tool)
    return {"pass": len(missing) == 0, "detail": f"เครื่องมือขาด: {missing}" if missing else "ครบทุก tool"}


def run_eval() -> dict:
    import logging
    logging.disable(logging.CRITICAL)

    orc = Orchestrator()
    results = []

    # 1. ตรวจสอบเครื่องมือ
    tr = test_tools_registered(orc)
    results.append({"name": "Tools Registration", **tr})

    # 2. รัน test cases
    for name, inp, expected_checks, expected_domain in TEST_CASES:
        start = time.time()
        try:
            out = orc.run(inp)
            elapsed = round((time.time() - start) * 1000, 1)
            passed = all(check in out for check in expected_checks)
            results.append({
                "name": name,
                "pass": passed,
                "time_ms": elapsed,
                "detail": f"{'ผ่าน' if passed else 'ไม่ผ่าน'} ({elapsed}ms) — ต้องการ: {expected_checks[:2]}",
            })
        except Exception as e:
            results.append({
                "name": name,
                "pass": False,
                "time_ms": -1,
                "detail": f"Exception: {type(e).__name__} - {str(e)}",
            })

    # สรุป
    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    failed = total - passed
    times = [r.get("time_ms", 0) for r in results if r.get("time_ms", -1) >= 0]
    avg_time = round(sum(times) / len(times), 1) if times else 0.0

    summary = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": round(passed / total * 100, 1) if total > 0 else 0,
        "avg_time_ms": avg_time,
        "results": results,
    }
    return summary


def main():
    print("=" * 50)
    print("🧪 Jinx Self-Evaluation")
    print("=" * 50)

    summary = run_eval()

    for r in summary["results"]:
        icon = "✅" if r["pass"] else "❌"
        detail = r.get("detail", "")
        print(f"  {icon} {r['name']}: {detail}")

    print("-" * 50)
    print(f"ผลลัพธ์: {summary['passed']}/{summary['total']} ผ่าน "
          f"({summary['success_rate']}%) | "
          f"เวลาเฉลี่ย: {summary['avg_time_ms']}ms")
    print()

    if summary["failed"] > 0:
        print("❌ รายการที่ไม่ผ่าน:")
        for r in summary["results"]:
            if not r["pass"]:
                print(f"  - {r['name']}: {r.get('detail', '')}")

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
