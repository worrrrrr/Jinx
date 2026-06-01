# engines/response.py

import random
import re
from typing import Dict, Any, List, Optional

from tools.math import format_solution_pair


class ResponseEngine:
    """
    Response Layer (ฉบับเสร็จสมบูรณ์ระดับโปรดักชัน): 
    - จัดสรุปข้อความทางคณิตศาสตร์ด้วยสัญลักษณ์ที่เที่ยงตรงทางพีชคณิต (= และ ≈)
    - คัดกรองและเรียบเรียงเนื้อหาจากไฟล์คลังความรู้โลคัล (data/knowledge) ให้อ่านง่ายเป็นภาษาพูด
    """
    
    def __init__(self):
        self.templates = {
            "success": [
                "เรียบร้อยครับ! ผลลัพธ์คือ: {result}",
                "จัดการให้แล้วครับ ได้คำตอบเป็น {result}",
                "นี่คือข้อมูลที่หามาได้ครับ: {result}",
                "✅ ทำเสร็จแล้ว: {result}"
            ],
            "error": [
                "ขออภัยครับ เกิดข้อผิดพลาด: {message}",
                "ไปต่อไม่ได้ครับ ติดปัญหาที่ {message}",
                "❌ เกิดข้อผิดพลาด: {message}",
                "ขอโทษครับ ระบบเจอปัญหา: {message}"
            ],
            "fail": [
                "คำนวณไม่สำเร็จครับ: {message}",
                "สมการนี้มีปัญหา: {message}",
                "⚠️ ตรวจสอบนิพจน์อีกครั้ง: {message}"
            ],
            "noop": [
                "รับทราบครับ ผมได้บันทึกความคืบหน้าตรงนี้ลงในฐานระบบเรียบร้อยแล้ว: {result}",
                "จัดเก็บข้อมูลลงเซสชันเรียบร้อยแล้วครับ ต้องการให้ตรวจสอบหรือต่อยอดในประเด็นไหนเพิ่มเติมแจ้งได้เลยนะ",
                "📝 บันทึกข้อมูลเข้าคลังเรียบร้อยแล้ว พร้อมสำหรับดำเนินการขั้นตอนถัดไปครับ"
            ],
            "chat:greet": [
                "สวัสดีครับ! มีอะไรให้ผมช่วยวันนี้บอกได้เลยนะครับ 🙏",
                "หวัดดีครับ! พร้อมช่วยเหลือเสมอ 😊",
                "สวัสดี! วันนี้ต้องการให้ช่วยเรื่องอะไรดีครับ?",
                "ไงครับ! ผมพร้อมฟังเสมอ 💬"
            ],
            "chat:farewell": [
                "ไว้คุยกันใหม่นะครับ! บ๊ายบาย 🙏",
                "ขอให้วันนี้เป็นวันที่ดีนะครับ! 😊",
                "พักผ่อนให้เพียงพอนะครับ ไว้เจอกันใหม่! 💤",
                "บ๊ายบายครับ! มีอะไรเรียกใช้ได้เลยนะครับ ✨"
            ],
            "chat:gratitude": [
                "ยินดีครับ! มีอะไรอีกบอกได้เลยนะ 😊",
                "ไม่มีอะไรครับ ผมยินดีช่วยเหลือเสมอ 🙏",
                "😊 ยินดีมากๆ ครับ มีอะไรอีกไหมครับ?",
                "ขอบคุณที่ไว้ใจนะครับ! 💙"
            ],
            "chat:apology": [
                "ไม่เป็นไรครับ ผมเข้าใจ 😊",
                "ไม่ต้องขอโทษนะครับ เกิดขึ้นได้เสมอ 💙",
                "โอเคครับ ไม่มีปัญหาอะไร 🙏",
                "สบายมากครับ เราไปต่อกันเลย! ✨"
            ],
            "chat:chitchat": [
                "อ๋อ เข้าใจครับ แล้วมีอะไรให้ผมช่วยเพิ่มเติมไหมครับ?",
                "น่าสนใจครับ! เล่าให้ผมฟังต่อได้เลยนะ 😊",
                "อืม... แล้วคุณล่ะครับ คิดยังไงกับเรื่องนี้?",
                "ฮะๆ ผมเห็นด้วยครับ! แล้วมีเรื่องอื่นอยากคุยไหมครับ?"
            ],
            "chat:emotion": [
                "ผมเข้าใจความรู้สึกนั้นเลยครับ 💙 ถ้าอยากเล่าหรือต้องการคำแนะนำอะไร บอกผมได้นะครับ",
                "เป็นแบบนี้ใครๆ ก็รู้สึกได้ครับ ผมอยู่ตรงนี้เสมอถ้าต้องการคนฟัง 🤝",
                "ขอส่งกำลังใจให้นะครับ 💪 มีอะไรให้ผมช่วยบอกได้เลย",
                "ผมรับฟังนะครับ ถ้าอยากคุยต่อผมพร้อมเสมอครับ 🫂"
            ],
            "chat:joke": [
                "😄 {result}",
                "🤣 {result}",
                "ฮะๆ {result}",
                "มุกนี้เด็ด! {result}"
            ],
            "qa:answer": [
                "จากข้อมูลที่มี: {result}",
                "คำตอบคือ: {result}",
                "📚 ตามที่ค้นหาได้: {result}",
                "สรุปให้ครับ: {result}"
            ],
            "qa:not_found": [
                "ขออภัยครับ ฉันยังไม่มีข้อมูลเกี่ยวกับ '{topic}' ในฐานความรู้",
                "หัวข้อนี้ยังไม่มีในคลังความรู้ของผมครับ ลองถามในรูปแบบอื่นดูไหมครับ?",
                "🤔 ผมยังเรียนรู้เรื่องนี้ไม่ครบถ้วนครับ มีแหล่งข้อมูลแนะนำไหมครับ?",
                "ขอโทษครับ เรื่องนี้ผมยังตอบไม่ได้แน่ชัด ลองถามเรื่องอื่นดูนะครับ"
            ],
            "clarify": [
                "ขอโทษครับ ผมยังไม่แน่ใจว่าคุณต้องการให้ช่วยเรื่อง '{topic}' อย่างไร ช่วยอธิบายเพิ่มเติมหน่อยได้ไหมครับ? 🤔",
                "ช่วยขยายความอีกนิดได้ไหมครับ ผมอยากช่วยคุณให้ถูกต้องที่สุด 💬",
                "เพื่อให้ผมช่วยได้ตรงจุด Rบกวนระบุรายละเอียดเพิ่มนิดนึงนะครับ 🙏"
            ]
        }
        
        self.personality = {
            "name": "Jinx",
            "tone": "friendly",
            "emoji_level": "medium",
            "language": "th",
            "max_length": 500  # ปรับความยาวเพื่อให้ครอบคลุมการอธิบายข้อมูล RAG
        }
        
        self.emojis = {
            "success": ["✅", "✨", "🎉", "💯"],
            "error": ["❌", "⚠️", "😅", "🔧"],
            "greet": ["🙏", "😊", "👋", "💬"],
            "farewell": ["🙏", "✨", "💤", "👋"],
            "emotion": ["💙", "🤝", "💪", "🫂"],
            "joke": ["😄", "🤣", "😂", "🎭"],
            "qa": ["📚", "🔍", "💡", "🎯"],
            "default": ["✨", "💬", "🤖", "🙏"]
        }

    def format(self, execution_output: Dict[str, Any], perception: Dict[str, Any] = None) -> str:
        status = execution_output.get("status", "success")
        result = execution_output.get("result", "")
        message = execution_output.get("message", "Unknown error")
        metadata = execution_output.get("metadata", {})
        
        intent = perception.get("intent", "unknown") if perception else "unknown"
        domain = perception.get("domain", "general") if perception else "general"
        topic = perception.get("topic", "") if perception else ""
        
        hint = metadata.get("response_hint", {})
        template_key = self._select_template_key(status, intent, domain, execution_output)
        
        template_list = self.templates.get(template_key, self.templates["noop"])
        chosen_template = random.choice(template_list)
        
        response = self._format_message(chosen_template, result, message, topic, hint)
        response = self._apply_personality(response, hint, status)
        
        max_len = self.personality["max_length"]
        if len(response) > max_len:
            response = response[:max_len - 3] + "..."
            
        return response

    def _select_template_key(self, status: str, intent: str, domain: str, output: Dict) -> str:
        if intent.startswith("chat:"):
            if intent in self.templates:
                return intent
            base = intent.split(":")[-1]
            if f"chat:{base}" in self.templates:
                return f"chat:{base}"
            return "chat:chitchat"
        
        if intent.startswith("qa:"):
            result = output.get("result")
            if status == "success" and result:
                if isinstance(result, str) and "ไม่พบข้อมูลที่ตรงกับคำค้นหา" in result:
                    return "qa:not_found"
                return "qa:answer"
            return "qa:not_found"
        
        if status == "awaiting_input" or "clarify" in intent:
            return "clarify"
        
        if status == "success":
            return "success"
        elif status == "fail":
            return "fail"
        elif status == "error":
            return "error"
            
        return "noop"

    def _format_message(self, template: str, result: Any, message: str, topic: str, hint: Dict) -> str:
        formatted_result = self._format_result_value(result)
        try:
            return template.format(
                result=formatted_result,
                message=message,
                topic=topic or "เรื่องนี้",
                **hint
            )
        except KeyError:
            clean_text = template.replace("{result}", str(formatted_result))
            clean_text = clean_text.replace("{message}", str(message))
            clean_text = clean_text.replace("{topic}", str(topic or "เรื่องนี้"))
            return clean_text

    def _is_terminating_decimal(self, value: float) -> bool:
        """
        ตรวจสอบว่าค่าทศนิยมนั้นเป็น 'ทศนิยมรู้จบ' ในฐานสิบ (เช่น 2.4, 9.6) หรือไม่
        """
        try:
            from fractions import Fraction
            frac = Fraction(value).limit_denominator(100000)
            denom = frac.denominator
            while denom % 2 == 0:
                denom //= 2
            while denom % 5 == 0:
                denom //= 5
            return denom == 1
        except Exception:
            return False

    def _format_result_value(self, value: Any) -> str:
        if value is None:
            return "ไม่มีข้อมูล"
        if isinstance(value, bool):
            return "ใช่" if value else "ไม่ใช่"
            
        # การจัดรูปแบบกรณีเป็นตัวเลขจำนวนเดียว (Float / Int)
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                if value.is_integer() or abs(value - round(value)) < 1e-9:
                    return f"{int(round(value)):,}"
                if self._is_terminating_decimal(value):
                    return f"{value:,.6f}".rstrip('0').rstrip('.')
                if abs(value) < 1e10:
                    return f"{value:,.6f}".rstrip('0').rstrip('.')
            return f"{value:,}"
            
        if isinstance(value, list):
            if not value:
                return "ไม่พบคำตอบจากสมการ"

            # ตรวจแยกกลุ่มโครงสร้างอาเรย์ผลลัพธ์ของคลังความรู้ (data/knowledge)
            if all(isinstance(v, dict) for v in value) and any(
                "snippet" in v for v in value
            ):
                return self._format_knowledge_hits(value)

            # ผลลัพธ์สมการ (dict ของตัวแปร)
            if all(isinstance(v, dict) for v in value) and all(
                "snippet" not in v for v in value
            ):
                parts = []
                for sol in value:
                    formatted_pairs = []
                    for k, item in sol.items():
                        # ตรวจสอบว่ามีข้อมูล Meta-Type ของตัวแปรจาก tools/math.py ส่งพ่วงมาด้วยหรือไม่
                        if isinstance(item, dict) and "type" in item and "value" in item:
                            val_type = item["type"]
                            num_val = item["value"]
                            
                            if val_type == "approx":
                                val_str = f"{num_val:,.4f}".rstrip('0').rstrip('.')
                                formatted_pairs.append(f"{k} ≈ {val_str}")
                            else:
                                if num_val.is_integer() or abs(num_val - round(num_val)) < 1e-9:
                                    formatted_pairs.append(f"{k} = {int(round(num_val)):,}")
                                else:
                                    val_str = f"{num_val:,.4f}".rstrip('0').rstrip('.')
                                    formatted_pairs.append(f"{k} = {val_str}")
                        else:
                            # การจัดรูปแบบกรณีเป็นข้อความสตริงที่ขึ้นต้นด้วยเครื่องหมายประมาณค่ามาอยู่แล้ว
                            val_str = str(item)
                            if val_str.startswith("≈"):
                                formatted_pairs.append(f"{k} {val_str}")
                            else:
                                formatted_pairs.append(format_solution_pair(str(k), item))
                    
                    pairs = ", ".join(formatted_pairs)
                    parts.append(f"({pairs})")
                return " หรือ ".join(parts)
            if len(value) <= 3:
                return ", ".join(str(v) for v in value)
            return f"{len(value)} รายการ"
        
        if isinstance(value, dict):
            if "result" in value:
                return self._format_result_value(value["result"])
            if "message" in value:
                return value["message"]
            return ", ".join(f"{str(k)} = {self._format_result_value(v)}" for k, v in value.items())
            
        if isinstance(value, str):
            if "ไม่พบข้อมูลที่ตรงกับคำค้นหา" in value:
                return value
            clean = re.sub(r'<[^>]+>', '', value)
            return clean.strip()[:250]
            
        return str(value)

    def _format_table_to_text(self, markdown_table: str) -> str:
        """
        แปลงโครงสร้างตาราง Markdown ดิบให้เป็นสรุปรายการแบบจุดหัวข้อ (Bullet List) เพื่อความง่ายในการอ่าน
        """
        lines = [line.strip() for line in markdown_table.strip().split("\n") if line.strip()]
        if len(lines) < 3:
            return markdown_table
            
        # สกัดแยกหัวข้อคอลัมน์ของตาราง
        headers = [h.strip() for h in lines[0].split("|") if h.strip()]
        rows_text = []
        
        # ข้ามแถวหัวข้อและแถวเครื่องหมายคั่นวิเคราะห์ค่าพารามิเตอร์ข้อมูลด้านใน
        for line in lines[2:]:
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= len(headers):
                details = []
                for h, val in zip(headers, cells):
                    # ละทิ้งมาร์กดาวน์ตกแต่งภายในเซลล์
                    clean_val = re.sub(r'\*\*|`', '', val).strip()
                    details.append(f"{h}: {clean_val}")
                rows_text.append("   • " + ", ".join(details))
                
        return "\n" + "\n".join(rows_text)

    def _format_knowledge_hits(self, hits: List[Dict[str, Any]]) -> str:
        """
        สแกน ทำความสะอาด และจัดรูปแบบย่อหน้าข้อมูลความรู้ที่ค้นพบจากคลังเอกสาร
        """
        if not hits:
            return "ไม่พบข้อมูลอ้างอิงที่เหมาะสมในฐานข้อมูลความรู้ระบบ"

        valid_snippets = []
        for hit in hits:
            snippet = str(hit.get("snippet", "")).strip()
            source_name = hit.get("title", "เอกสาร").replace(".md", "").replace(".txt", "")
            
            # 1. ป้องกันดักจับกรณีเนื้อหาเป็นเครื่องมือตั้งค่าโครงสร้างระบบ (JSON Schema)
            if '"$schema"' in snippet or "JSON Schema" in snippet or "intent_mappings" in snippet:
                continue
                
            # 2. ป้องกันย่อหน้านำมาตอบมีเฉพาะคำซ้ำกับหัวข้อเอกสารที่ดึงขึ้นมา
            if snippet.lower() == f"## {source_name.lower()}":
                continue
            if len(snippet) <= len(source_name) + 4 and snippet.replace("#", "").strip() == source_name:
                continue

            # 3. จัดการกรณีเนื้อหาที่พบจัดฟอร์แมตเป็นโครงสร้างตารางข้อมูล
            if "|" in snippet and "---" in snippet:
                parsed_table = self._format_table_to_text(snippet)
                valid_snippets.append(f"• รายละเอียดจากเอกสาร '{source_name}': {parsed_table}")
                continue

            # 4. เคลียร์อักขระและแท็กมาร์กดาวน์เพื่อให้ออกเสียงประโยคแชตได้อย่างเรียบเนียน
            snippet = re.sub(r'#+\s+', '', snippet)  # ลบเครื่องหมายหัวข้อ (#)
            snippet = re.sub(r'\[\[(.*?)\]\]', r'\1', snippet)  # แปลงลิงก์วิกิ [[Link]] เป็นคำอ่านธรรมดา
            snippet = re.sub(r'```.*?```', '', snippet, flags=re.DOTALL)  # นำบล็อกตัวอย่างโค้ดระบบออก
            snippet = re.sub(r'\s+', ' ', snippet).strip()  # เคลียร์ช่องสเปซช่องไฟเกิน
            
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
                
            if snippet:
                valid_snippets.append(f"• จากหัวข้อ '{source_name}': {snippet}")

        # ฟังก์ชันสำรองฉุกเฉิน (Fallback) หากกลุ่มเนื้อหาหลักโดนสกัดล้างไปจนหมด
        if not valid_snippets and hits:
            fallback_hit = hits[0]
            fallback_snippet = fallback_hit.get("snippet", "")
            source_name = fallback_hit.get("title", "เอกสาร").replace(".md", "").replace(".txt", "")
            
            fallback_clean = re.sub(r'```.*?```', '', fallback_snippet, flags=re.DOTALL)
            fallback_clean = re.sub(r'\s+', ' ', fallback_clean).strip()[:180] + "..."
            return f"จากแหล่งข้อมูล '{source_name}' ระบุรายละเอียดไว้ว่า: {fallback_clean}"

        return "\n".join(valid_snippets)

    def _apply_personality(self, text: str, hint: Dict, status: str) -> str:
        emoji_level = hint.get("emoji", self.personality["emoji_level"])
        if emoji_level != "none":
            emoji = self._get_emoji(status, hint)
            if emoji and emoji_level in ["medium", "high"]:
                if hint.get("style") == "warm":
                    text = f"{emoji} {text}"
                else:
                    text = f"{text} {emoji}"
        
        if hint.get("ask_back") and not text.endswith("?"):
            questions = ["แล้วคุณล่ะครับ?", "มีอะไรให้ผมช่วยอีกไหมครับ?", "อยากคุยต่อเรื่องอะไรดีครับ?"]
            text = f"{text} {random.choice(questions)}"
            
        if hint.get("include_future") and "ไว้" not in text:
            text = f"{text} ไว้เจอกันใหม่นะครับ!"
            
        return text

    def _get_emoji(self, status: str, hint: Dict) -> Optional[str]:
        if hint.get("emoji") is True:
            style = hint.get("style", "default")
            if style in self.emojis:
                return random.choice(self.emojis[style])
                
        emoji_map = {
            "success": "success",
            "error": "error", 
            "fail": "error",
            "chat:greet": "greet",
            "chat:farewell": "farewell",
            "chat:emotion": "emotion",
            "chat:joke": "joke",
            "qa:answer": "qa"
        }
        
        key = emoji_map.get(status) or emoji_map.get(hint.get("style"), "default")
        if key in self.emojis:
            return random.choice(self.emojis[key])
        return None

    def set_personality(self, **kwargs):
        valid_keys = {"name", "tone", "emoji_level", "language", "max_length"}
        for k, v in kwargs.items():
            if k in valid_keys:
                self.personality[k] = v