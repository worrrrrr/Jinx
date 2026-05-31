# engines/response.py

import random
import re
from typing import Dict, Any, List, Optional


class ResponseEngine:
    """
    Response Layer (ฉบับอัปเกรด): ปรุงแต่งข้อความรายงานผลลัพธ์และปรับบุคลิกภาพตามสัญญาณแผนงาน
    """
    
    def __init__(self):
        # ลบช่องว่างท้ายประโยคทั้งหมดใน Templates ป้องกันปัญหาการจัดรูปวรรคตอนผิดพลาด
        self.templates = {
            # --- กลุ่มการคำนวณและดำเนินการสำเร็จ ---
            "success": [
                "เรียบร้อยครับ! ผลลัพธ์คือ: {result}",
                "จัดการให้แล้วครับ ได้คำตอบเป็น {result}",
                "นี่คือข้อมูลที่หามาได้ครับ: {result}",
                "✅ ทำเสร็จแล้ว: {result}"
            ],
            
            # --- กลุ่มความผิดพลาดจากการรันคำสั่งย่อย ---
            "error": [
                "ขออภัยครับ เกิดข้อผิดพลาด: {message}",
                "ไปต่อไม่ได้ครับ ติดปัญหาที่ {message}",
                "❌ เกิดข้อผิดพลาด: {message}",
                "ขอโทษครับ ระบบเจอปัญหา: {message}"
            ],
            
            # --- กลุ่มความผิดพลาดทางคณิตศาสตร์เฉพาะทาง ---
            "fail": [
                "คำนวณไม่สำเร็จครับ: {message}",
                "สมการนี้มีปัญหา: {message}",
                "⚠️ ตรวจสอบนิพจน์อีกครั้ง: {message}"
            ],
            
            # --- กลุ่มบันทึกข้อมูลทั่วไปหรือไม่มีการประมวลผลเครื่องมือ ---
            "noop": [
                "รับทราบครับ ผมบันทึกข้อมูลไว้แล้ว: {result}",
                "อ่านแล้วครับ มีอะไรให้ช่วยอีกไหม?",
                "📝 บันทึกเรียบร้อยแล้ว"
            ],
            
            # --- กลุ่มคำกล่าวทักทาย ---
            "chat:greet": [
                "สวัสดีครับ! มีอะไรให้ผมช่วยวันนี้บอกได้เลยนะครับ 🙏",
                "หวัดดีครับ! พร้อมช่วยเหลือเสมอ 😊",
                "สวัสดี! วันนี้ต้องการให้ช่วยเรื่องอะไรดีครับ?",
                "ไงครับ! ผมพร้อมฟังเสมอ 💬"
            ],
            
            # --- กลุ่มคำกล่าวลา ---
            "chat:farewell": [
                "ไว้คุยกันใหม่นะครับ! บ๊ายบาย 🙏",
                "ขอให้วันนี้เป็นวันที่ดีนะครับ! 😊",
                "พักผ่อนให้เพียงพอนะครับ ไว้เจอกันใหม่! 💤",
                "บ๊ายบายครับ! มีอะไรเรียกใช้ได้เลยนะครับ ✨"
            ],
            
            # --- กลุ่มขอบคุณตอบรับ ---
            "chat:gratitude": [
                "ยินดีครับ! มีอะไรอีกบอกได้เลยนะ 😊",
                "ไม่มีอะไรครับ ผมยินดีช่วยเหลือเสมอ 🙏",
                "😊 ยินดีมากๆ ครับ มีอะไรอีกไหมครับ?",
                "ขอบคุณที่ไว้ใจนะครับ! 💙"
            ],
            
            # --- กลุ่มตอบรับคำขอโทษ ---
            "chat:apology": [
                "ไม่เป็นไรครับ ผมเข้าใจ 😊",
                "ไม่ต้องขอโทษนะครับ เกิดขึ้นได้เสมอ 💙",
                "โอเคครับ ไม่มีปัญหาอะไร 🙏",
                "สบายมากครับ เราไปต่อกันเลย! ✨"
            ],
            
            # --- กลุ่มสนทนาทั่วไป (Chitchat) ---
            "chat:chitchat": [
                "อ๋อ เข้าใจครับ แล้วมีอะไรให้ผมช่วยเพิ่มเติมไหมครับ?",
                "น่าสนใจครับ! เล่าให้ผมฟังต่อได้เลยนะ 😊",
                "อืม... แล้วคุณล่ะครับ คิดยังไงกับเรื่องนี้?",
                "ฮะๆ ผมเห็นด้วยครับ! แล้วมีเรื่องอื่นอยากคุยไหมครับ?"
            ],
            
            # --- กลุ่มประโยคปลอบโยนและแสดงความเข้าอกเข้าใจ (Empathy) ---
            "chat:emotion": [
                "ผมเข้าใจความรู้สึกนั้นเลยครับ 💙 ถ้าอยากเล่าหรือต้องการคำแนะนำอะไร บอกผมได้นะครับ",
                "เป็นแบบนี้ใครๆ ก็รู้สึกได้ครับ ผมอยู่ตรงนี้เสมอถ้าต้องการคนฟัง 🤝",
                "ขอส่งกำลังใจให้นะครับ 💪 มีอะไรให้ผมช่วยบอกได้เลย",
                "ผมรับฟังนะครับ ถ้าอยากคุยต่อผมพร้อมเสมอครับ 🫂"
            ],
            
            # --- กลุ่มการเล่าเรื่องตลก ---
            "chat:joke": [
                "😄 {result}",
                "🤣 {result}",
                "ฮะๆ {result}",
                "มุกนี้เด็ด! {result}"
            ],
            
            # --- กลุ่มการตอบคำถามคลังความรู้สำเร็จ ---
            "qa:answer": [
                "จากข้อมูลที่มี: {result}",
                "คำตอบคือ: {result}",
                "📚 ตามที่ค้นหาได้: {result}",
                "สรุปให้ครับ: {result}"
            ],
            
            # --- กลุ่มการไม่พบเนื้อหาในคลังความรู้ ---
            "qa:not_found": [
                "ขออภัยครับ ฉันยังไม่มีข้อมูลเกี่ยวกับ '{topic}' ในฐานความรู้",
                "หัวข้อนี้ยังไม่มีในคลังความรู้ของผมครับ ลองถามในรูปแบบอื่นดูไหมครับ?",
                "🤔 ผมยังเรียนรู้เรื่องนี้ไม่ครบถ้วนครับ มีแหล่งข้อมูลแนะนำไหมครับ?",
                "ขอโทษครับ เรื่องนี้ผมยังตอบไม่ได้แน่ชัด ลองถามเรื่องอื่นดูนะครับ"
            ],
            
            # --- กลุ่มคำขอกรอบบริบทเพิ่มเติม ---
            "clarify": [
                "ขอโทษครับ ผมยังไม่แน่ใจว่าคุณต้องการให้ช่วยเรื่อง '{topic}' อย่างไร ช่วยอธิบายเพิ่มเติมหน่อยได้ไหมครับ? 🤔",
                "ช่วยขยายความอีกนิดได้ไหมครับ ผมอยากช่วยคุณให้ถูกต้องที่สุด 💬",
                "เพื่อให้ผมช่วยได้ตรงจุด รบกวนระบุรายละเอียดเพิ่มนิดนึงนะครับ 🙏"
            ]
        }
        
        # ตั้งค่าคุณลักษณะบุคลิกเริ่มต้นของระบบ
        self.personality = {
            "name": "Jinx",
            "tone": "friendly",
            "emoji_level": "medium",
            "language": "th",
            "max_length": 200
        }
        
        # คลังเครื่องหมายสัญญลักษณ์อีโมจิแยกตามกลุ่มความตั้งใจ
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
        """
        ทางเข้าหลัก: นำผลลัพธ์การรันเครื่องมือมาประยุกต์จัดแต่งประโยคพร้อมสวมทับบุคลิก
        """
        status = execution_output.get("status", "success")
        result = execution_output.get("result", "")
        message = execution_output.get("message", "Unknown error")
        metadata = execution_output.get("metadata", {})
        
        # สกัดบริบทความตั้งใจ โดเมน และหัวข้อจาก Perception
        intent = perception.get("intent", "unknown") if perception else "unknown"
        domain = perception.get("domain", "general") if perception else "general"
        topic = perception.get("topic", "") if perception else ""
        
        # ดึงสัญญาณชี้นำการปรุงแต่ง (Response Hint)
        hint = metadata.get("response_hint", {})
        
        # ตัดสินใจเลือกคีย์แม่แบบคำตอบ
        template_key = self._select_template_key(status, intent, domain, execution_output)
        
        template_list = self.templates.get(template_key, self.templates["noop"])
        chosen_template = random.choice(template_list)
        
        # ทำการสลักข้อมูลตัวแปรลงในแม่แบบอย่างปลอดภัย
        response = self._format_message(chosen_template, result, message, topic, hint)
        
        # สวมทับบุคลิกและประทับสัญลักษณ์อีโมจิ
        response = self._apply_personality(response, hint, status)
        
        # ควบคุมขีดจำกัดความยาวของอักษรส่งกลับ
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
        
        # จัดการแทนค่าตัวแปรด้วยวิธีทนทานต่อ KeyError
        try:
            return template.format(
                result=formatted_result,
                message=message,
                topic=topic or "เรื่องนี้",
                **hint
            )
        except KeyError:
            # Fallback ทำความสะอาดสายอักขระทดแทนกรณีตัวแปรไม่สมบูรณ์
            clean_text = template.replace("{result}", str(formatted_result))
            clean_text = clean_text.replace("{message}", str(message))
            clean_text = clean_text.replace("{topic}", str(topic or "เรื่องนี้"))
            return clean_text

    def _format_result_value(self, value: Any) -> str:
        """
        จัดแต่งและรายงานผลลัพธ์ของข้อมูล โดยถอดค่าและฟอร์แมตตัวแปรอย่างถูกต้องไร้รอยต่อ
        """
        if value is None:
            return "ไม่มีข้อมูล"
        if isinstance(value, bool):
            return "ใช่" if value else "ไม่ใช่"
        if isinstance(value, (int, float)):
            if isinstance(value, float) and abs(value) < 1e10:
                return f"{value:,.6f}".rstrip('0').rstrip('.')
            return f"{value:,}"
        if isinstance(value, list):
            if len(value) <= 3:
                return ", ".join(str(v) for v in value)
            return f"{len(value)} รายการ"
        
        # ปรับปรุงโครงสร้าง: ดึงคีย์ตัวแปรและค่ามาแสดงเป็นสมการแยกอ่านง่าย ป้องกันบั๊ก "fields"
        if isinstance(value, dict):
            if "result" in value:
                return self._format_result_value(value["result"])
            if "message" in value:
                return value["message"]
            return ", ".join(f"{k} = {self._format_result_value(v)}" for k, v in value.items())
            
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
        
        # แทรกคำถามต่อท้ายสนทนาเพื่อกระตุ้นปฏิสัมพันธ์ตามที่ระบุในสัญญานนำทาง
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