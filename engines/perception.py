# engines/perception.py

import re
import unicodedata
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

@dataclass(frozen=True)
class PerceptionOutput:
    raw: str
    clean: str
    intent: str
    domain: str
    action: str
    entities: List[str]
    topic: str
    confidence: float
    is_chitchat: bool
    is_question: bool
    requires_response: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PerceptionEngine:
    """
    Perception Engine: ทำความเข้าใจเจตนา คัดแยกสัญญานเป้าหมาย และคัดกรองระบบชื่อศาสตร์แยกเฉพาะออกจากโหราศาสตร์ไทย
    """
    
    def __init__(self):
        # ========== REGEX PATTERNS ==========
        self.math_pattern = re.compile(r"([a-zA-Z0-9\.]+)\s*([+\-*/^%=<>!]+)\s*([a-zA-Z0-9\.]+)")
        self.has_math_ops = re.compile(r"[+\-*/^=]")
        self.file_pattern = re.compile(r"([a-zA-Z0-9_\-.]+(?:\.(?:md|json|py|log|txt|csv|yaml|yml|conf|js|html|css)))")
        self.url_pattern = re.compile(r"(https?://[^\s]+)")
        
        # ========== INTENT MAP ==========
        self.intent_keywords = {
            "task:solve": ["คำนวณ", "แก้", "solve", "บวก", "ลบ", "คูณ", "หาร", "เท่ากับ", "สมการ", "ผลลัพ", "หาค่า", "เท่าไร", "เท่าไหร่", "ได้เท่าไหร่", "กี่"],
            "task:edit": ["แก้ไข", "ปรับปรุง", "edit", "update", "modify", "fix", "เปลี่ยน", "patch"],
            "task:search": ["ค้นหา", "หา", "search", "find", "query", "สืบค้น", "ขอดูข้อมูล", "ค้นหาข้อมูล"],
            "task:analyze": ["วิเคราะห์", "analyze", "ตรวจสอบ", "check", "examine", "investigate", "สรุป", "สถิติ", "ข้อมูล", "csv"],
            "task:html": ["html", "เว็บ", "หน้าเว็บ", "web page", "สร้างหน้า", "การ์ด", "card", "เว็บเพจ"],
            
            # 🪐 ลงทะเบียนกลุ่มคำเฉพาะของโมดูลชื่อศาสตร์มงคลและเลขศาสตร์
            "task:name_analysis": ["วิเคราะห์ชื่อ", "ชื่อมงคล", "เลขศาสตร์ชื่อ", "ตั้งชื่อ", "วิเคราะห์ชื่อมงคล", ".name"],
            
            "task:western_astro": ["western", "western_astro", "ดูดวงฝรั่ง", "ฝรั่ง", "โหราศาสตร์สากล", "sun sign", "rising", "big three"],
            "task:astrology": ["ดูดวง", "บาซี่", "bazi", "astrology", "ปีนักษัตร", "นักษัตร", "ชะตา", "หมอดู", "วิเคราะห์ดวง"],
            "task:thai_astro": ["โหราศาสตร์ไทย", "พรหมชาติ", "นวางค์", "พระเคราะห์", "ฤกษ์", "เลขศาสตร์"],
            "task:jyotish": ["jyotish", "vedic", "ดูดวงอินเดีย", "โหราศาสตร์อินเดีย", "ภพ", "dasha"],
            "task:tree": ["tree", "decision tree", "ทางเลือก", "ตัดสินใจ", "คำถามนำทาง", "แนะนำ"],
            "task:state": ["state", "machine", "สถานะ", "workflow", "event", "เดินเครื่อง"],
            "task:show": ["แสดง", "โชว์", "display", "show", "view", "list", "ขอดู"],
            "task:open": ["เปิด", "read", "open"],
            "task:create": ["สร้าง", "ทำ", "new", "create", "write", "generate", "เขียน"],
            "task:delete": ["ลบ", "remove", "delete", "destroy", "ล้าง"],
            "task:copy": ["คัดลอก", "copy", "duplicate", "cp"],
            "task:move": ["ย้าย", "move", "mv"],
            "task:rename": ["เปลี่ยนชื่อ", "rename"],
            "task:debug": ["แก้บั๊ก", "debug", "หาข้อผิดพลาด", "trace"],
            "task:test": ["ทดสอบ", "test", "run test", "verify"],
            "task:execute": ["รัน", "run", "execute", "เริ่มทำงาน", "ประมวลผล"],
            
            "chat:greet": ["สวัสดี", "หวัดดี", "hello", "hi", "ว่าไง", "ทักทาย"],
            "chat:farewell": ["ลาก่อน", "บาย", "goodbye", "bye", "ไว้เจอกัน", "ไปละ"],
            "chat:gratitude": ["ขอบคุณ", "ขอบใจ", "thanks", "thank you", "แต๊งคิว"],
            "chat:apology": ["ขอโทษ", "sorry", "apologize"],
            "chat:chitchat": ["เป็นไง", "สบายดีไหม", "ทำอะไรอยู่", "เบื่อ", "เหงา", "คุยกับฉัน"],
            "chat:emotion": ["เครียด", "สุข", "เศร้า", "เหนื่อย", "ดีใจ", "โกรธ", "ท้อ"],
            "chat:joke": ["เล่าตลก", "ขอเพลง", "แนะนำหนัง", "เล่นอะไรหน่อย", "มุก"],
            "chat:compliment": ["เก่ง", "ฉลาด", "ดีจัง", "ชอบ", "ประทับใจ"],
            
            "qa:what": ["คืออะไร", "อะไร", "what", "หมายถึง"],
            "qa:why": ["ทำไม", "why", "เหตุผล", "เพราะอะไร"],
            "qa:how": ["อย่างไร", "ยังไง", "how", "วิธี"],
            "qa:who": ["ใคร", "who", "ผู้ใด"],
            "qa:when": ["เมื่อไหร่", "when", "เวลา"],
            "qa:where": ["ที่ไหน", "where", "สถานที่"],
            "qa:explain": ["ช่วยอธิบาย", "บอกฉันเกี่ยวกับ", "เล่าให้ฟัง"],
        }
        
        # ========== DOMAIN KEYWORDS ==========
        self.domain_keywords = {
            "math": ["เลข", "คณิต", "math", "ทศนิยม", "ค่า", "สมการ", "สูตร", "คำนวณ", "คูณ", "บวก", "ลบ", "หาร"],
            "file": ["ไฟล์", "file", "เอกสาร", ".py", ".json", ".md", ".txt"],
            "web": ["เว็บ", "website", "url", "ลิงก์", "http", "ค้นหา", "สืบค้น"],
            "code": ["โค้ด", "code", "python", "script", "def", "import"],
            "conversation": ["คุย", "พูด", "แชท", "คุยเล่น", "เล่า", "สวัสดี", "ยินดี"]
        }
        
        self.chitchat_signals = [
            r"^(สวัสดี|hello|hi|hey|ว่าไง).*",
            r".*(ไหม|มั้ย|เหรอ|หรอ|นะครับ|นะคะ|จ้า|ครับ|ค่ะ)$",
            r".*(เบื่อ|เหงา|เหนื่อย|สุข|เศร้า|เครียด).*",
            r".*(วันนี้|เมื่อวาน|พรุ่งนี้|อากาศ|กิน).*",
            r"^(ฉัน|ผม|เรา|กู).*(อยาก|ชอบ|ไม่ชอบ|คิดว่า).*"
        ]
        self.chitchat_regex = [re.compile(p, re.IGNORECASE) for p in self.chitchat_signals]

    def perceive(self, text: str) -> Dict[str, Any]:
        clean_text = self._normalize(text)
        lower_text = clean_text.lower()
        
        intent = self._score_intent(lower_text)
        entities = self._extract_entities(clean_text)
        domain = self._score_domain(lower_text, entities, intent)
        
        # Override: ถ้ามี "html" และ intent เป็น task:create ให้ใช้ task:html แทน
        if intent == "task:create" and "html" in lower_text:
            intent = "task:html"
            domain = "general"
        
        # Override: "list_dir" → task:show + domain file
        if "list_dir" in lower_text:
            intent = "task:show"
            domain = "file"
        
        # ตรวจสอบเพื่อแยกเป้าหมายคณิตศาสตร์
        if intent == "unknown" and self._is_math_expression(clean_text):
            intent = "task:solve"
            domain = "math"
            
        if intent == "unknown" and self._is_chitchat(lower_text):
            intent = "chat:chitchat"
            domain = "conversation"
            
        if intent == "unknown" and self._is_question(lower_text) and domain != "math":
            intent = self._guess_question_type(lower_text)
            domain = "qa"
        
        if intent in ("task:create", "task:edit") and any(
            isinstance(e, str) and e.lower().endswith(tuple(self._code_extensions()))
            for e in entities
        ):
            domain = "code"

        confidence = self._compute_confidence(intent, domain, entities, lower_text)
        action = self._infer_action(intent, domain, entities)
        
        # คลีนภาษาและสกัดสูตรล่วงหน้า
        if domain == "math":
            topic = self._extract_math_formula(clean_text)
            entities = [topic] if topic else []
        else:
            topic = self._extract_topic(clean_text, intent)
            
        output = PerceptionOutput(
            raw=text,
            clean=clean_text,
            intent=intent,
            domain=domain,
            action=action,
            entities=entities,
            topic=topic,
            confidence=confidence,
            is_chitchat=intent.startswith("chat:"),
            is_question=intent.startswith("qa:"),
            requires_response=self._needs_response(intent)
        )
        
        return output.to_dict()

    def _normalize(self, text: str) -> str:
        text = "".join(c for c in text if unicodedata.category(c)[0] != "C" or c in " \n\t")
        text = "".join(chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in text)
        return re.sub(r"\s+", " ", text).strip()

    def _score_intent(self, text: str) -> str:
        best_intent = "unknown"
        max_score = 0
        max_kw_len = 0
        for intent, kw_list in self.intent_keywords.items():
            score = 0
            matched_max = 0
            for kw in kw_list:
                matches = len(re.findall(re.escape(kw), text))
                if matches > 0:
                    score += matches * (1 if len(kw) <= 2 else 2)
                    matched_max = max(matched_max, len(kw))
            if score > max_score or (score == max_score and matched_max > max_kw_len):
                max_score = score
                max_kw_len = matched_max
                best_intent = intent
        return best_intent

    def _score_domain(self, text: str, entities: List[str], intent: str) -> str:
        # 🪐 ดึงคีย์เจตนาวิเคราะห์ชื่อสอดประสานกับโมดูลดวงหลักเพื่อไม่ให้หลุดไปรันวิเคราะห์คณิตศาสตร์
        non_math_intents = {"task:astrology", "task:tree", "task:state", "task:html", "task:thai_astro", "task:jyotish", "task:western_astro", "task:name_analysis"}
        if intent in non_math_intents:
            return "general"
        if self._is_math_expression(text):
            return "math"
        if intent.startswith("task:solve"):
            return "math"
        if intent == "task:search":
            return "web"
            
        best_domain = "general"
        max_score = 0
        
        for domain, kw_list in self.domain_keywords.items():
            score = 0
            for kw in kw_list:
                matches = len(re.findall(re.escape(kw), text))
                if matches > 0:
                    score += matches * 1
            
            if domain == "file" and any(e.endswith((".md", ".json", ".py", ".txt")) for e in entities):
                score += 5
            if domain == "web" and any(e.startswith(("http", "www")) for e in entities):
                score += 5
                
            if score > max_score:
                max_score = score
                best_domain = domain
                
        if max_score == 0:
            if intent.startswith(("task:edit", "task:create", "task:delete")):
                return "file"
            if intent.startswith(("chat:", "qa:")):
                return "conversation"
                
        return best_domain

    def _extract_entities(self, text: str) -> List[str]:
        entities = []
        math_match = self.math_pattern.search(text)
        if math_match:
            entities.extend([math_match.group(1), math_match.group(2), math_match.group(3)])
        elif self._is_math_expression(text):
            entities.append(text.strip())
        
        files = self.file_pattern.findall(text)
        entities.extend([f[0] if isinstance(f, tuple) else f for f in files])
        urls = self.url_pattern.findall(text)
        entities.extend(urls)
        return list(set(entities))

    def _is_math_expression(self, text: str) -> bool:
        compiled = self._extract_math_formula(text)
        clean = compiled.replace(" ", "")
        has_ops = bool(self.has_math_ops.search(clean))
        has_numbers = any(c.isdigit() for c in clean)
        has_vars = any(c.isalpha() for c in clean)
        return has_ops and (has_numbers or has_vars) and len(clean) < 100

    def _is_chitchat(self, text: str) -> bool:
        has_command = bool(self.file_pattern.search(text) or self.url_pattern.search(text))
        if has_command:
            return False
        return any(regex.match(text) for regex in self.chitchat_regex)

    def _is_question(self, text: str) -> bool:
        return any(q in text for q in ["?", "ไหม", "มั้ย", "เหรอ", "หรอ", "อะไร", "ทำไม", "อย่างไร", "ใคร", "เมื่อไหร่", "ที่ไหน"])

    def _guess_question_type(self, text: str) -> str:
        if any(w in text for w in ["อะไร", "what", "หมายถึง"]): return "qa:what"
        if any(w in text for w in ["ทำไม", "why", "เพราะ"]): return "qa:why"
        if any(w in text for w in ["อย่างไร", "ยังไง", "how", "วิธี"]): return "qa:how"
        if any(w in text for w in ["ใคร", "who"]): return "qa:who"
        if any(w in text for w in ["เมื่อไหร่", "when", "เวลา"]): return "qa:when"
        if any(w in text for w in ["ที่ไหน", "where"]): return "qa:where"
        return "qa:explain"

    def _compute_confidence(self, intent: str, domain: str, entities: List[str], text: str) -> float:
        score = 0.0
        score += 0.4 if intent != "unknown" else 0.0
        score += 0.3 if domain != "general" else 0.0
        score += 0.3 if entities else 0.0
        if intent != "unknown" and entities and domain != "general":
            score = min(score + 0.1, 1.0)
        return round(min(score, 1.0), 2)

    def _code_extensions(self) -> tuple:
        return (".py", ".ts", ".tsx", ".js", ".json", ".yaml", ".yml", ".html", ".css")

    def _infer_action(self, intent: str, domain: str, entities: Optional[List[str]] = None) -> str:
        entities = entities or []
        has_code_file = any(
            isinstance(e, str) and e.lower().endswith(self._code_extensions()) for e in entities
        )
        has_md_file = any(
            isinstance(e, str) and e.lower().endswith((".md", ".txt")) for e in entities
        )

        if intent == "task:create" and (domain == "code" or has_code_file):
            return "write_code"
        if intent == "task:edit" and (domain == "code" or has_code_file):
            return "write_code"
        if intent == "task:create" and has_md_file:
            return "create_note"

        action_map = {
            ("task:solve", "math"): "compute_math",
            ("task:edit", "file"): "vault_write",
            ("task:delete", "file"): "delete_file",
            ("task:copy", "file"): "copy_file",
            ("task:move", "file"): "move_file",
            ("task:execute", "code"): "run_script",
            ("task:debug", "code"): "read_code",
            ("task:search", "web"): "web_search",
            
            # ── 🪐 ผูกค่าสัญญาณเจตนาไปเรียกโมดูลตรวจสอบประวัติวิเคราะห์ชื่อสถาปัตยกรรมใหม่ ──
            ("task:name_analysis", "general"): "name_analysis",
            ("task:name_analysis", "web"): "name_analysis",
            
            ("task:astrology", "general"): "comprehensive_astrology",
            ("task:astrology", "web"): "comprehensive_astrology",
            ("task:thai_astro", "general"): "thai_astro",
            ("task:thai_astro", "web"): "thai_astro",
            ("task:jyotish", "general"): "jyotish",
            ("task:jyotish", "web"): "jyotish",
            ("task:western_astro", "general"): "western_astro",
            ("task:western_astro", "web"): "western_astro",
            ("qa:what", "general"): "vault_search",
            ("task:open", "general"): "vault_read",
            ("task:html", "general"): "generate_html",
            ("task:html", "web"): "generate_html",
            ("task:analyze", "web"): "analyze_data",
            ("task:analyze", "general"): "analyze_data",
            ("task:tree", "general"): "decision_tree",
            ("task:state", "general"): "state_machine",
            ("task:show", "file"): "list_dir",
            ("qa:what", "qa"): "answer_definition",
            ("qa:how", "qa"): "answer_procedure",
            ("qa:why", "qa"): "answer_reason",
        }
        key = (intent, domain)
        if key in action_map:
            return action_map[key]
        if intent.startswith("chat:"): return "handle_conversation"
        if intent.startswith("qa:"): return "answer_question"
        if intent.startswith("task:"): return f"{intent.split(':')[-1]}_{domain}"
        return "noop"

    def _extract_topic(self, text: str, intent: str) -> str:
        if intent.startswith(("chat:", "qa:")):
            return text.strip()
        keywords = []
        for intent_key, kw_list in self.intent_keywords.items():
            if intent_key == intent or intent_key.split(":")[-1] == intent.split(":")[-1]:
                keywords.extend(kw_list)
        if keywords:
            pattern = "|".join(r"\b" + re.escape(kw) + r"\b" for kw in keywords)
            topic = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
            return topic if topic else text
        return text.strip()

    def _needs_response(self, intent: str) -> bool:
        return intent not in ["task:delete", "task:copy", "task:move"]

    def _extract_math_formula(self, text: str) -> str:
        clean = text.lower().strip()
        strip_words = [
            "ถ้า", "เมื่อ", "กำหนดให้", "จงหา", "หาค่า", "คำนวณ", "ได้เท่าไหร่", "เท่ากับเท่าไหร่", "คืออะไร",
            "if", "when", "given", "find", "answer", "solve", "determine", "what is", "calculate", "หาค่าของ"
        ]
        for w in strip_words:
            clean = re.sub(rf"\b{w}\b", "", clean)
            clean = clean.replace(w, "")
            
        clean = re.sub(r"([a-zA-Z0-9]+)\s*มากกว่า\s*([a-zA-Z0-9]+)\s*[\u0e00-\u0e7f\s]*\s*([a-zA-Z0-9.]+)", r"\1 - \2 = \3", clean)
        clean = re.sub(r"\b([a-zA-Z0-9]+)\s*more\s*than\s*([a-zA-Z0-9]+)\s*(?:equal|is|equals|equal\s*to|\s)*\s*([a-zA-Z0-9.]+)", r"\1 - \2 = \3", clean)
        
        clean = re.sub(r"([a-zA-Z0-9]+)\s*น้อยกว่า\s*([a-zA-Z0-9]+)\s*[\u0e00-\u0e7f\s]*\s*([a-zA-Z0-9.]+)", r"\2 - \1 = \3", clean)
        clean = re.sub(r"\b([a-zA-Z0-9]+)\s*less\s*than\s*([a-zA-Z0-9]+)\s*(?:equal|is|equals|equal\s*to|\s)*\s*([a-zA-Z0-9.]+)", r"\2 - \1 = \3", clean)
        
        clean = re.sub(r"(?:และ|เเละ|เละ)", ",", clean)
        clean = re.sub(r"\band\b", ",", clean)
        clean = re.sub(r"\bเเละ\b", ",", clean)
        
        clean = re.sub(r"\bเท่ากับ\b", "=", clean)
        clean = re.sub(r"\bเท่า\b", "=", clean)
        clean = re.sub(r"\b(?:is|equal|equals)\b", "=", clean)
        
        clean = re.sub(r"\bบวก\b", "+", clean)
        clean = re.sub(r"\bรวมกับ\b", "+", clean)
        clean = re.sub(r"\bplus\b", "+", clean)
        
        clean = re.sub(r"\bลบ\b", "-", clean)
        clean = re.sub(r"\bหักออก\b", "-", clean)
        clean = re.sub(r"\bminus\b", "-", clean)
        
        clean = re.sub(r"\bคูณ\b", "*", clean)
        clean = re.sub(r"\bคูณกับ\b", "*", clean)
        clean = re.sub(r"\btimes\b", "*", clean)
        
        clean = re.sub(r"\bหาร\b", "/", clean)
        clean = re.sub(r"\bหารด้วย\b", "/", clean)
        clean = re.sub(r"\bdivide\b", "/", clean)
        clean = re.sub(r"\bdivided by\b", "/", clean)

        clean = re.sub(r"\s+[a-zA-Z](?:\s*,\s*[a-zA-Z\s])*$", "", clean)
        clean = re.sub(r"[\u0e00-\u0e7f]", "", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        clean = re.sub(r"\s*,\s*", ", ", clean)
        return clean