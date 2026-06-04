"""
Module: engines/response.py — Jinx Response Engine (Final Ultimate Edition)
=============================================================================
หลักการ: "ดู Intent + วัดความสุภาพ → ตอบให้ตรง + รักษาน้ำเสียง"
- Math: สั้น/ถาม/สุภาพ → ตอบตามระดับ
- Chat: Greet/Farewell/Emotion → ตอบตามระดับความสุภาพ
- Q&A: ตอบตรง
- Person Analyzer: จัดรูปแบบ
- Fallback: ถามกลับเมื่อไม่แน่ใจ
"""

import random
from typing import Dict, Any


class ResponseEngine:

    def __init__(self):
        # ── Greeting — แยกตามระดับความสุภาพ ──
        self.greet = {
            0: ["ว่าไง! 😄", "ไง! 🔥", "โย่ว! 🚀"],
            1: ["สวัสดีครับ! มีอะไรให้ช่วย? 🙏", "สวัสดีครับ! 😊", "หวัดดีครับ! 💬"],
            2: ["สวัสดีครับ! มีอะไรให้ผมช่วยวันนี้? 🙏", "สวัสดีครับ! พร้อมช่วยเหลือเสมอ 😊"],
        }
        # ── Farewell ──
        self.farewell = {
            0: ["บาย! 👋", "ไว้เจอกัน! 😎"],
            1: ["ไว้คุยกันใหม่นะครับ! 🙏", "บายครับ! 😊"],
            2: ["ไว้คุยกันใหม่นะครับ! ขอบคุณที่คุยด้วย 🙏", "บายครับ! ไว้เจอกันใหม่นะครับ 😊"],
        }
        # ── Gratitude ──
        self.gratitude = {
            0: ["ยินดี! 😊", "เต็มที่! 💪"],
            1: ["ยินดีครับ! 😊", "ด้วยความเต็มใจครับ! 💙"],
            2: ["ยินดีครับ! มีอะไรอีกบอกได้เลยนะ 🙏", "ขอบคุณที่ไว้ใจครับ! 💙"],
        }
        # ── Apology ──
        self.apology = {
            0: ["ไม่เป็นไร! 🤝", "ช่างมัน! 😊"],
            1: ["ไม่เป็นไรครับ! 💙", "ไม่ต้องคิดมากครับ 🤝"],
            2: ["ไม่เป็นไรเลยครับ ผมเข้าใจ 💙", "ไม่ต้องขอโทษนะครับ 🤝"],
        }
        # ── Chitchat ──
        self.chitchat = {
            0: ["อ๋อ! ว่าไงต่อ? 😄", "เข้าใจ! มีไรอีก? 💬"],
            1: ["อ๋อ เข้าใจครับ มีอะไรให้ช่วยไหม? 💬", "น่าสนใจครับ! มีอะไรอีก? 😊"],
            2: ["อ๋อ เข้าใจครับ มีอะไรให้ผมช่วยเพิ่มเติมไหมครับ? 💬", "น่าสนใจครับ! ถ้ามีอะไรให้ช่วยบอกได้นะ 😊"],
        }
        # ── Emotion ──
        self.emotion = {
            0: ["เข้าใจเลย... 💙", "หนักหน่วงนะ! สู้ๆ! 💪"],
            1: ["ผมเข้าใจครับ 💙", "สู้ๆ นะครับ! 💪"],
            2: ["ผมเข้าใจความรู้สึกนั้นเลยครับ 💙", "ผมอยู่ตรงนี้นะครับ ถ้าต้องการคนฟัง 🤝"],
        }
        # ── Math ──
        self.math_prefix = {
            0: "",
            1: "ได้ ",
            2: "ได้ ",
        }
        self.math_suffix = {
            0: "",
            1: "",
            2: " ครับ",
        }

    # ============================================================
    # MAIN FORMAT
    # ============================================================

    def format(self, execution_output: Dict[str, Any], perception: Dict[str, Any] = None) -> str:
        result = execution_output.get("result")
        action = execution_output.get("action", "")
        status = execution_output.get("status", "success")
        message = execution_output.get("message", "")
        user_text = perception.get("raw", "") if perception else ""
        level = self._politeness_level(user_text)

        # ── 1. ERROR ──
        if status == "error":
            return f"❌ {message}\n\nอยากให้ลองใหม่ไหมครับ? 🤔"

        # ── 2. NOOP ──
        if status == "noop":
            return "🤔 ไม่แน่ใจว่าต้องการให้ทำอะไร — ช่วยอธิบายเพิ่มเติมหน่อยได้ไหมครับ?"

        # ── 3. LLM / Astrology / Name (ยาว > 300) → คืนตรง ──
        if isinstance(result, str) and len(result) > 300:
            return result

        # ── 4. Direct Response → คืนตรง ──
        if execution_output.get("direct_response"):
            return str(result or "")

        # ── 5. Person Analyzer ──
        if isinstance(result, dict) and "mbti_ranking" in result:
            return self._fmt_person(result)

        # ── 6. MATH ──
        if action in ("compute_math", "math") or perception.get("domain") == "math" if perception else False:
            return self._fmt_math(result, level)

        # ── 7. CHAT ──
        if perception:
            intent = perception.get("intent", "")
            if intent == "chat:greet":
                return random.choice(self.greet.get(level, self.greet[1]))
            if intent == "chat:farewell":
                return random.choice(self.farewell.get(level, self.farewell[1]))
            if intent == "chat:gratitude":
                return random.choice(self.gratitude.get(level, self.gratitude[1]))
            if intent == "chat:apology":
                return random.choice(self.apology.get(level, self.apology[1]))
            if intent == "chat:emotion":
                return random.choice(self.emotion.get(level, self.emotion[1]))
            if intent.startswith("chat:"):
                return random.choice(self.chitchat.get(level, self.chitchat[1]))
            if intent.startswith("qa:"):
                if status == "success" and result:
                    return str(result)
                return f"ยังไม่มีข้อมูลเกี่ยวกับ '{perception.get('topic', '')}' ครับ 😅"

        # ── 8. SUCCESS (Fallback) ──
        if status == "success" and result is not None:
            return str(result)

        # ── 9. UNKNOWN ──
        return str(result or message or "รับทราบครับ ✨")

    # ============================================================
    # MATH FORMATTER
    # ============================================================

    def _fmt_math(self, result, level: int) -> str:
        """ตอบ Math — สั้น/ถาม/สุภาพ → prefix + result + suffix"""
        # Clean result
        if isinstance(result, list):
            parts = []
            for item in result:
                if isinstance(item, dict):
                    parts.append(", ".join(f"{k} = {v}" for k, v in item.items()))
            result_str = ", ".join(parts) if parts else str(result)
        else:
            result_str = str(result)

        prefix = self.math_prefix.get(level, "")
        suffix = self.math_suffix.get(level, "")
        return f"{prefix}{result_str}{suffix}"

    # ============================================================
    # PERSON ANALYZER FORMATTER
    # ============================================================

    def _fmt_person(self, result: dict) -> str:
        mbti = result.get("mbti_ranking", [])
        ennea = result.get("enneagram_ranking", [])

        if not mbti:
            return "🤔 วิเคราะห์ไม่ชัดนะ — ลองพิมพ์ข้อความที่ยาวขึ้นหน่อย?"

        top = mbti[0]
        lines = [
            f"🧠 ดูแล้วน่าจะเป็น **{top.get('type', '?')}** — {top.get('confidence', 0)}%"
        ]

        if len(mbti) > 1:
            second = ", ".join(
                f"{p.get('type', '?')} ({p.get('confidence', 0)}%)"
                for p in mbti[1:4]
            )
            lines.append(f"🔹 รองลงมา: {second}")

        if ennea:
            e = ennea[0]
            lines.append(
                f"🎯 Enneagram: {e.get('type', '?')} "
                f"({e.get('name', '?')}) — {e.get('confidence', 0)}%"
            )

        return "\n".join(lines)

    # ============================================================
    # POLITENESS DETECTOR
    # ============================================================

    def _politeness_level(self, text: str) -> int:
        """วัดระดับความสุภาพ 0-2"""
        high = ["ครับ", "ค่ะ", "ขอ", "รบกวน", "กรุณา", "ขอบคุณ", "นะครับ", "นะคะ"]
        medium = ["ได้เท่าไหร่", "เท่าไร", "เท่าไหร่", "ไหม", "มั้ย", "?", "หรือเปล่า", "รึยัง"]

        if any(w in text for w in high):
            return 2
        if any(w in text for w in medium):
            return 1
        return 0

    # ============================================================
    # PERSONALITY
    # ============================================================

    def set_personality(self, **kwargs):
        pass


def get_response_engine() -> ResponseEngine:
    return ResponseEngine()