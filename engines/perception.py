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

    def __init__(self):
        self.math_pattern = re.compile(
            r"([a-zA-Z0-9\.]+)\s*([+\-*/^%=<>!]+)\s*([a-zA-Z0-9\.]+)"
        )
        self.has_math_ops = re.compile(r"[+\-*/^=]")
        self.file_pattern = re.compile(
            r"([a-zA-Z0-9_\-.]+(?:\.(?:md|json|py|log|txt|csv|yaml|yml|conf|js|html|css)))"
        )
        self.url_pattern = re.compile(r"(https?://[^\s]+)")

        self.intent_keywords = {
            # ── Priority Intents (longer keywords win ties) ──
            "task:personality_analysis": [
                "วิเคราะห์คนนี้", "วิเคราะห์คน", "วิเคราะห์บุคลิก",
                "เขาเป็นคนแบบไหน", "เธอเป็นคนแบบไหน",
                "คนนี้เป็น", "อ่านคน", "ลักษณะนิสัย",
                "personality type", "mbti", "enneagram",
                "INFJ", "INTJ", "INFP", "INTP",
            ],
            "task:solve": [
                "คำนวณ", "แก้สมการ", "solve", "บวก", "ลบ", "คูณ", "หาร",
                "เท่ากับ", "สมการ", "ผลลัพ", "หาค่า", "เท่าไร", "เท่าไหร่",
                "ได้เท่าไหร่", "กี่",
            ],
            "task:astrology": [
                "ดูดวง", "บาซี่", "bazi", "astrology", "ปีนักษัตร",
                "นักษัตร", "ชะตา", "หมอดู", "วิเคราะห์ดวง", "ดวงชะตา",
            ],
            "task:name_analysis": [
                "วิเคราะห์ชื่อ", "ชื่อมงคล", "เลขศาสตร์ชื่อ", "ตั้งชื่อ",
            ],
            "task:western_astro": [
                "western", "ดูดวงฝรั่ง", "โหราศาสตร์สากล", "sun sign", "rising",
            ],
            "task:thai_astro": [
                "โหราศาสตร์ไทย", "พรหมชาติ", "นวางค์", "พระเคราะห์", "ฤกษ์",
            ],
            "task:jyotish": [
                "jyotish", "vedic", "ดูดวงอินเดีย", "โหราศาสตร์อินเดีย", "dasha",
            ],

            # ── General Tasks ──
            "task:search": ["ค้นหา", "search", "find", "สืบค้น"],
            "task:debug": ["แก้บั๊ก", "debug", "bug", "หาข้อผิดพลาด"],
            "task:html": ["html", "หน้าเว็บ", "web page", "การ์ด", "card"],
            "task:edit": ["แก้ไข", "edit", "update", "fix", "เปลี่ยน"],
            "task:create": ["สร้าง", "create", "generate", "เขียน"],
            "task:delete": ["ลบ", "remove", "delete"],
            "task:show": ["แสดง", "list", "ขอดู"],
            "task:open": ["เปิด", "read", "open"],
            "task:execute": ["รัน", "run", "execute", "ประมวลผล"],
            "task:test": ["ทดสอบ", "test"],

            # ── Chat ──
            "chat:greet": ["สวัสดี", "หวัดดี", "hello", "hi", "ว่าไง"],
            "chat:farewell": ["ลาก่อน", "บาย", "goodbye", "bye"],
            "chat:gratitude": ["ขอบคุณ", "ขอบใจ", "thanks"],
            "chat:apology": ["ขอโทษ", "sorry"],
            "chat:emotion": ["เครียด", "เศร้า", "เหนื่อย", "ดีใจ", "โกรธ", "ท้อ"],
            "chat:chitchat": ["สบายดีไหม", "ทำอะไรอยู่", "เบื่อ", "เหงา"],

            # ── Q&A ──
            "qa:what": ["คืออะไร", "อะไร", "what", "หมายถึง"],
            "qa:why": ["ทำไม", "why", "เพราะอะไร"],
            "qa:how": ["อย่างไร", "ยังไง", "how", "วิธี"],
            "qa:who": ["ใคร", "who"],
            "qa:when": ["เมื่อไหร่", "when"],
            "qa:where": ["ที่ไหน", "where"],
        }

        self.domain_keywords = {
            "math": ["เลข", "คณิต", "math", "สมการ", "คำนวณ"],
            "file": ["ไฟล์", "file", ".py", ".json", ".md"],
            "web": ["เว็บ", "url", "http", "ค้นหา"],
            "code": ["โค้ด", "code", "python", "script"],
            "conversation": ["คุย", "พูด", "แชท", "สวัสดี"],
        }

        self.chitchat_signals = [
            r"^(สวัสดี|hello|hi|hey|ว่าไง).*",
            r".*(เบื่อ|เหงา|เหนื่อย|สุข|เศร้า|เครียด).*",
            r"^(ฉัน|ผม|เรา|กู).*(อยาก|ชอบ|ไม่ชอบ|คิดว่า).*",
        ]
        self.chitchat_regex = [re.compile(p, re.IGNORECASE) for p in self.chitchat_signals]

    # ============================================================
    # MAIN
    # ============================================================

    def perceive(self, text: str) -> Dict[str, Any]:
        clean_text = self._normalize(text)
        lower_text = clean_text.lower()

        intent = self._score_intent(lower_text)
        entities = self._extract_entities(clean_text)
        domain = self._score_domain(lower_text, entities, intent)

        # Override: math expression
        if intent == "unknown" and self._is_math_expression(clean_text):
            intent = "task:solve"
            domain = "math"

        # Override: chitchat
        if intent == "unknown" and self._is_chitchat(lower_text):
            intent = "chat:chitchat"
            domain = "conversation"

        # Override: question
        if intent == "unknown" and self._is_question(lower_text) and domain != "math":
            intent = self._guess_question_type(lower_text)
            domain = "qa"

        confidence = self._compute_confidence(intent, domain, entities)
        action = self._infer_action(intent, domain, entities)

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
            requires_response=self._needs_response(intent),
        )

        return output.to_dict()

    # ============================================================
    # HELPERS
    # ============================================================

    def _normalize(self, text: str) -> str:
        text = "".join(c for c in text if unicodedata.category(c)[0] != "C" or c in " \n\t")
        text = "".join(
            chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in text
        )
        return re.sub(r"\s+", " ", text).strip()

    def _score_intent(self, text: str) -> str:
        best_intent = "unknown"
        best_score = 0
        best_len = 0

        for intent, kw_list in self.intent_keywords.items():
            score = 0
            max_len = 0
            for kw in kw_list:
                count = len(re.findall(re.escape(kw), text))
                if count > 0:
                    weight = len(kw) if len(kw) > 3 else 2
                    score += count * weight
                    max_len = max(max_len, len(kw))
            if score > best_score or (score == best_score and max_len > best_len):
                best_score = score
                best_len = max_len
                best_intent = intent

        return best_intent

    def _score_domain(self, text: str, entities: List[str], intent: str) -> str:
        non_math = {
            "task:astrology", "task:thai_astro", "task:jyotish",
            "task:western_astro", "task:name_analysis",
            "task:personality_analysis",
        }
        if intent in non_math:
            return "general"

        if self._is_math_expression(text) or intent.startswith("task:solve"):
            return "math"
        if intent == "task:search":
            return "web"

        best = "general"
        best_score = 0
        for domain, kw_list in self.domain_keywords.items():
            score = sum(len(re.findall(re.escape(kw), text)) for kw in kw_list)
            if domain == "file" and any(e.endswith((".md", ".json", ".py", ".txt")) for e in entities):
                score += 5
            if domain == "web" and any(e.startswith(("http", "www")) for e in entities):
                score += 5
            if score > best_score:
                best_score = score
                best = domain

        return best

    def _extract_entities(self, text: str) -> List[str]:
        entities = []
        m = self.math_pattern.search(text)
        if m:
            entities.extend([m.group(1), m.group(2), m.group(3)])
        elif self._is_math_expression(text):
            entities.append(text.strip())
        entities.extend(self.file_pattern.findall(text))
        entities.extend(self.url_pattern.findall(text))
        return list(set(entities))

    def _is_math_expression(self, text: str) -> bool:
        clean = self._extract_math_formula(text).replace(" ", "")
        return bool(self.has_math_ops.search(clean)) and any(c.isdigit() for c in clean) and len(clean) < 100

    def _is_chitchat(self, text: str) -> bool:
        if self.file_pattern.search(text) or self.url_pattern.search(text):
            return False
        return any(rgx.match(text) for rgx in self.chitchat_regex)

    def _is_question(self, text: str) -> bool:
        return any(q in text for q in ["?", "ไหม", "มั้ย", "เหรอ", "อะไร", "ทำไม", "อย่างไร", "ใคร", "เมื่อไหร่", "ที่ไหน"])

    def _guess_question_type(self, text: str) -> str:
        if any(w in text for w in ["อะไร", "what"]): return "qa:what"
        if any(w in text for w in ["ทำไม", "why"]): return "qa:why"
        if any(w in text for w in ["อย่างไร", "ยังไง", "how"]): return "qa:how"
        if any(w in text for w in ["ใคร", "who"]): return "qa:who"
        if any(w in text for w in ["เมื่อไหร่", "when"]): return "qa:when"
        if any(w in text for w in ["ที่ไหน", "where"]): return "qa:where"
        return "qa:explain"

    def _compute_confidence(self, intent: str, domain: str, entities: List[str]) -> float:
        score = 0.0
        if intent != "unknown": score += 0.4
        if domain != "general": score += 0.3
        if entities: score += 0.3
        return round(min(score, 1.0), 2)

    def _code_extensions(self) -> tuple:
        return (".py", ".ts", ".tsx", ".js", ".json", ".yaml", ".yml", ".html", ".css")

    def _infer_action(self, intent: str, domain: str, entities: Optional[List[str]] = None) -> str:
        entities = entities or []
        has_code = any(e.lower().endswith(self._code_extensions()) for e in entities)
        has_md = any(e.lower().endswith((".md", ".txt")) for e in entities)

        if intent == "task:create" and has_code: return "write_code"
        if intent == "task:edit" and has_code: return "write_code"
        if intent == "task:create" and has_md: return "create_note"

        action_map = {
            ("task:solve", "math"): "compute_math",
            ("task:astrology", "general"): "comprehensive_astrology",
            ("task:thai_astro", "general"): "thai_astro",
            ("task:jyotish", "general"): "jyotish",
            ("task:western_astro", "general"): "western_astro",
            ("task:name_analysis", "general"): "name_analysis",
            # 🆕 FIX: personality_analysis must map to person_analyzer
            ("task:personality_analysis", "general"): "person_analyzer",
            ("task:personality_analysis", "web"): "person_analyzer",
            ("task:search", "web"): "web_search",
            ("task:debug", "code"): "read_code",
            ("task:html", "general"): "generate_html",
            ("task:edit", "file"): "vault_write",
            ("task:delete", "file"): "delete_file",
            ("task:show", "file"): "list_dir",
            ("task:open", "general"): "vault_read",
            ("qa:what", "qa"): "answer_definition",
            ("qa:how", "qa"): "answer_procedure",
            ("qa:why", "qa"): "answer_reason",
        }

        key = (intent, domain)
        if key in action_map:
            return action_map[key]

        if intent.startswith("chat:"):
            return "handle_conversation"
        if intent.startswith("qa:"):
            return "answer_question"
        if intent.startswith("task:"):
            return f"{intent.split(':')[-1]}_{domain}"

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
        for w in ["ถ้า", "เมื่อ", "กำหนดให้", "จงหา", "หาค่า", "คำนวณ",
                   "ได้เท่าไหร่", "เท่ากับเท่าไหร่", "คืออะไร"]:
            clean = re.sub(rf"\b{w}\b", "", clean)
        clean = re.sub(r"\bเท่ากับ\b", "=", clean)
        clean = re.sub(r"\bเท่า\b", "=", clean)
        clean = re.sub(r"\bบวก\b", "+", clean)
        clean = re.sub(r"\bplus\b", "+", clean)
        clean = re.sub(r"\bลบ\b", "-", clean)
        clean = re.sub(r"\bminus\b", "-", clean)
        clean = re.sub(r"\bคูณ\b", "*", clean)
        clean = re.sub(r"\btimes\b", "*", clean)
        clean = re.sub(r"\bหาร\b", "/", clean)
        clean = re.sub(r"\bdivide\b", "/", clean)
        clean = re.sub(r"[\u0e00-\u0e7f]", "", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean


_perception_instance = None


def get_perception_engine() -> PerceptionEngine:
    global _perception_instance
    if _perception_instance is None:
        _perception_instance = PerceptionEngine()
    return _perception_instance