# engines/response.py

import random
import re
from typing import Dict, Any, List, Optional


class ResponseEngine:
    """
    Response Layer (ฉบับสมบูรณ์สูงสุด): รองรับการแสดงผลลัพธ์พจนานุกรมเดี่ยวและพจนานุกรมชุด (หรือ) อย่างถูกต้อง
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
                "รับทราบครับ ผมบันทึกข้อมูลไว้แล้ว: {result}",
                "อ่านแล้วครับ มีอะไรให้ช่วยอีกไหม?",
                "📝 บันทึกเรียบร้อยแล้ว"
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
            "max_length": 200
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
            if status == "success" and output.get("result"):
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

    def _format_result_value(self, value: Any) -> str:
        """
        จัดแต่งรายงานผลลัพธ์ของข้อมูล โดยถอดค่าและเชื่อมโยงคำตอบหลายชุด (หรือ) ตามระบบพีชคณิตระดับสูง
        """
        if value is None:
            return "ไม่มีข้อมูล"
        if isinstance(value, bool):
            return "ใช่" if value else "ไม่ใช่"
        if isinstance(value, (int, float)):
            if isinstance(value, float) and abs(value) < 1e10:
                return f"{value:,.6f}".rstrip('0').rstrip('.')
            return f"{value:,}"
            
        # ตรวจพบกลุ่มผลลัพธ์ระบบสมการพีชคณิต (List of Dicts) ของ SymPy -> แปลงเป็นประโยคเชื่อม "หรือ"
        if isinstance(value, list):
            if len(value) > 0 and all(isinstance(v, dict) for v in value):
                return " หรือ ".join(
                    "(" + ", ".join(f"{str(k)} = {self._format_result_value(val)}" for k, val in v.items()) + ")"
                    for v in value
                )
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
            clean = re.sub(r'<[^>]+>', '', value)
            return clean.strip()[:150]
            
        return str(value)

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