# engines/perception.py

import re
import unicodedata
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple

@dataclass(frozen=True)
class PerceptionOutput:
    """
    โครงสร้างข้อมูลมาตรฐาน (Schema) ของชั้นรับรู้ ป้องกันข้อผิดพลาดเชิงไวยากรณ์ในด่านถัดไป
    """
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
    Perception Layer (ฉบับอัปเกรด): สกัดและวิเคราะห์อินพุตด้วยเกณฑ์คะแนนเชิงน้ำหนัก (Weighted Scoring)
    """
    
    def __init__(self):
        # ========== REGEX PATTERNS ==========
        self.math_pattern = re.compile(r"([a-zA-Z0-9\.]+)\s*([+\-*/^%=<>!]+)\s*([a-zA-Z0-9\.]+)")
        self.has_math_ops = re.compile(r"[+\-*/^=]")
        self.file_pattern = re.compile(r"([a-zA-Z0-9_\-.]+(?:\.(?:md|json|py|log|txt|csv|yaml|yml|conf|js|html|css)))")
        self.url_pattern = re.compile(r"(https?://[^\s]+)")
        
        # ========== INTENT MAP (จัดกลุ่มกลุ่มคีย์เวิร์ดเพื่อวัดคะแนนความหนาแน่น) ==========
        self.intent_keywords = {
            "task:solve": ["คำนวณ", "แก้", "solve", "บวก", "ลบ", "คูณ", "หาร", "เท่ากับ", "สมการ", "ผลลัพ", "หาค่า", "เท่าไร", "เท่าไหร่", "ได้เท่าไหร่", "กี่"],
            "task:edit": ["แก้ไข", "ปรับปรุง", "edit", "update", "modify", "fix", "เปลี่ยน", "patch"],
            "task:search": ["ค้นหา", "หา", "search", "find", "query", "สืบค้น", "ขอดูข้อมูล", "ค้นหาข้อมูล"],
            "task:analyze": ["วิเคราะห์", "analyze", "ตรวจสอบ", "check", "examine", "investigate", "สรุป"],
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
            r"^([สหว]|hello|hi|hey|ว่าไง).*",
            r".*(ไหม|มั้ย|เหรอ|หรอ|นะ|จ้า|ครับ|ค่ะ)$",
            r".*(เบื่อ|เหงา|เหนื่อย|สุข|เศร้า|เครียด).*",
            r".*(วันนี้|เมื่อวาน|พรุ่งนี้|อากาศ|กิน).*",
            r"^(ฉัน|ผม|เรา|กู).*(อยาก|ชอบ|ไม่ชอบ|คิดว่า).*"
        ]
        self.chitchat_regex = [re.compile(p, re.IGNORECASE) for p in self.chitchat_signals]

    def perceive(self, text: str) -> Dict[str, Any]:
        """
        ประมวลผลข้อความนำเข้าเพื่อส่งออกเป็นโครงสร้างข้อมูลมาตรฐาน
        """
        clean_text = self._normalize(text)
        lower_text = clean_text.lower()
        
        # ค้นหา Intent และ Domain ด้วยระบบคำนวณคะแนนค่าน้ำหนักความสัมพันธ์
        intent = self._score_intent(lower_text)
        entities = self._extract_entities(clean_text)
        domain = self._score_domain(lower_text, entities, intent)
        
        # ระบบช่วยเหลือกรณีเป็นสมการคณิตศาสตร์ที่ไม่มีคีย์เวิร์ดนำทาง
        if intent == "unknown" and self._is_math_expression(clean_text):
            intent = "task:solve"
            domain = "math"
            
        # ระบบช่วยเหลือกรณีเป็นประโยคคุยเล่นทั่วไป
        if intent == "unknown" and self._is_chitchat(lower_text):
            intent = "chat:chitchat"
            domain = "conversation"
            
        # ระบบช่วยเหลือระบุหมวดหมู่คำถามหลัก (QA)
        if intent == "unknown" and self._is_question(lower_text) and domain != "math":
            intent = self._guess_question_type(lower_text)
            domain = "qa"
            
        confidence = self._compute_confidence(intent, domain, entities, lower_text)
        action = self._infer_action(intent, domain)
        
        # จัดระเบียบการแยกข้อมูลสมการ (คัดภาษาไทยออกเพื่อไม่ให้ปะปนในเครื่องมือคำนวณ)
        if domain == "math":
            topic = self._extract_math_formula(clean_text)
            entities = [topic] if topic else []
        else:
            topic = self._extract_topic(clean_text, intent)
            
        # บรรจุข้อมูลและตรวจสอบตามกติกาของ PerceptionOutput Schema
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
        """
        คำนวณและประเมินผล Intent ด้วยระบบค่าน้ำหนักความหนาแน่นสูงสุด (Weighted Scoring)
        """
        best_intent = "unknown"
        max_score = 0
        
        for intent, kw_list in self.intent_keywords.items():
            score = 0
            for kw in kw_list:
                # คำนวณคะแนนตามจำนวนที่ตรวจเจอ
                matches = len(re.findall(re.escape(kw), text))
                if matches > 0:
                    # คำสั้นหรือคีย์เวิร์ดย่อยได้คะแนนต่ำกว่าเพื่อป้องกัน false positive
                    score += matches * (1 if len(kw) <= 2 else 2)
            
            if score > max_score:
                max_score = score
                best_intent = intent
                
        return best_intent

    def _score_domain(self, text: str, entities: List[str], intent: str) -> str:
        """
        คำนวณประเมินผล Domain ด้วยระบบวิเคราะห์สัดส่วนคะแนนรวมและบริบทตัวแปรแวดล้อม
        """
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
            
            # ตรวจสอบตัวแปรทางกายภาพอื่นมาร่วมวิเคราะห์คะแนน
            if domain == "file" and any(e.endswith((".md", ".json", ".py", ".txt")) for e in entities):
                score += 5
            if domain == "web" and any(e.startswith(("http", "www")) for e in entities):
                score += 5
                
            if score > max_score:
                max_score = score
                best_domain = domain
                
        # หากไม่มีโดเมนใดมีคะแนนโดดเด่น ให้สืบหาโดเมนตาม Intent หลัก
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
        clean = text.replace(" ", "")
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

    def _infer_action(self, intent: str, domain: str) -> str:
        action_map = {
            ("task:solve", "math"): "compute_math",
            ("task:edit", "file"): "update_file",
            ("task:delete", "file"): "delete_file",
            ("task:copy", "file"): "copy_file",
            ("task:move", "file"): "move_file",
            ("task:execute", "code"): "run_script",
            ("task:debug", "code"): "debug_code",
            ("task:search", "web"): "web_search",
            ("chat:greet", "conversation"): "respond_greeting",
            ("chat:chitchat", "conversation"): "respond_chitchat",
            ("chat:emotion", "conversation"): "respond_empathy",
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
            pattern = "|".join(map(re.escape, keywords))
            topic = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
            return topic if topic else text
        return text.strip()

    def _needs_response(self, intent: str) -> bool:
        return intent not in ["task:delete", "task:copy", "task:move"]

    def _extract_math_formula(self, text: str) -> str:
        """สกัดกรองตัดอักขระภาษาไทยทิ้งทั้งหมด เหลือเฉพาะสัญญลักษณ์คณิตศาสตร์สากล"""
        clean = re.sub(r"[\u0e00-\u0e7f]", "", text)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean