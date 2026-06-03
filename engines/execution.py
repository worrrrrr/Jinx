# engines/execution.py

import math
import re
import os
from typing import Dict, Any, Optional, Callable, List

# ลงทะเบียนเชื่อมต่อเครื่องมือเสริมทางกายภาพจากภายนอก (tools/)
try:
    from tools import math as t_math
    from tools import search as t_search
    from tools import utils as t_utils
    from tools import obsidian as t_obsidian
    from tools import file as t_file
    from tools import html_gen as t_html
    from tools import data_analysis as t_data
    from tools import decision_tree as t_tree
    from tools import state_manager as t_state
    from tools import bazi as t_bazi
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False

WORKSPACE_TOOL_KEYS = frozenset({
    "write_code", "create_code", "update_code", "read_code", "read_workspace",
    "list_workspace", "list_dir", "apply_patch", "run_script", "debug_code",
})


class ExecutionEngine:
    """
    Execution Layer (ฉบับอัปเกรด): รันเครื่องมือตามแผนงาน พร้อมส่งต่อสัญญาณนำทางความตรรกศาสตร์
    """
    
    def __init__(self, llm_core=None):
        self.tools: Dict[str, Callable] = {}
        self.llm_core = llm_core
        
        if TOOLS_AVAILABLE:
            self._register_external_tools()
        else:
            self._register_fallback_tools()
        
        # รายชื่อคำสั่งอันตรายป้องกัน Shell / Python Code Injection
        self.forbidden_patterns = [
            "os.system", "subprocess", "eval(", "exec(", "__import__", 
            "shutil.", "open(", "write(", "remove("
        ]

    def _register_external_tools(self):
        """
        ลงทะเบียนระบบเรียกใช้เครื่องมือจริงจากโฟลเดอร์ tools/
        """
        try:
            self.tools.update(t_math.get_tools())
            self.tools.update(t_search.get_tools())
            self.tools.update(t_obsidian.get_tools())
            self.tools.update(t_file.get_tools())
            self.tools.update(t_html.get_tools())
            self.tools.update(t_data.get_tools())
            self.tools.update(t_tree.get_tools())
            self.tools.update(t_state.get_tools())
            self.tools.update(t_bazi.get_tools())
            if hasattr(t_utils, "get_tools"):
                self.tools.update(t_utils.get_tools())
            # QA intents ใช้คลังความรู้โลคัล (ไม่ทับด้วย fallback mock)
            self.tools.setdefault("answer_question", t_search.search_local_knowledge)
            self.tools.setdefault("search_knowledge", t_search.search_local_knowledge)
            # Chat handlers — fallback ในกรณี action map ส่งมา
            self.tools.setdefault("handle_conversation", self._chat_handler)
        except Exception as e:
            # ตกเข้าสู่ระบบ Fallback กรณีตัวเครื่องมือภายนอกสะกดไวยากรณ์ผิดพลาด
            self._register_fallback_tools()

    def _register_fallback_tools(self):
        """
        ลงทะเบียนคลังเครื่องมือสำรองกรณีฉุกเฉิน
        """
        self.tools.update({
            "compute_math": self._math_handler,
            "math": self._math_handler,
            "web_search": self._search_handler,
            "search": self._search_handler,
            "check_file": self._file_handler,
            "file": self._file_handler,
            "handle_conversation": self._chat_handler,
            "answer_question": self._qa_handler,
        })

    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        ทางเข้าหลัก: ดึงค่าจากแผนงานรันคำสั่ง → ประมวลผลเครื่องมือเป้าหมาย → แนบข้อมูล Metadata ไปยัง Response
        """
        domain = plan.get("domain", "general")
        action = plan.get("action", "analyze")
        inp = plan.get("topic", "") or plan.get("raw", "")
        entities = plan.get("entities", [])
        tasks = plan.get("tasks", [])
        
        # ดึงสัญญานเมทาดาตาเพื่อส่งต่อ
        metadata = plan.get("metadata", {})
        response_hint = plan.get("response_hint", {})
        
        # ค้นหาเครื่องมือเป้าหมายลำดับแรกตาม Action -> Domain -> Task
        handler_key = action or domain or (tasks[0] if tasks else "noop")
        handler = self.tools.get(handler_key)
        
        # ค้นหาแบบสำรองกรณีไม่พบคีย์หลักตรงๆ
        if not handler:
            for key in [action, domain] + tasks:
                if key in self.tools:
                    handler = self.tools[key]
                    break
        
        # เตรียมแพ็กเกจข้อมูลสำหรับ Response Engine
        response_metadata = {**metadata, "response_hint": response_hint}
        
        if handler:
            try:
                # ข้าม injection check สำหรับ file tool (รับโค้ดจริง)
                skip_injection = handler_key in WORKSPACE_TOOL_KEYS
                if not skip_injection and (
                    self._is_dangerous(str(inp)) or any(self._is_dangerous(str(e)) for e in entities)
                ):
                    return {
                        "status": "fail", 
                        "message": "ตรวจพบรูปแบบคำสั่งที่อาจไม่ปลอดภัยต่อระบบปฏิบัติการ",
                        "metadata": response_metadata
                    }
                
                # รันเครื่องมือจริง
                output = handler(action, inp, entities)
                
                # ทำการห่อพัสดุแนบเมทาดาตาและสัญญานชี้นำคำตอบ (Response Hint) คืนกลับระบบ
                if isinstance(output, dict):
                    if "metadata" not in output:
                        output["metadata"] = {}
                    output["metadata"].update(response_metadata)
                    return output
                else:
                    return {
                        "status": "success",
                        "result": output,
                        "metadata": response_metadata
                    }
                
            except Exception as e:
                return {
                    "status": "error", 
                    "message": f"Execution Error: {type(e).__name__} - {str(e)}", 
                    "result": None,
                    "metadata": response_metadata
                }
        
        # กรณีไม่มีเครื่องมือใดรองรับ
        return {
            "status": "noop", 
            "result": inp, 
            "message": f"No active tool registered for key: '{handler_key}'",
            "metadata": response_metadata
        }

    def _is_dangerous(self, text: str) -> bool:
        """
        ตรวจหาคำสั่งและสัญลักษณ์อันตรายในสายอักขระ
        """
        return any(pat in text for pat in self.forbidden_patterns)

    # ==========================================
    # FALLBACK ENGINE HANDLERS (ระบบสำรองป้องกันพัง)
    # ==========================================

    def _math_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        clean = inp.replace("^", "**").replace("=", "==")
        allowed = set("0123456789+-*/().%^ ")
        
        for func in ["sqrt", "sin", "cos", "tan", "log", "exp", "abs"]:
            clean = clean.replace(f"{func}(", f"__{func}(")
        
        if not all(c in allowed or c in "_()" or c.isalpha() for c in clean):
            return {"status": "fail", "message": "นิพจน์คณิตศาสตร์มีสัญลักษณ์ที่ไม่ปลอดภัย"}
        
        try:
            safe_ns = {
                "__builtins__": None,
                "abs": abs,
                **{k: getattr(math, k) for k in ["sqrt", "sin", "cos", "tan", "log", "log10", "exp"]},
            }
            for func in ["sqrt", "sin", "cos", "tan", "log", "exp", "abs"]:
                clean = clean.replace(f"__{func}(", f"{func}(")
            
            result = eval(clean, safe_ns)
            if isinstance(result, float):
                result = round(result, 6) if abs(result) < 1e10 else result
            return {"status": "success", "result": result}
            
        except ZeroDivisionError:
            return {"status": "fail", "message": "ไม่สามารถหารด้วยศูนย์ได้"}
        except Exception as e:
            return {"status": "fail", "message": f"คำนวณผิดพลาด: {type(e).__name__}"}

    def _search_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        query = inp or " ".join(entities) if entities else "unknown"
        return {
            "status": "success",
            "result": [{"title": f"ข้อมูลจำลองสำหรับ: {query}", "snippet": "ผลลัพธ์จากคลังข้อมูลสำรอง"}],
            "query": query
        }

    def _file_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        path = entities[0] if entities else inp
        if not path:
            return {"status": "fail", "message": "ไม่ระบุชื่อไฟล์เป้าหมาย"}
        if ".." in path or path.startswith("/"):
            return {"status": "fail", "message": "เส้นทางพาธระบุไฟล์มีความเสี่ยงต่อระบบ"}
        return {
            "status": "success",
            "result": {"exists": os.path.exists(path), "path": path}
        }

    def _chat_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        # ถ้ามี LLM พร้อมใช้ — ให้ LLM ตอบกลับสำหรับ chat intent
        if self.llm_core and self.llm_core.available:
            for provider in self.llm_core.providers.values():
                if provider.ready:
                    try:
                        response = provider.chat(
                            prompt=inp,
                            temperature=0.7,
                            max_tokens=500
                        )
                        if response:
                            return {"status": "success", "result": response, "direct_response": True}
                    except Exception:
                        continue
        # fallback: ส่งข้อความเดิมกลับไปให้ response engine จัดการ template
        return {"status": "success", "result": inp}

    def _qa_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        if TOOLS_AVAILABLE:
            try:
                return t_search.search_local_knowledge(action, inp, entities)
            except Exception:
                pass
        return {"status": "success", "result": f"คลังสำรองไม่พบข้อมูลจำเพาะสำหรับ '{inp}'"}