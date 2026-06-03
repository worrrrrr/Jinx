"""
Module: engines/execution.py
Description: Execution Layer (Enterprise Full Max Edition)
             ระบบประสานงาน คัดกรองความปลอดภัย และเรียกใช้เครื่องมือวิเคราะห์จริง (Real Tools)
             เพิ่มระบบจัดทำรายงานมหาพยากรณ์รวม 4 มิติสากล (จีน ไทย อินเดีย ฝรั่ง)
"""

import ast
import logging
import math
import operator
import os
import re
from typing import Dict, Any, Optional, Callable, List

# ตั้งค่าระบบ Logger สากลของ Jinx
logger = logging.getLogger("core.execution")

# รายชื่อเครื่องมือหลักที่ต้องทำการตรวจสอบและโหลดเข้าคลังระบบ
REQUIRED_TOOLS_CONFIG = [
    ("math", "t_math"),
    ("search", "t_search"),
    ("utils", "t_utils"),
    ("obsidian", "t_obsidian"),
    ("file", "t_file"),
    ("html_gen", "t_html"),
    ("data_analysis", "t_data"),
    ("decision_tree", "t_tree"),
    ("state_manager", "t_state"),
    ("bazi", "t_bazi"),
    ("name_analysis", "t_name_analysis"),  # 🔗 โมดูลวิเคราะห์ชื่อศาสตร์โบราณ 5 มิติ
]

# รายชื่อเครื่องมือเสริมที่มีความเกี่ยวข้องกับปฏิทินดาราศาสตร์ระดับสูง
OPTIONAL_TOOLS_CONFIG = [
    ("thai_astro", "t_thai_astro"),        # 🔗 โมดูลดวงชะตากำเนิดไทยสิบดาว (ต้องการ pyswisseph)
    ("jyotish", "t_jyotish"),              # 🔗 โมดูลโหราศาสตร์อินเดีย ( Vetic )
    ("western_astro", "t_western_astro"),  # 🔗 โมดูลโหราศาสตร์สากล ( Western )
]

# คลังโมดูลที่โหลดสำเร็จจริงของระบบ
LOADED_TOOLS: Dict[str, Any] = {}
_REQUIRED_TOOL_ERRORS: List[str] = []

# ทำการโหลดแยกตัวแปรทีละหน่วยอย่างทรหด (Individual Sandbox Loading Pattern)
for module_name, var_name in REQUIRED_TOOLS_CONFIG:
    try:
        imported_mod = __import__(f"tools.{module_name}", fromlist=[module_name])
        LOADED_TOOLS[var_name] = imported_mod
    except ImportError as e:
        _REQUIRED_TOOL_ERRORS.append(f"Required tools.{module_name} error: {e}")
        logger.error(f"Failed to import required tool '{module_name}': {e}")

for module_name, var_name in OPTIONAL_TOOLS_CONFIG:
    try:
        imported_mod = __import__(f"tools.{module_name}", fromlist=[module_name])
        LOADED_TOOLS[var_name] = imported_mod
    except ImportError as e:
        LOADED_TOOLS[var_name] = None
        logger.warning(f"Optional tool '{module_name}' is not loaded: {e}")

# ประเมินเกณฑ์ความสมบูรณ์ของแกนรันหลัก
TOOLS_AVAILABLE = len(_REQUIRED_TOOL_ERRORS) == 0

WORKSPACE_TOOL_KEYS = frozenset({
    "write_code", "create_code", "update_code", "read_code", "read_workspace",
    "list_workspace", "list_dir", "apply_patch", "run_script", "debug_code",
})


class ExecutionEngine:
    """
    Execution Layer: ทำหน้าที่รับแผน ตรวจสอบความปลอดภัยสูงสุด และส่งมอบการประมวลผลให้เครื่องมือจริง
    """
    
    def __init__(self, llm_core: Optional[Any] = None) -> None:
        self.tools: Dict[str, Callable] = {}
        self.llm_core = llm_core
        
        # ตารางจับคู่ค่าพลังเลขศาสตร์ภาษาไทยมาตรฐาน
        self.thai_numerology_map: Dict[str, int] = {
            'ก': 1, 'ด': 1, 'ถ': 1, 'ท': 1, 'ภ': 1, 'ฤ': 1, 'า': 1, 'อุ': 1, 'ำ': 1, '่': 1, 'ุ': 1,
            'ข': 2, 'ช': 2, 'ง': 2, 'บ': 2, 'ป': 2, 'เ': 2, 'แ': 2, 'ู': 2, '้': 2,
            'ฆ': 3, 'ต': 3, 'ฑ': 3, 'ฒ': 3, 'ฃ': 3, '๋': 3,
            'ค': 4, 'ธ': 4, 'ญ': 4, 'ร': 4, 'ษ': 4, 'ฅ': 4, 'ะ': 4, 'ิ': 4, 'โ': 4, 'ั': 4,
            'ฉ': 5, 'ณ': 5, 'ฌ': 5, 'น': 5, 'ม': 5, 'ห': 5, 'ฎ': 5, 'ฬ': 5, 'ฮ': 5, 'ึ': 5,
            'จ': 6, 'ล': 6, 'ว': 6, 'อ': 6, 'ใ': 6,
            'ซ': 7, 'ศ': 7, 'ส': 7, 'ี': 7, 'ื': 7, '๊': 7,
            'ย': 8, 'พ': 8, 'ฟ': 8, 'ผ': 8, 'ฝ': 8, '็': 8,
            'ฏ': 9, 'ฐ': 9, 'ไ': 9, '์': 9
        }

        if TOOLS_AVAILABLE:
            self._register_external_tools()
        else:
            self._register_fallback_tools()
            
        self._ensure_critical_fallbacks()

        # รูปแบบข้อความระมัดระวังป้องกัน Shell / Code Injection
        self.forbidden_patterns = [
            "os.system", "subprocess", "eval", "exec", "__import__", 
            "shutil.", "open(", "write(", "remove("
        ]

    def _register_external_tools(self) -> None:
        """
        ลงทะเบียนเชื่อมต่อเครื่องมือจริงจากคลาสโมดูลต่าง ๆ ในแฟ้ม tools/
        """
        try:
            self.tools.update(LOADED_TOOLS["t_math"].get_tools())
            self.tools.update(LOADED_TOOLS["t_search"].get_tools())
            self.tools.update(LOADED_TOOLS["t_obsidian"].get_tools())
            self.tools.update(LOADED_TOOLS["t_file"].get_tools())
            self.tools.update(LOADED_TOOLS["t_html"].get_tools())
            self.tools.update(LOADED_TOOLS["t_data"].get_tools())
            self.tools.update(LOADED_TOOLS["t_tree"].get_tools())
            self.tools.update(LOADED_TOOLS["t_state"].get_tools())
            self.tools.update(LOADED_TOOLS["t_bazi"].get_tools())
            
            if LOADED_TOOLS.get("t_name_analysis") and hasattr(LOADED_TOOLS["t_name_analysis"], "get_tools"):
                self.tools.update(LOADED_TOOLS["t_name_analysis"].get_tools())

            if LOADED_TOOLS.get("t_thai_astro") and hasattr(LOADED_TOOLS["t_thai_astro"], "get_tools"):
                self.tools.update(LOADED_TOOLS["t_thai_astro"].get_tools())
                
            if LOADED_TOOLS.get("t_jyotish") and hasattr(LOADED_TOOLS["t_jyotish"], "get_tools"):
                self.tools.update(LOADED_TOOLS["t_jyotish"].get_tools())
                
            if LOADED_TOOLS.get("t_western_astro") and hasattr(LOADED_TOOLS["t_western_astro"], "get_tools"):
                self.tools.update(LOADED_TOOLS["t_western_astro"].get_tools())
                
            if hasattr(LOADED_TOOLS.get("t_utils"), "get_tools"):
                self.tools.update(LOADED_TOOLS["t_utils"].get_tools())
                
            self.tools.setdefault("answer_question", LOADED_TOOLS["t_search"].search_local_knowledge)
            self.tools.setdefault("search_knowledge", LOADED_TOOLS["t_search"].search_local_knowledge)
            self.tools.setdefault("handle_conversation", self._chat_handler)
            
        except Exception as e:
            logger.critical(f"Critical error registering external tools: {e}. Falling back to mocks.")
            self._register_fallback_tools()

    def _ensure_critical_fallbacks(self) -> None:
        """
        ตรวจสอบสิทธิ์เพื่อให้แน่ใจว่าเครื่องมือพยากรณ์หลักมีฟังก์ชันผู้ช่วยรองรับอยู่เสมอ
        """
        # ลงทะเบียนสัญญานพยากรณ์รวมมหาชะตา 4 ศาสตร์
        self.tools.setdefault("comprehensive_astrology", self._comprehensive_astrology_handler)
        self.tools.setdefault("astrology", self._comprehensive_astrology_handler)
        self.tools.setdefault("ดูดวง", self._comprehensive_astrology_handler)
        self.tools.setdefault("วิเคราะห์ดวง", self._comprehensive_astrology_handler)

        self.tools.setdefault("name_analysis", self.tools.get("analyze_thai_name") or self._name_analysis_fallback)
        self.tools.setdefault("analyze_name", self.tools.get("analyze_thai_name") or self._name_analysis_fallback)
        self.tools.setdefault("NAME ANALYSIS", self.tools.get("analyze_thai_name") or self._name_analysis_fallback)
        
        self.tools.setdefault("thai_astro", self.tools.get("thai_astrology_chart") or self._thai_astro_fallback_handler)
        self.tools.setdefault("thai_astrology_chart", self.tools.get("thai_astro") or self._thai_astro_fallback_handler)

    def _comprehensive_astrology_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        """
        สะพานจัดรวบรวมรายงานพยากรณ์รวม 4 มิติสากล (Comprehensive Master Astrology Coordinator)
        ทลายสิทธิล็อคดาวจีนเดิม แล้วสวีกวาดผลทำนายจาก จีน ไทย อินเดีย ฝรั่ง มาเย็บรวมเล่มพยากรณ์ใหญ่สวยงาม
        """
        reports = []
        
        # 1. โหลดพยากรณ์ดวงจีน (Bazi)
        bazi_func = self.tools.get("bazi")
        if bazi_func:
            try:
                res = bazi_func(action, inp, entities)
                if isinstance(res, dict) and res.get("status") == "success":
                    reports.append("## ☯️ มิติที่ 1: บาซี่ชะตาลิขิต (โหราศาสตร์จีน - BaZi Astrology)\n\n" + res.get("result", ""))
            except Exception as e:
                logger.error(f"Error compiling Bazi in master report: {e}")
                
        # 2. โหลดพยากรณ์ดวงชะตากำเนิดไทย (Thai Astro)
        thai_func = self.tools.get("thai_astro")
        if thai_func:
            try:
                res = thai_func(action, inp, entities)
                if isinstance(res, dict) and res.get("status") == "success":
                    # นำหัวข้อใหญ่ออกเพื่อความสวยงามในสารบัญรายงานหลัก
                    cleaned_report = re.sub(r"^##\s+โหราศาสตร์ไทย.*?\n", "", res.get("result", ""), flags=re.IGNORECASE)
                    reports.append("## 🕉️ มิติที่ 2: โหราศาสตร์ไทยดวงกำเนิด (ดวงสิบลายลักษณ์)\n\n" + cleaned_report)
            except Exception as e:
                logger.error(f"Error compiling Thai Astro in master report: {e}")
                
        # 3. โหลดพยากรณ์ดวงภพพระเวท (Vedic Jyotish)
        jyotish_func = self.tools.get("jyotish")
        if jyotish_func:
            try:
                res = jyotish_func(action, inp, entities)
                if isinstance(res, dict) and res.get("status") == "success":
                    cleaned_report = re.sub(r"^##\s+Jyotish.*?\n", "", res.get("result", ""), flags=re.IGNORECASE)
                    reports.append("## 🪐 มิติที่ 3: โหราศาสตร์พระเวทอินเดีย (Vedic Jyotish)\n\n" + cleaned_report)
            except Exception as e:
                logger.error(f"Error compiling Jyotish in master report: {e}")
                
        # 4. โหลดพยากรณ์ดวงจิตวิทยาฝรั่ง (Western Astrology)
        western_func = self.tools.get("western_astro")
        if western_func:
            try:
                res = western_func(action, inp, entities)
                if isinstance(res, dict) and res.get("status") == "success":
                    cleaned_report = re.sub(r"^##\s+Western.*?\n", "", res.get("result", ""), flags=re.IGNORECASE)
                    reports.append("## 🌟 มิติที่ 4: โหราศาสตร์จิตวิทยาสากลตะวันตก (Western Astrology)\n\n" + cleaned_report)
            except Exception as e:
                logger.error(f"Error compiling Western Astro in master report: {e}")
                
        if not reports:
            return {
                "status": "fail",
                "message": "ไม่พบโมดูลพยากรณ์ดวงชะตาระบบใด ๆ ที่พร้อมใช้งานในระบบขณะนี้"
            }
            
        # ผนึกกำลังรายงานพยากรณ์ขนาดใหญ่ให้เป็นสากลสูงสุด
        master_report = [
            "# 🌟 มหารายงานพยากรณ์ประสานชะตาลิขิต 4 มิติสากล (Master Astrology & Destiny Synthesis)",
            "*(ทำการประมวลผลคำนวณถอดรหัสรอยนิ้วมือจักรวาลแบบบูรณาการรายบุคคล)*",
            "",
            "\n\n--ะ--\n\n".join(reports),
            "\n\n---\n## 📝 บทพิจารณาสรุปพิกัดนำทางจิตวิญญาณแบบสากล",
            "เมื่อพิจารณามวลพลังงานดวงดาวของทั้ง 4 ระบบโบราณ จะพบจุดร่วมที่น่าทึ่งมากในการเรียนรู้และแก้กรรมดวงชะตา ขอแนะนำให้นำพลังความทรหดและวินัยของดาวเสาร์ (เสาร์เรือนการงานของไทยและอินเดีย) มาประคับประคองการกระทำ และน้อมนำสมาธิปัญญาความดีของดาวพฤหัสบดีมานำทางชีวิต ชะตาชีวิตของคุณจะเคลื่อนตัวเข้าสู่ความมั่นคง มั่งคั่ง และสงบสุขอย่างสมบูรณ์แบบถาวรในทุกศาสตร์ลิขิตครับ"
        ]
        
        return {
            "status": "success",
            "result": "\n\n".join(master_report),
            "direct_response": True
        }

    def _thai_astro_fallback_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        """
        ระบบแจ้งเตือนกรณีดึงโมดูลดวงชะตากำเนิดไทยขึ้นมารันล้มเหลว (มักเกิดจากลืมติดตั้ง pyswisseph บนโอเอส)
        """
        response_text = (
            f"❌ **สัญญานความพร้อมล้มเหลว:** ไม่สามารถผูกดวงชะตากำเนิดเชิงลึกได้ในขณะนี้ครับ\n"
            f"- **สาเหตุเชิงระบบ:** เครื่องยนต์ตรวจพบว่าระบบปฏิบัติการปัจจุบันยังไม่ได้ติดตั้งหรือทำการคอมไพล์ไลบรารีดาราศาสตร์ "
            f"`pyswisseph` (Swiss Ephemeris Support) ลงสู่ระบบแกนหลัก\n"
            f"- **แนวทางการแก้ไข:** แนะนำให้ใช้ผู้บำรุงรักษาระบบ (Developer) ดำเนินการรันชุดคำสั่งด้านล่างนี้เพื่อเปิดสิทธิ์ความสามารถเต็มพิกัดของ Jinx:\n"
            f"  ```bash\n"
            f"  pip install pyswisseph\n"
            f"  ```"
        )
        return {
            "status": "fail",
            "result": response_text,
            "direct_response": True
        }

    def _name_analysis_fallback(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        """
        ระบบประมวลผลคำนวณและวิเคราะห์ชื่อย่อมงคลแบบพยัญชนะไทยนำ (Fallback Engine)
        """
        target_name = entities[0] if entities else inp
        clean_name = re.sub(r'[^ก-๙]', '', target_name)
        
        if not clean_name:
            return {
                "status": "fail",
                "message": "ไม่พบชื่อภาษาไทยที่สามารถนำมาคำนวณเลขศาสตร์ได้ กรุณระบุชื่อเป็นภาษาไทยที่ถูกต้อง"
            }
            
        total_sum = sum(self.thai_numerology_map.get(char, 0) for char in clean_name)
        
        if total_sum <= 100:
            response_text = (
                f"วิเคราะห์ข้อมูลสำหรับชื่อ **'{clean_name}'** เรียบร้อยแล้วครับ\n"
                f"- **ผลรวมเลขศาสตร์ดวงดาว:** ได้หมายเลข **{total_sum}**\n"
                f"- **แนวทางการพยากรณ์:** ระบบตรวจพบค่ารหัสพลังดวงดาวหมายเลข {total_sum} "
                f"ซึ่งคุณสามารถนำผลรวมนี้ไปเทียบเคียงกับรายงานบทวิเคราะห์เชิงลึกที่ระบุไว้ใน "
                f"`numerology.md` ได้ทันทีครับ 💯"
            )
        else:
            reduced_sum = total_sum
            while reduced_sum > 9:
                reduced_sum = sum(int(digit) for digit in str(reduced_sum))
                
            response_text = (
                f"วิเคราะห์ข้อมูลสำหรับชื่อ **'{clean_name}'** เรียบร้อยแล้วครับ\n"
                f"- **ผลรวมเลขศาสตร์ดวงดาว:** ได้หมายเลข **{total_sum}**\n"
                f"- **แนวทางการพยากรณ์:** เนื่องจากผลรวมมีค่าเกินเกณฑ์ 100 ระบบจึงทำการลดรูปกำลังเลขศาสตร์ "
                f"ตามโครงสร้าง Digital Root ได้รหัสหมายเลข **{reduced_sum}** "
                f"ซึ่งคุณสามารถนำรหัสผลลัพธ์ชุดย่อย **{reduced_sum}** นี้ ไปเทียบเคียงความหมายดวงดาวพื้นฐาน "
                f"ในรายงานวิจัยเจาะลึก `numerology.md` ได้ทันทีครับ ✨"
            )
        
        return {
            "status": "success",
            "result": response_text,
            "direct_response": True
        }

    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        ทางเข้าหลักการทำงานของ Engine คัดกรองความปลอดภัย รันคำสั่ง และจัดระเบียบสัญญาณกลับคืน Orchestrator
        """
        domain = plan.get("domain", "general")
        action = plan.get("action", "")
        inp = plan.get("topic", "") or plan.get("raw", "")
        entities = plan.get("entities", [])
        tasks = plan.get("tasks", [])
        
        metadata = plan.get("metadata", {})
        response_hint = plan.get("response_hint", {})
        
        handler_key = action or domain or (tasks[0] if tasks else "noop")
        handler = self.tools.get(handler_key)
        
        if not handler:
            for key in [action, domain] + tasks:
                if key and key in self.tools:
                    handler = self.tools[key]
                    handler_key = key
                    break
        
        response_metadata = {**metadata, "response_hint": response_hint}
        
        if handler:
            try:
                skip_injection = handler_key in WORKSPACE_TOOL_KEYS
                if not skip_injection and (
                    self._is_dangerous(str(inp)) or any(self._is_dangerous(str(e)) for e in entities)
                ):
                    return {
                        "status": "fail", 
                        "message": "Security Alert: ตรวจพบโครงสร้างสตริงสุ่มเสี่ยงต่อภัยบุกรุกบนพารามิเตอร์ส่งผ่าน",
                        "metadata": response_metadata
                    }
                
                output = handler(action, inp, entities)
                
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
                logger.error(f"Runtime execution error on handler '{handler_key}': {e}")
                return {
                    "status": "error", 
                    "message": f"Execution Error: {type(e).__name__} - {str(e)}", 
                    "result": None,
                    "metadata": response_metadata
                }
        
        return {
            "status": "noop", 
            "result": inp, 
            "message": f"No active tool registered for key: '{handler_key}'",
            "metadata": response_metadata
        }

    def _is_dangerous(self, text: str) -> bool:
        """
        สแกนตัดช่องว่างและข้อความเพื่อประเมินเกณฑ์ความปลอดภัยของคำสั่งส่งผ่าน
        """
        normalized_text = re.sub(r'\s+', '', text).lower()
        return any(pat.lower() in normalized_text for pat in self.forbidden_patterns)

    # ==========================================
    # CORE COGNITIVE UTILITIES & AST EVALUATORS
    # ==========================================

    def _math_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        """
        ระบบคำนวณคณิตศาสตร์แบบปลอดภัย (Secure AST Mathematical Evaluator)
        """
        clean_expr = inp.replace("^", "**").replace("=", "==").strip()
        
        try:
            tree = ast.parse(clean_expr, mode='eval')
            
            safe_operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
                ast.UAdd: operator.pos,
            }
            
            safe_functions = {
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "abs": abs,
            }
            
            def _eval_node(node):
                if isinstance(node, ast.Constant):  
                    if isinstance(node.value, (int, float)):
                        return node.value
                    raise TypeError("Unsupported constant value type.")
                elif isinstance(node, ast.Num):  
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = _eval_node(node.left)
                    right = _eval_node(node.right)
                    op_type = type(node.op)
                    if op_type in safe_operators:
                        return safe_operators[op_type](left, right)
                    raise TypeError(f"Unsupported binary operator: {op_type.__name__}")
                elif isinstance(node, ast.UnaryOp):
                    operand = _eval_node(node.operand)
                    op_type = type(node.op)
                    if op_type in safe_operators:
                        return safe_operators[op_type](operand)
                    raise TypeError(f"Unsupported unary operator: {op_type.__name__}")
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in safe_functions:
                        func = safe_functions[node.func.id]
                        args = [_eval_node(arg) for arg in node.args]
                        return func(*args)
                    raise TypeError("Unsupported function execution path.")
                raise TypeError(f"Unsupported operation token: {type(node).__name__}")
                
            result = _eval_node(tree.body)
            
            if isinstance(result, float):
                result = round(result, 6) if abs(result) < 1e10 else result
            return {"status": "success", "result": result}
            
        except ZeroDivisionError:
            return {"status": "fail", "message": "เกิดข้อผิดพลาดในการประมวลผล: ไม่สามารถหารด้วยเลขศูนย์ได้"}
        except Exception as e:
            return {"status": "fail", "message": f"การคำนวณวิเคราะห์สมการคณิตศาสตร์ล้มเหลว: {str(e)}"}

    def _search_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        query = inp or " ".join(entities) if entities else "unknown"
        return {
            "status": "success",
            "result": [{"title": f"ข้อมูลจำลองสตรีมมิ่งสำหรับ: {query}", "snippet": "ผลลัพธ์สถิติจากคลังฐานข้อมูลสำรอง"}],
            "query": query
        }

    def _file_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        path = entities[0] if entities else inp
        if not path:
            return {"status": "fail", "message": "ไม่พบข้อมูลพาธไฟล์เป้าหมายที่ต้องการตรวจสอบ"}
        if ".." in path or path.startswith("/"):
            return {"status": "fail", "message": "Security Warning: เส้นทางเข้าถึงระบุไฟล์มีความสุ่มเสี่ยงต่อระบบแกนหลัก"}
        return {
            "status": "success",
            "result": {"exists": os.path.exists(path), "path": path}
        }

    def _chat_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
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
                    except Exception as e:
                        logger.warning(f"Failed chatting with provider: {e}")
                        continue
        return {"status": "success", "result": inp}

    def _qa_handler(self, action: str, inp: str, entities: list) -> Dict[str, Any]:
        if TOOLS_AVAILABLE and "t_search" in LOADED_TOOLS:
            try:
                return LOADED_TOOLS["t_search"].search_local_knowledge(action, inp, entities)
            except Exception as e:
                logger.error(f"Fallback QA logic execution failed: {e}")
        return {"status": "success", "result": f"คลังสำรองไม่พบข้อมูลจำเพาะสำหรับ '{inp}'"}