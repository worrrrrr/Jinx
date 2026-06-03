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

    # ชุดทดสอบสถานการณ์จริง (Real-world Scenario Dataset)
    scenarios = [
        {
            "query": "5 + 3 * (2 - 1) / 4"
        },
        {
            "query": "ดูดวง 8/8/1992 16.49 น ซินแซ"
        },
        {
            "query": "วิเคราะห์ชื่อ วรกฤช สุนทรธรรมนิติ"
        }
    ]   

    print("=" * 70)
    print("🎯 JINX REAL-WORLD SYSTEM EXECUTION RESULT")
    print("=" * 70)

    for idx, case in enumerate(scenarios, 1):
        query = case["query"]
        
        print(f"👉 สิ่งที่ผู้ใช้ป้อนเข้ามา: \"{query}\"")
        
        # รันผ่านท่อประมวลผล Pipeline หลัก (Perception -> Reasoning -> Execution -> Response)
        answer = jinx.run(query)
        
        print(answer)
        print("-" * 70)

if __name__ == "__main__":
    run_realworld_test()