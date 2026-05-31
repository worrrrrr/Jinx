# run_realworld.py

import sys
import os
from typing import List

# ตรวจสอบตำแหน่ง Directory ปัจจุบันเพื่อให้แน่ใจว่า import ได้ถูกต้อง
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import Orchestrator

def run_realworld_test():
    """
    ตัวทดสอบการรันระบบจริงเพื่อแสดงผลลัพธ์ของ JINX หลังจากอัปเดตเครื่องมือ Math และ Search
    """
    # เริ่มระบบ Orchestrator หลัก
    jinx = Orchestrator()
    
    # ปรับรูปแบบการแสดงผลของ Response ให้เหมาะสมสำหรับการทดสอบ
    jinx.response.set_personality(name="Jinx", emoji_level="high")

    # ชุดทดสอบสถานการณ์จริง (Real-world Scenario Dataset)
    scenarios = [
        # 1. การสืบค้นฐานข้อมูลความรู้โลคัลด้วย Search Engine (Grep-based)
        {
            "category": "LOCAL SEARCH",
            "query": "ค้นหาข้อมูล ยินดีต้อนรับ"
        },
        # 2. ปัญหาสมการยกกำลังตัวแปรทับซ้อนที่เคยเกิดปัญหา TypeError ใน SymPy
        {
            "category": "EXPONENTIATION SOLVE",
            "query": "3^x=x^9  ได้เท่าไหร่"
        },
        # 3. ปัญหาระบบสมการเว้นวรรค (ไม่มีเครื่องหมายคั่น) ที่เคยเกิดปัญหา SyntaxError ใน Z3
        {
            "category": "IMPLICIT MULTI-EQUATIONS",
            "query": "หาค่าของ x+y=12 5y=12 "
        },
        # 4. ปัญหาระบบสมการคั่นจุลภาคตามปกติ ที่เคยเกิดปัญหา Decimal Literal ใน Z3
        {
            "category": "COMMA SEPARATED EQUATIONS",
            "query": "x+y=12, 5y=1  ได้เท่าไหร่"
        },
        # 5. โจทย์ภาษาไทยที่มีคำคณิตศาสตร์ (ต้องตัดสิทธิ์ไม่ให้รัน Engine ดิบ และประเมินผลอย่างปลอดภัย)
        {
            "category": "THAI WORD PROBLEM",
            "query": "ถ้า x มากกว่า y อยู่ 5 และ xy=24 "
        },
        {
            "category": "ENG WORD PROBLEM",
            "query": " if x more than y equal 5  and  x*y=24  find answer"
        },
        {
            "category": "ENG WORD PROBLEM",
            "query": " x-y=5, xy=24 "
        }
    ]

    print("=" * 70)
    print("🎯 JINX REAL-WORLD SYSTEM EXECUTION RESULT")
    print("=" * 70)

    for idx, case in enumerate(scenarios, 1):
        category = case["category"]
        query = case["query"]
        
        print(f"\n[{idx}] หมวดหมู่: {category}")
        print(f"👉 สิ่งที่ผู้ใช้ป้อนเข้ามา: \"{query}\"")
        
        # รันผ่านท่อประมวลผล Pipeline หลัก (Perception -> Reasoning -> Execution -> Response)
        answer = jinx.run(query)
        
        print(answer)
        print("-" * 70)

if __name__ == "__main__":
    run_realworld_test()