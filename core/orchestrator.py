# core/orchestrator.py

import logging
import time
from typing import Dict, Any, Optional
import os
from core.memory import (
    SessionMemory,
    extract_variables_from_result,
    substitute_variables_in_text,
)

_SESSION_PERSIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "session_memory.json"
)
from core.llm_core import JinxLLMCore
from engines.perception import PerceptionEngine
from engines.reasoning import ReasoningEngine
from engines.execution import ExecutionEngine
from engines.response import ResponseEngine

# ตั้งค่า Logger สำหรับติดตามการทำงานของระบบ
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrator: ตัวประสานงานหลักของ Jinx Agent ทำหน้าที่ควบคุม Pipeline 4 ด่าน 
    (Perception -> Reasoning -> Execution -> Response)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        
        # โหลด LLM (Ollama local) เป็น optional component
        self.llm_core = JinxLLMCore()
        if self.llm_core.available:
            logger.info(f"✅ LLM ready: {', '.join(self.llm_core.provider_names)}")

        # เริ่มต้นการทำงานของทั้ง 4 Engines หลัก
        self.perception = PerceptionEngine()
        self.reasoning = ReasoningEngine()
        self.execution = ExecutionEngine(llm_core=self.llm_core)
        self.response = ResponseEngine()
        
        # ตรวจสอบและสวมทับสไตล์ส่วนตัวของ Jinx จาก Config (override preferences)
        personality_config = self.config.get("personality", {})
        if personality_config:
            self.response.set_personality(**personality_config)
            
        # สร้างรหัสจำเพาะการเชื่อมต่อของเซสชัน (Session Tracking)
        self.session_id = f"jinx_{int(time.time())}"

        # แก้เป็นแบบนี้ — ไม่ระบุชื่อพารามิเตอร์ตัวแรก:
        self.memory = SessionMemory(
            self.config.get("memory_max_history", 10),
            persist_path=_SESSION_PERSIST
        )
        
        # ระบบจัดเก็บสถิติเชิงปริมาณ (Telemetry metrics)
        self._stats = {
            "requests": 0,
            "errors": 0,
            "latency_ms": []
        }
        
        logger.info(f"🧠 Jinx Orchestrator ready and synchronized (session_id: {self.session_id})")

    def run(self, user_input: str) -> str:
        """
        ท่อประมวลผลหลัก (Main Pipeline Entry): รับข้อความดิบ → แปลงข้อมูล 4 ด่าน → คืนผลลัพธ์การตอบสนอง
        """
        start_time = time.time()
        self._stats["requests"] += 1
        
        try:
            # 1. PERCEPTION LAYER: ทำความเข้าใจเจตนา และคัดกรองสมการให้สะอาดบริสุทธิ์
            perception_output = self.perception.perceive(user_input)
            logger.debug(f"🔍 Perception complete: intent='{perception_output['intent']}', domain='{perception_output['domain']}'")
            
            # 2. REASONING LAYER: วางแผนการทำงานตามเงื่อนไขบริบท พร้อมส่งสัญญาณจัดแต่งประโยค
            plan_output = self.reasoning.plan(perception_output)
            logger.debug(f"🧭 Plan generated: tasks={plan_output['tasks']}, status='{plan_output['status']}'")

            # แทนค่าตัวแปรเฉพาะนิพจน์ที่ไม่มี '=' (ไม่แทนในสมการที่กำลังหาตัวแปร)
            if plan_output.get("domain") == "math" and self.memory.variables:
                topic = plan_output.get("topic", "")
                if topic and "=" not in topic:
                    plan_output["topic"] = substitute_variables_in_text(
                        topic, self.memory.variables
                    )
            
            # 3. EXECUTION LAYER: ประมวลผลเครื่องมือจริง (Math/Search/File)
            execution_output = self.execution.execute(plan_output)
            logger.debug(f"⚙️ Execution finished: status='{execution_output['status']}'")

            # 💡 เพิ่มเติมลอจิกช่วยดีบักคีย์คำสั่งตกค้าง
            if execution_output.get("status") == "noop":
                logger.warning(
                    f"⚠️ System Warning: No active tool handler was executed for plan! "
                    f"Intent: {plan_output.get('intent')}, Action: {plan_output.get('action')}. "
                    f"Falling back to default response."
                )

            self.memory.update_context("last_intent", perception_output.get("intent"))
            self.memory.update_context("last_domain", perception_output.get("domain"))
            
            # 4. RESPONSE LAYER: ปรุงแต่งและเรียบเรียงประโยคตอบสนองผู้ใช้ตามบุคลิกภาพ
            response_answer = self.response.format(execution_output, perception=perception_output)

            self.memory.add_turn(user_input, response_answer)
            
            # คำนวณและบันทึกเวลาการทำงานเพื่อประเมินประสิทธิภาพความหน่วง (Latency Telemetry)
            latency = (time.time() - start_time) * 1000
            self._stats["latency_ms"].append(latency)
            
            logger.info(f"✅ Success in {latency:.1f}ms: Input='{user_input[:30]}...' -> Reply='{response_answer[:30]}...'")
            return response_answer
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"❌ Pipeline runtime error: {type(e).__name__} - {str(e)}", exc_info=True)
            
            # Emergency Fallback Boundary: คืนคำตอบสุภาพประคองระบบกรณีเกิดข้อผิดพลาดรุนแรงภายใน
            return "ขออภัยครับ เกิดข้อผิดพลาดในขั้นตอนประมวลผลภายในระบบ กรุณาปรับเปลี่ยนรูปแบบคำสั่งแล้วลองใหมู่อีกครั้งนะครับ 🙏"

    def chat(self, text: str) -> str:
        """
        Convenience alias สำหรับการเรียกใช้อย่างยืดหยุ่นในระบบ Chat interface
        """
        return self.run(text)

    def get_stats(self) -> Dict[str, Any]:
        """
        สกัดค่าสถิติการรันโปรแกรมเพื่อตรวจสอบสถานะเชิงระบบ
        """
        latencies = self._stats["latency_ms"]
        total_reqs = self._stats["requests"]
        errors = self._stats["errors"]
        
        success_rate = round(((total_reqs - errors) / max(1, total_reqs)) * 100, 2)
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
        
        return {
            "session_id": self.session_id,
            "total_requests": total_reqs,
            "error_count": errors,
            "success_rate_percent": success_rate,
            "avg_latency_ms": avg_latency,
            "system_integrity": {
                "perception_healthy": self.perception is not None,
                "reasoning_healthy": self.reasoning is not None,
                "execution_healthy": self.execution is not None,
                "response_healthy": self.response is not None
            },
            "memory": {
                "turns": len(self.memory.history),
                "variables": dict(self.memory.variables),
            },
        }

    def reset_memory(self):
        """ล้างความจำเซสชัน (ประวัติสนทนาและตัวแปร)"""
        self.memory.clear()
        logger.info("🔄 Session memory cleared")

    def reset_stats(self):
        """
        รีเซ็ตตารางสถิติตัวแปรเชิงระบบย่อยใหม่ทั้งหมด
        """
        self._stats = {
            "requests": 0,
            "errors": 0,
            "latency_ms": []
        }
        logger.info("🔄 Orchestrator performance statistics reset")