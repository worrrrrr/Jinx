"""
Person Analyzer V3.0 — Hybrid MBTI + Enneagram Detection (Final Tuned)
========================================================================
Layer 1: Direct Dichotomy Detection (E/I, S/N, T/F, J/P) — Speech Signatures
Layer 2: Cognitive Function Detection (Ni, Ne, Si, Se, Ti, Te, Fi, Fe) — Intent Patterns
Cross-Reference: Boost if both layers agree, flag if disagree

Enneagram Detection: 9 Types — Core Motivation Patterns

Tuning:
- Strict Dominant Filtering: multipliers for dominant, auxiliary, inferior
- Enneagram Bias: Type 8 boosts Te/Se dominant/auxiliary types
- Inconclusive Flag: top confidence < 40% marked

Architecture:
- 70% Cognitive Intent (with multipliers)
- 30% Speech Signature
- Cross-Reference for final confidence
- Enneagram bias applied afterwards
- Inconclusive flag if needed
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class TypePrediction:
    type_code: str
    type_name: str
    confidence: float
    evidence: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    mbti_ranking: List[TypePrediction]
    enneagram_ranking: List[TypePrediction]
    cognitive_signature: Dict[str, float]
    dichotomy_scores: Dict[str, Dict[str, float]]
    summary: str


# ============================================================
# MBTI TYPE NAMES
# ============================================================

MBTI_NAMES = {
    "INTJ": "The Architect", "INTP": "The Logician", "ENTJ": "The Commander", "ENTP": "The Debater",
    "INFJ": "The Advocate", "INFP": "The Mediator", "ENFJ": "The Protagonist", "ENFP": "The Campaigner",
    "ISTJ": "The Logistician", "ISFJ": "The Defender", "ESTJ": "The Executive", "ESFJ": "The Consul",
    "ISTP": "The Virtuoso", "ISFP": "The Adventurer", "ESTP": "The Entrepreneur", "ESFP": "The Entertainer"
}

# ============================================================
# ENNEAGRAM TYPES
# ============================================================

ENNEAGRAM_TYPES = {
    1: {"name": "The Reformer", "core_fear": "กลัวผิดพลาด/ไม่มีคุณค่า", "core_desire": "ต้องการถูกต้อง"},
    2: {"name": "The Helper", "core_fear": "กลัวไม่เป็นที่รัก", "core_desire": "ต้องการเป็นที่ต้องการ"},
    3: {"name": "The Achiever", "core_fear": "กลัวล้มเหลว/ไร้ค่า", "core_desire": "ต้องการสำเร็จ"},
    4: {"name": "The Individualist", "core_fear": "กลัวไม่มีตัวตน", "core_desire": "ต้องการมีเอกลักษณ์"},
    5: {"name": "The Investigator", "core_fear": "กลัวไร้ความสามารถ", "core_desire": "ต้องการเข้าใจ"},
    6: {"name": "The Loyalist", "core_fear": "กลัวไม่ปลอดภัย", "core_desire": "ต้องการมั่นคง"},
    7: {"name": "The Enthusiast", "core_fear": "กลัวถูกจำกัด", "core_desire": "ต้องการอิสระ"},
    8: {"name": "The Challenger", "core_fear": "กลัวถูกควบคุม", "core_desire": "ต้องการเข้มแข็ง"},
    9: {"name": "The Peacemaker", "core_fear": "กลัวแตกแยก", "core_desire": "ต้องการสงบ"}
}

# ============================================================
# LAYER 1: DIRECT DICHOTOMY DETECTION (Speech Signatures)
# ============================================================

DICHOTOMY_KEYWORDS = {
    "E": [
        "เพื่อน", "สังคม", "กลุ่ม", "เรา", "ไปเที่ยว", "ปาร์ตี้", "คนอื่น", "ทุกคน",
        "ข้างนอก", "เจอคน", "เข้าสังคม", "ทีม", "เพื่อนร่วมงาน", "ไปด้วยกัน", "ชวน",
        "มาสิ", "ไปกัน", "อยู่ด้วยกัน", "คนเยอะ", "พบปะ", "สังสรรค์"
    ],
    "I": [
        "คนเดียว", "อยู่บ้าน", "เงียบ", "ฉัน", "ส่วนตัว", "โลกส่วนตัว", "อยากอยู่เงียบๆ",
        "ขอเวลาคิด", "ไม่ค่อยเจอใคร", "ปลีกตัว", "สันโดษ", "อ่านหนังสือ", "อยู่กับตัวเอง",
        "ไม่ชอบคนเยอะ", "หลบ", "อยู่ในห้อง", "พักก่อน", "เก็บตัว"
    ],
    "S": [
        "เห็น", "ได้ยิน", "สัมผัส", "ตอนนี้", "เมื่อกี้", "เมื่อวาน", "วันนี้", "ตัวเลข",
        "ข้อมูล", "ข้อเท็จจริง", "ทำ", "ลงมือ", "ของจริง", "ประสบการณ์", "เคยทำ",
        "เห็นผล", "จับต้องได้", "รายละเอียด", "ขั้นตอน", "ปฏิบัติ", "ลองแล้ว"
    ],
    "N": [
        "อนาคต", "ทฤษฎี", "จินตนาการ", "what if", "pattern", "ความหมาย", "ภาพรวม",
        "แนวโน้ม", "สัญลักษณ์", "เชื่อมโยง", "abstract", "idea", "ไอเดีย", "คิดว่า",
        "อาจจะเป็น", "น่าจะ", "ความเป็นไปได้", "imagine", "ฝัน", "วิสัยทัศน์"
    ],
    "T": [
        "เพราะ", "ดังนั้น", "ข้อมูล", "เหตุผล", "ถูกต้อง", "วิเคราะห์", "ตรรกะ",
        "ไม่สมเหตุสมผล", "ข้อเท็จจริง", "พิสูจน์", "หลักการ", "ระบบ", "ตรวจสอบ",
        "แยกแยะ", "นิยาม", "ทำให้ถูก", "ผิด", "แก้ไข", "ตามหลัก", "ตามข้อมูล"
    ],
    "F": [
        "รู้สึก", "แคร์", "เข้าใจ", "เห็นใจ", "ความสัมพันธ์", "คนอื่น", "เกรงใจ",
        "เสียใจ", "ดีใจ", "ห่วง", "ช่วย", "ดูแล", "ทุกข์", "สุข", "อารมณ์",
        "น้ำใจ", "สงสาร", "ใส่ใจ", "ความรัก", "เป็นห่วง"
    ],
    "J": [
        "ต้อง", "ควร", "วางแผน", "ตาราง", "ขั้นตอน", "เสร็จ", "ตัดสินใจ", "เด็ดขาด",
        "กำหนด", "deadline", "เรียบร้อย", "จัดการ", "สรุป", "จบ", "แน่นอน",
        "ตามแผน", "ตามกฎ", "ต้องทำให้ได้", "ห้ามพลาด", "ต้องเป๊ะ"
    ],
    "P": [
        "อาจจะ", "เดี๋ยว", "ช่างเถอะ", "ตามสถานการณ์", "ยังไม่ตัดสินใจ", "เปิดกว้าง",
        "ยืดหยุ่น", "แล้วแต่", "ค่อยว่ากัน", "ยังไม่แน่", "เดี๋ยวดูอีกที", "ตามอารมณ์",
        "ปล่อย", "ไม่ต้องรีบ", "แล้วแต่สะดวก", "ตามน้ำ", "ตามใจ", "อะไรก็ได้"
    ]
}


# ============================================================
# LAYER 2: COGNITIVE FUNCTION INTENT PATTERNS
# ============================================================

COGNITIVE_INTENT_PATTERNS = {
    "Ni": [
        r"(ทั้งหมด|ทุกอย่าง|หลายๆอย่าง).{0,20}(สรุป|นำไปสู่|ชี้ไปที่|หมายความว่า)",
        r"(สับสน|ไม่แน่ใจ|ไม่รู้).{0,10}(ว่า)?(ตัวเอง|ตน).{0,10}(เป็น|คือ|ใช่)",
        r"(คิดว่า|เชื่อว่า|มั่นใจว่า).{0,10}(ฉัน|ผม|กู|ตัวเอง).{0,10}(เป็น|คือ)",
        r"(เห็น)?(pattern|แนวโน้ม|รูปแบบ|ภาพรวม).{0,10}(ชัด|ซ้ำ|เดิม)",
        r"(มัน)?(กำลังจะ|จะต้อง|ในที่สุด).{0,10}(เป็น|เกิด|เปลี่ยน|ลงเอย)",
    ],
    "Ne": [
        r"(แล้ว)?(ถ้า|สมมติ|เกิด|what if).{0,10}(ลอง|เปลี่ยน|ทำ|เป็น)",
        r"(เชื่อม|link|ต่อยอด|relate).{0,10}(กับ|ไป|ได้).{0,10}(อีก|หลาย|น่าสนใจ)",
        r"((?:แล้วก็|หรือว่า|ไม่ก็|อีกอย่าง|อีกมุม).{0,30}){2,}",
        r"(มี)?(ทาง|วิธี|ความเป็นไปได้).{0,5}(อื่น|อีก|ใหม่).{0,5}(ไหม|บ้าง)",
    ],
    "Se": [
        r"(อย่า)?(เพิ่ง)?(คิด|วิเคราะห์).{0,10}(ลงมือ|ทำ|ลอง|เริ่ม).{0,5}(ก่อน|เลย|ตอนนี้)",
        r"(เมื่อกี้|ตอนนี้|ตรงนี้|ตรงหน้า).{0,5}(เกิด|เห็น|ได้ยิน|ทำ).{0,5}(อะไร|ยังไง)",
        r"(เปลี่ยน|ย้าย|สลับ).{0,5}(กลุ่ม|เพื่อน|ที่|งาน).{0,5}(บ่อย|ตลอด|ประจำ)",
        r"(ไม่)?(ลอง|ทำ|เห็น|เจอ).{0,5}(ไม่)?(รู้|เชื่อ|เข้าใจ)",
    ],
    "Si": [
        r"(เมื่อก่อน|แต่ก่อน|ครั้งที่แล้ว|อดีต|จำได้ว่า).{0,10}(เคย)?(ทำ|เป็น|เกิด).{0,10}(แบบนี้|แล้วดี|แล้วเวิร์ค)",
        r"(ทำ)?(ตาม)?(ที่)?(เคย|เดิม|สืบทอด|ประเพณี|ประจำ|ปกติ)",
        r"(ของ)?(เก่า|เดิม|classic|ดั้งเดิม).{0,10}(ดี|เวิร์ค|ใช้ได้|ทน|กว่า)",
    ],
    "Ti": [
        r"(ไม่)?(สมเหตุสมผล|make sense|ลงตัว|สอดคล้อง|มีเหตุผล).{0,10}(กับ|ใน|เลย)",
        r"(นิยาม|define|หมายถึง|คือ).{0,5}(อะไร|ว่าอะไร|ยังไง).{0,5}(กันแน่|จริงๆ|เป๊ะๆ)",
        r"(ขัด|ย้อน|แย้ง).{0,5}(กัน|ตัวเอง|ในตัว|กันเอง)",
        r"(แยก|จัด|แบ่ง|classify).{0,5}(ให้)?(ชัด|ถูก|เป็นระบบ|เป็นหมวด)",
        r"(ใช้ชีวิต|อยู่กับ|สังคม).{0,5}(ยาก|ลำบาก|ไม่ได้|ไม่รอด)",
    ],
    "Te": [
        r"(ref|reference|อ้างอิง|แหล่งที่มา|source).{0,5}(: |จาก|ตาม|บอกว่า)",
        r"(ขั้นตอนที่|ข้อที่|ลำดับที่)\s*\d",
        r"(ข้อมูล|ตัวเลข|สถิติ|รายงาน|research|ข้อสอบ).{0,10}(บอก|แสดง|ชี้|ระบุ|ว่า)",
        r"(deadline|กำหนด|แผน|ตาราง).{0,5}(คือ|เมื่อไหร่|อะไร|ยังไง)",
        r"(ต้อง)?(จัดการ|ทำให้เสร็จ|execute|ดำเนินการ).{0,10}(เดี๋ยวนี้|ทันที|เร็ว)",
    ],
    "Fi": [
        r"(ถึง)?(ใคร|ทุกคน|คนอื่น|สังคม).{0,15}(จะว่า|จะมอง|จะคิด).{0,10}(แต่)?(ฉัน|ผม|กู).{0,10}(ไม่|ยัง|ก็|ขอ)",
        r"(สำหรับฉัน|ในมุมฉัน|ส่วนตัว|ฉันว่า).{0,10}(มัน)?(ไม่)?(ดี|แฟร์|ถูก|ใช่|โอเค)",
        r"(มัน)?(ไม่)?(ใช่|ตัว|แนว|ทาง).{0,5}(ฉัน|ตัวเอง|ของฉัน|กู)",
        r"(ขัดกับ|ตรงกับ).{0,5}(ตัวตน|หลักการ|หัวใจ|ค่านิยม|สิ่งที่ฉันเป็น)",
    ],
    "Fe": [
        r"(ทุกคน|ใคร|ใครสักคน).{0,10}(โอเค|รู้สึก|คิด|เป็นไง).{0,5}(ไหม|ยังไง|บ้าง|\?)",
        r"(บรรยากาศ|vibe|mood|อารมณ์|ความรู้สึก|ไวบ์).{0,10}(เปลี่ยน|แปลก|ตึง|ดี|แย่)",
        r"(เกรงใจ|เสียมารยาท|ไม่เหมาะสม|ไม่ดี|น่าเกลียด).{0,10}(จัง|เลย|มาก|ถ้า|ที่)",
        r"(อย่า)?(ทะเลาะ|เถียง|ขัดแย้ง).{0,5}(กัน|เลย|อีก|ไป|นะ)",
        r"(ฝาก|ช่วย|รบกวน).{0,5}(ดู|ตรวจ|วิเคราะห์|แนะนำ).{0,5}(หน่อย|ที|ให้|ด้วย)",
        r"(ทน|อดทน|อดกลั้น).{0,10}(มาก|กว่า|ไว้|ต่อไป|มาตลอด)",
    ]
}


# ============================================================
# ENNEAGRAM INTENT PATTERNS
# ============================================================

ENNEAGRAM_PATTERNS = {
    1: [
        r"(มัน)?(ไม่)?(ถูกต้อง|เหมาะสม|สมควร|ดีพอ|ถูกหลัก)",
        r"(ควร|ต้อง|จำเป็น).{0,5}(แก้ไข|ปรับปรุง|ทำให้ดี|ถูกต้อง)",
        r"(มาตรฐาน|คุณภาพ|ความเป็นระเบียบ|เป๊ะ)",
    ],
    2: [
        r"(ไม่เป็นไร)?(เดี๋ยว)?(ฉัน|ผม|เดี๋ยว).{0,5}(ช่วย|ดูแล|จัดการ|ทำให้)",
        r"(คุณ|เธอ|นาย).{0,5}(ต้องการ|อยากได้).{0,5}(อะไร|ไหม|หรือเปล่า)",
        r"(ฉัน|ผม).{0,5}(อยู่)?(ตรงนี้|ข้างๆ|ด้วย).{0,5}(นะ|เสมอ|ตลอด)",
    ],
    3: [
        r"(ต้อง)?(สำเร็จ|ชนะ|เก่ง|ดีเด่น|ดีที่สุด|อันดับหนึ่ง)",
        r"(ผลงาน|achievement|success|ความสำเร็จ).{0,5}(ของ)?(ฉัน|ผม|เรา)",
        r"(เขา|คนอื่น|สังคม).{0,5}(มอง|เห็น|คิด).{0,5}(ว่า)?(เรา|ฉัน).{0,5}(เป็น|ยังไง)",
    ],
    4: [
        r"(ไม่มีใคร)?(เข้าใจ|เห็น|รู้สึก).{0,5}(ฉัน|ตัวฉัน|ความรู้สึกฉัน)",
        r"(ฉัน)?(ไม่)?(เหมือน|ซ้ำ|ธรรมดา).{0,5}(ใคร|คนอื่น|ทั่วไป)",
        r"(ต้อง)?(พิเศษ|แตกต่าง|ไม่เหมือนใคร|มีเอกลักษณ์|unique)",
        r"(สับสน)?(ว่า)?(ตัวเอง|ตน).{0,5}(เป็น|คือ).{0,5}(อะไร|ใคร|แบบไหน)",
    ],
    5: [
        r"(ขอ)?(เวลา|ข้อมูล|หลักฐาน).{0,5}(ก่อน|เพิ่ม|อีก|ศึกษา|วิเคราะห์)",
        r"(ต้อง)?(เข้าใจ|รู้|วิเคราะห์|ศึกษา).{0,5}(ก่อน|ให้ได้|ให้หมด|ให้ชัด)",
        r"(ข้อมูล|ความรู้|ความเข้าใจ).{0,5}(ไม่พอ|ยังขาด|ต้องเพิ่ม)",
        r"(ทำไม|เพราะอะไร|ยังไง).{0,5}(ต้องรู้|อยากรู้|สงสัย)",
    ],
    6: [
        r"(แน่ใจ)?(ไหม|หรือ|รึเปล่า|แล้วเหรอ)",
        r"(มี)?(แผนสำรอง|แผนสอง|backup|ทางหนี).{0,5}(ไหม|หรือเปล่า)",
        r"(เกิด)?(อะไร)?(ขึ้น)?(ถ้า|หาก).{0,5}(ผิดพลาด|ล้มเหลว|ไม่สำเร็จ)",
        r"(กังวล|กลัว|ไม่มั่นใจ|ไม่แน่ใจ).{0,10}(เรื่อง|ว่า|กับ)",
    ],
    7: [
        r"(น่า)?(สนใจ|ตื่นเต้น|สนุก|ใหม่|เจ๋ง).{0,5}(จัง|มาก|ดี|อีก|เลย)",
        r"(เบื่อ|จำเจ|ซ้ำซาก|เดิมๆ).{0,5}(อีกแล้ว|ตลอด|จัง|มาก|แล้ว)",
        r"(มี)?(ทางเลือก|ตัวเลือก|อะไร).{0,5}(อื่น|อีก|ใหม่|เยอะ|สนุก)",
    ],
    8: [
        r"(อย่า)?(มา)?(บังคับ|ควบคุม|สั่ง|จัดการ|ยุ่ง).{0,5}(ฉัน|ชีวิต|ความคิด|กู)",
        r"(ฉัน|ผม|กู).{0,5}(จัดการเอง|ตัดสินใจเอง|ควบคุมเอง|นำเอง)",
        r"(ต้อง)?(เข้มแข็ง|แข็งแกร่ง|สู้|ไม่ยอม|ชนะ)",
        r"(ไป)?(เถียง|สู้|เคลียร์).{0,5}(กับ|เลย|ตรงนี้)",
    ],
    9: [
        r"(ช่างเถอะ|อะไรก็ได้|ตามนั้น|แล้วแต่|ตามใจ).{0,5}(คุณ|เขา|พวกเรา|เถอะ)",
        r"(อย่า)?(ทะเลาะ|ขัดแย้ง|มีปัญหา|เถียง).{0,5}(กัน|เลย|อีก|ไป)",
        r"(สงบ|เงียบ|สบาย|สบายๆ|กลมเกลียว).{0,5}(ก็พอ|ดีกว่า|แล้ว|สำคัญ)",
    ]
}


# ============================================================
# MBTI COGNITIVE STACKS (for Fallback / Cognitive Ranking)
# ============================================================

MBTI_STACKS = {
    "INTJ": {"dom": "Ni", "aux": "Te", "ter": "Fi", "inf": "Se"},
    "INTP": {"dom": "Ti", "aux": "Ne", "ter": "Si", "inf": "Fe"},
    "ENTJ": {"dom": "Te", "aux": "Ni", "ter": "Se", "inf": "Fi"},
    "ENTP": {"dom": "Ne", "aux": "Ti", "ter": "Fe", "inf": "Si"},
    "INFJ": {"dom": "Ni", "aux": "Fe", "ter": "Ti", "inf": "Se"},
    "INFP": {"dom": "Fi", "aux": "Ne", "ter": "Si", "inf": "Te"},
    "ENFJ": {"dom": "Fe", "aux": "Ni", "ter": "Se", "inf": "Ti"},
    "ENFP": {"dom": "Ne", "aux": "Fi", "ter": "Te", "inf": "Si"},
    "ISTJ": {"dom": "Si", "aux": "Te", "ter": "Fi", "inf": "Ne"},
    "ISFJ": {"dom": "Si", "aux": "Fe", "ter": "Ti", "inf": "Ne"},
    "ESTJ": {"dom": "Te", "aux": "Si", "ter": "Ne", "inf": "Fi"},
    "ESFJ": {"dom": "Fe", "aux": "Si", "ter": "Ne", "inf": "Ti"},
    "ISTP": {"dom": "Ti", "aux": "Se", "ter": "Ni", "inf": "Fe"},
    "ISFP": {"dom": "Fi", "aux": "Se", "ter": "Ni", "inf": "Te"},
    "ESTP": {"dom": "Se", "aux": "Ti", "ter": "Fe", "inf": "Ni"},
    "ESFP": {"dom": "Se", "aux": "Fi", "ter": "Te", "inf": "Ni"}
}


# ============================================================
# BIAS SET: Types with Te or Se as Dominant or Auxiliary
# ============================================================

TE_SE_TYPES = {
    "ENTJ", "ESTJ", "ESTP", "ESFP",  # Te-dom, Se-dom
    "INTJ", "ISTJ", "ISTP", "ISFP"   # Te-aux, Se-aux
}


# ============================================================
# MAIN ANALYZER CLASS
# ============================================================

class PersonAnalyzer:
    """
    Hybrid MBTI + Enneagram Analyzer V3.0 (Tuned)
    
    Layer 1: Direct Dichotomy (Speech Signatures) — 30% weight
    Layer 2: Cognitive Functions (Intent Patterns) — 70% weight
    Strict Dominant Filtering for cognitive ranking
    Enneagram Bias: Type 8 boosts Te/Se types
    Inconclusive Flag: top confidence < 40%
    """
    
    def __init__(self):
        pass
    
    # ============================================================
    # LAYER 1: DIRECT DICHOTOMY
    # ============================================================
    
    def _detect_dichotomy(self, text: str) -> Dict[str, Dict[str, float]]:
        """จับ 4 ขั้ว E/I, S/N, T/F, J/P จากคำพูด"""
        lower = text.lower()
        scores = {}
        for dim, poles in [("EI", ["E", "I"]), ("SN", ["S", "N"]), 
                           ("TF", ["T", "F"]), ("JP", ["J", "P"])]:
            dim_scores = {}
            for pole in poles:
                keywords = DICHOTOMY_KEYWORDS.get(pole, [])
                count = sum(lower.count(kw) for kw in keywords)
                dim_scores[pole] = count
            scores[dim] = dim_scores
        return scores
    
    def _dichotomy_to_mbti(self, scores: Dict[str, Dict[str, float]]) -> Tuple[str, float]:
        """แปลง 4 ขั้วเป็น MBTI 4 ตัวอักษร และ confidence"""
        mbti = ""
        total_confidence = 0.0
        
        # E vs I
        e_score = scores["EI"]["E"]
        i_score = scores["EI"]["I"]
        if e_score > i_score:
            mbti += "E"
            conf = e_score / (e_score + i_score) if (e_score + i_score) > 0 else 0.5
        elif i_score > e_score:
            mbti += "I"
            conf = i_score / (e_score + i_score) if (e_score + i_score) > 0 else 0.5
        else:
            mbti += "I"
            conf = 0.5
        total_confidence += conf
        
        # S vs N
        s_score = scores["SN"]["S"]
        n_score = scores["SN"]["N"]
        if s_score > n_score:
            mbti += "S"
            conf = s_score / (s_score + n_score) if (s_score + n_score) > 0 else 0.5
        elif n_score > s_score:
            mbti += "N"
            conf = n_score / (s_score + n_score) if (s_score + n_score) > 0 else 0.5
        else:
            mbti += "N"
            conf = 0.5
        total_confidence += conf
        
        # T vs F
        t_score = scores["TF"]["T"]
        f_score = scores["TF"]["F"]
        if t_score > f_score:
            mbti += "T"
            conf = t_score / (t_score + f_score) if (t_score + f_score) > 0 else 0.5
        elif f_score > t_score:
            mbti += "F"
            conf = f_score / (t_score + f_score) if (t_score + f_score) > 0 else 0.5
        else:
            mbti += "F"
            conf = 0.5
        total_confidence += conf
        
        # J vs P
        j_score = scores["JP"]["J"]
        p_score = scores["JP"]["P"]
        if j_score > p_score:
            mbti += "J"
            conf = j_score / (j_score + p_score) if (j_score + p_score) > 0 else 0.5
        elif p_score > j_score:
            mbti += "P"
            conf = p_score / (j_score + p_score) if (j_score + p_score) > 0 else 0.5
        else:
            mbti += "J"
            conf = 0.5
        total_confidence += conf
        
        return mbti, round(total_confidence / 4.0 * 100, 1)
    
    # ============================================================
    # LAYER 2: COGNITIVE FUNCTIONS (Strict Dominant Filtering)
    # ============================================================
    
    def _detect_cognitive_functions(self, text: str) -> Dict[str, float]:
        """ตรวจจับ Cognitive Functions จาก Intent Patterns"""
        scores = {}
        for func, patterns in COGNITIVE_INTENT_PATTERNS.items():
            matched = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
            scores[func] = min(matched / len(patterns), 1.0) if patterns else 0.0
        return scores
    
    def _cognitive_to_mbti_ranking(self, cf_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        """
        จัดอันดับ MBTI จาก Cognitive Function Scores โดยใช้ Strict Dominant Filtering
        Dominant x2, Auxiliary x1.5, Tertiary x1, Inferior x0.5*0.5 = 0.25
        """
        type_scores = {}
        for mbti_type, stack in MBTI_STACKS.items():
            dom = stack["dom"]
            aux = stack["aux"]
            ter = stack["ter"]
            inf = stack["inf"]
            
            # strict multipliers
            score = (
                cf_scores.get(dom, 0) * 3.0 * 2.0 +   # dominant x6
                cf_scores.get(aux, 0) * 2.0 * 1.5 +   # auxiliary x3
                cf_scores.get(ter, 0) * 1.0 +          # tertiary x1
                cf_scores.get(inf, 0) * 0.5 * 0.5      # inferior x0.25
            )
            type_scores[mbti_type] = score
        
        ranked = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        total = sum(s for _, s in ranked if s > 0) or 1.0
        result = []
        for mbti_type, score in ranked:
            if score > 0:
                result.append((mbti_type, round(score / total * 100, 1)))
        return result[:4]
    
    # ============================================================
    # ENNEAGRAM DETECTION
    # ============================================================
    
    def _detect_enneagram(self, text: str) -> List[Tuple[int, float]]:
        """ตรวจจับ Enneagram จาก Intent Patterns"""
        scores = {}
        for num, patterns in ENNEAGRAM_PATTERNS.items():
            matched = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
            scores[num] = matched
        
        total = sum(scores.values()) or 1.0
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = []
        for num, score in ranked:
            if score > 0:
                result.append((num, round(score / total * 100, 1)))
        return result[:4]
    
    # ============================================================
    # ENNEAGRAM BIAS: Type 8 boosts Te/Se types
    # ============================================================
    
    def _apply_enneagram_bias(self, mbti_ranking: List[TypePrediction],
                              enneagram_top: Optional[TypePrediction]) -> List[TypePrediction]:
        """ถ้า Enneagram Top เป็น Type 8 ให้ boost ประเภทที่มี Te หรือ Se"""
        if enneagram_top is None or enneagram_top.type_code != "Type 8":
            return mbti_ranking
        
        for pred in mbti_ranking:
            if pred.type_code in TE_SE_TYPES:
                pred.confidence += 10.0
        
        # re-sort by confidence
        mbti_ranking.sort(key=lambda x: x.confidence, reverse=True)
        return mbti_ranking[:4]
    
    # ============================================================
    # CROSS-REFERENCE & FINAL RANKING
    # ============================================================
    
    def _cross_reference(
        self, 
        dichotomy_mbti: str, 
        dichotomy_conf: float,
        cognitive_ranking: List[Tuple[str, float]]
    ) -> List[TypePrediction]:
        """
        Cross-Reference ระหว่าง Layer 1 และ Layer 2
        - ถ้าตรงกัน: boost 15%
        - ไม่ตรง: Cognitive 70%, Speech 10% (ลดทอน)
        """
        final_predictions = []
        
        if cognitive_ranking:
            for mbti_type, cog_conf in cognitive_ranking:
                if mbti_type == dichotomy_mbti:
                    combined_conf = round(cog_conf * 0.7 + dichotomy_conf * 0.3 + 15, 1)
                    combined_conf = min(combined_conf, 100.0)
                    evidence = [
                        f"Speech Signature: {dichotomy_mbti} ({dichotomy_conf}%)",
                        f"Cognitive Intent: {mbti_type} ({cog_conf}%)",
                        "✅ Both layers agree — boosted confidence"
                    ]
                else:
                    combined_conf = round(cog_conf * 0.7 + dichotomy_conf * 0.1, 1)
                    evidence = [
                        f"Speech Signature: {dichotomy_mbti} ({dichotomy_conf}%)",
                        f"Cognitive Intent: {mbti_type} ({cog_conf}%)",
                        "⚠️ Layers disagree — using Cognitive Intent as primary"
                    ]
                
                final_predictions.append(TypePrediction(
                    type_code=mbti_type,
                    type_name=MBTI_NAMES.get(mbti_type, "Unknown"),
                    confidence=combined_conf,
                    evidence=evidence
                ))
        else:
            # fallback to dichotomy only
            if dichotomy_mbti:
                final_predictions.append(TypePrediction(
                    type_code=dichotomy_mbti,
                    type_name=MBTI_NAMES.get(dichotomy_mbti, "Unknown"),
                    confidence=dichotomy_conf,
                    evidence=[
                        f"Speech Signature: {dichotomy_mbti} ({dichotomy_conf}%)",
                        "⚠️ Cognitive Intent not detected — using Speech only"
                    ]
                ))
        
        # Ultimate fallback
        if not final_predictions:
            final_predictions.append(TypePrediction(
                type_code="INFJ",
                type_name="The Advocate",
                confidence=33.0,
                evidence=["Fallback: No patterns detected — default INFJ"]
            ))
        
        return final_predictions[:4]
    
    # ============================================================
    # MAIN ANALYZE
    # ============================================================
    
    def analyze(self, text: str, top_n: int = 4) -> AnalysisResult:
        """
        วิเคราะห์ข้อความแบบ Hybrid พร้อม Tuning
        """
        # Layer 1: Dichotomy
        dichotomy_scores = self._detect_dichotomy(text)
        dichotomy_mbti, dichotomy_conf = self._dichotomy_to_mbti(dichotomy_scores)
        
        # Layer 2: Cognitive Functions (with strict filtering)
        cf_scores = self._detect_cognitive_functions(text)
        cognitive_ranking = self._cognitive_to_mbti_ranking(cf_scores)
        
        # Cross-Reference (initial ranking)
        mbti_ranking = self._cross_reference(dichotomy_mbti, dichotomy_conf, cognitive_ranking)
        
        # Enneagram
        ennea_ranking_raw = self._detect_enneagram(text)
        ennea_ranking = []
        for num, conf in ennea_ranking_raw:
            type_data = ENNEAGRAM_TYPES[num]
            ennea_ranking.append(TypePrediction(
                type_code=f"Type {num}",
                type_name=type_data["name"],
                confidence=conf,
                evidence=[
                    f"Core Fear: {type_data['core_fear']}",
                    f"Core Desire: {type_data['core_desire']}"
                ]
            ))
        
        if not ennea_ranking:
            ennea_ranking.append(TypePrediction(
                type_code="Type 5",
                type_name="The Investigator",
                confidence=50.0,
                evidence=["Fallback: No Enneagram patterns detected"]
            ))
        
        # Apply Enneagram Bias (if Type 8 top)
        ennea_top = ennea_ranking[0] if ennea_ranking else None
        mbti_ranking = self._apply_enneagram_bias(mbti_ranking, ennea_top)
        
        # Inconclusive Flag if top confidence < 40%
        if mbti_ranking and mbti_ranking[0].confidence < 40.0:
            mbti_ranking[0].evidence.append("⚠️ Result Inconclusive: top confidence < 40%")
        
        # Summary
        top_mbti = mbti_ranking[0] if mbti_ranking else None
        top_ennea = ennea_ranking[0] if ennea_ranking else None
        
        summary_parts = []
        if top_mbti:
            summary_parts.append(f"MBTI: {top_mbti.type_code} ({top_mbti.type_name}) — {top_mbti.confidence}%")
        if top_ennea:
            summary_parts.append(f"Enneagram: {top_ennea.type_code} ({top_ennea.type_name}) — {top_ennea.confidence}%")
        if cf_scores:
            top_func = max(cf_scores.items(), key=lambda x: x[1])
            if top_func[1] > 0:
                summary_parts.append(f"Dominant Intent: {top_func[0]} (score: {top_func[1]:.2f})")
        
        return AnalysisResult(
            mbti_ranking=mbti_ranking,
            enneagram_ranking=ennea_ranking,
            cognitive_signature=cf_scores,
            dichotomy_scores=dichotomy_scores,
            summary=" | ".join(summary_parts) if summary_parts else "ไม่สามารถวิเคราะห์ได้"
        )


# ============================================================
# RESULT FORMATTER
# ============================================================

class ResultFormatter:
    @staticmethod
    def to_markdown(result: AnalysisResult) -> str:
        md = []
        md.append("# 🧠 ผลวิเคราะห์บุคลิกภาพ (Hybrid V3.0 — Tuned)\n")
        
        # Dichotomy Scores
        md.append("## 🔤 Direct Dichotomy (Speech Signatures)\n")
        for dim, poles in result.dichotomy_scores.items():
            parts = [f"{p}={s:.0f}" for p, s in poles.items()]
            md.append(f"- **{dim}**: {', '.join(parts)}")
        md.append("")
        
        # Cognitive Functions
        md.append("## 🧬 Cognitive Functions (Intent Patterns)\n")
        for func, score in sorted(result.cognitive_signature.items(), key=lambda x: x[1], reverse=True):
            if score > 0:
                bar = "█" * int(score * 10)
                md.append(f"- **{func}**: {bar} ({score:.2f})")
        md.append("")
        
        # MBTI Ranking
        md.append("## 🏆 MBTI Ranking\n")
        for i, p in enumerate(result.mbti_ranking):
            md.append(f"**#{i+1} {p.type_code} ({p.type_name})** — {p.confidence}%")
            for e in p.evidence:
                md.append(f"  - {e}")
            md.append("")
        
        # Enneagram Ranking
        md.append("## 🎯 Enneagram Ranking\n")
        for i, p in enumerate(result.enneagram_ranking):
            md.append(f"**#{i+1} {p.type_code} ({p.type_name})** — {p.confidence}%")
            for e in p.evidence:
                md.append(f"  - {e}")
            md.append("")
        
        md.append(f"## 📝 Summary\n{result.summary}")
        
        return "\n".join(md)
    
    @staticmethod
    def to_json(result: AnalysisResult) -> str:
        return json.dumps({
            "mbti_ranking": [
                {"rank": i+1, "type": p.type_code, "name": p.type_name,
                 "confidence": p.confidence, "evidence": p.evidence}
                for i, p in enumerate(result.mbti_ranking)
            ],
            "enneagram_ranking": [
                {"rank": i+1, "type": p.type_code, "name": p.type_name,
                 "confidence": p.confidence, "evidence": p.evidence}
                for i, p in enumerate(result.enneagram_ranking)
            ],
            "cognitive_signature": result.cognitive_signature,
            "dichotomy_scores": {k: {p: s for p, s in v.items()} for k, v in result.dichotomy_scores.items()},
            "summary": result.summary
        }, ensure_ascii=False, indent=2)


# ============================================================
# QUICK API
# ============================================================

def analyze_text(text: str, top_n: int = 4) -> dict:
    """Quick API สำหรับ Orchestrator"""
    analyzer = PersonAnalyzer()
    result = analyzer.analyze(text, top_n)
    return {
        "mbti_ranking": [
            {"rank": i+1, "type": p.type_code, "name": p.type_name,
             "confidence": p.confidence, "evidence": p.evidence}
            for i, p in enumerate(result.mbti_ranking)
        ],
        "enneagram_ranking": [
            {"rank": i+1, "type": p.type_code, "name": p.type_name,
             "confidence": p.confidence, "evidence": p.evidence}
            for i, p in enumerate(result.enneagram_ranking)
        ],
        "cognitive_signature": result.cognitive_signature,
        "dichotomy_scores": {k: {p: s for p, s in v.items()} for k, v in result.dichotomy_scores.items()},
        "summary": result.summary
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    analyzer = PersonAnalyzer()
    formatter = ResultFormatter()
    
    test_cases = [
        (
            "INFJ Ti-heavy",
            """
            ระบบนี้มันไม่สมเหตุสมผลเลย 
            ทำไมถึงคิดว่า INFJ ต้องอ่อนแอ?
            ฉันรู้สึกว่ามันไม่ถูกต้อง 
            ฉันต้องตรวจสอบให้แน่ใจ
            ข้อมูลยังไม่พอ ขอเวลาวิเคราะห์ก่อน
            คนอื่นจะเดือดร้อนถ้าระบบมันผิด
            """
        ),
        (
            "INTJ",
            """
            ข้อมูลจากรายงานบอกว่าวิธีนี้มีประสิทธิภาพมากกว่า 30%
            ดังนั้นเราควรเปลี่ยนแผนทันที
            ขั้นตอนที่ 1: วิเคราะห์ข้อมูล
            ขั้นตอนที่ 2: จัดการทีม
            ขั้นตอนที่ 3: Execute
            Ref: https://example.com/report
            """
        ),
        (
            "INFP",
            """
            สำหรับฉัน มันไม่แฟร์เลย
            ถึงใครจะว่ายังไง แต่ฉันรู้สึกว่ามันไม่ถูกต้อง
            มันขัดกับตัวตนของฉัน
            ทำไมโลกนี้ถึงโหดร้ายกับคนที่แตกต่าง?
            """
        ),
        (
            "INFJ vs INFP (เคสจริงจากกลุ่ม)",
            """
            ฝากช่วยดูหน่อยนะคะ 
            ทำแบบทดสอบหลังจากที่ไม่ได้ทำมาซักพัก 
            สับสนว่าตัวเองเป็น infp หรือ infj 
            แล้วก็ไม่รู้ว่าตัวเองใช้ fi หรือ fe
            ถ้ามันกระทบความรู้สึกเรามาก ๆ 
            เราก็จะกล้าพูดปกป้องตัวเอง 
            แต่ส่วนใหญ่เราทนมากกว่า
            """
        ),
        (
            "ISTP (เคสกลุ่ม)",
            """
            อยากทราบว่า istp-a ทุกคนมีมุมมองกับไทป์นี้ยังไงครับ
            พูดตามตรงว่าใช้ชีวิตกับสังคมยากมาก 
            เปลี่ยนเพื่อนปีละหลายๆกลุ่ม 
            เข้ากับเพื่อนไม่ได้เลย
            ข้อดีก็ไม่เห็นแสดงจุดเด่นที่ชัดเจนเหมือนไทป์อื่น
            แต่ข้อเสียชัดมาก
            """
        ),
        (
            "INTP",
            """
            นิยามของคำว่า "ถูกต้อง" คืออะไรกันแน่?
            ตรรกะมันขัดกันเอง
            ขอเวลาแยกแยะก่อนว่าอะไรเป็นอะไร
            มันไม่สมเหตุสมผลเลยถ้าคิดแบบนั้น
            """
        ),
        (
            "ENFJ",
            """
            ทุกคนโอเคไหมคะ?
            บรรยากาศมันตึงๆ ไปหน่อย
            เรามาช่วยกันทำให้ดีขึ้นนะ
            เกรงใจคนที่ทำงานหนักจังเลย
            """
        ),
        (
            "ENTP",
            """
            แล้วถ้าเราลองเปลี่ยนวิธีคิดใหม่ทั้งหมดล่ะ?
            มันเชื่อมกับเรื่องนั้นได้นะ!
            มีอีกมุมนึงที่น่าสนใจ...
            หรือว่าเราจะลองทำตรงข้ามไปเลย?
            """
        ),
        (
            "Type 8 (The Challenger)",
            """
            อย่ามาบอกฉันว่าต้องทำอะไร
            ฉันจัดการเองได้ทั้งหมด
            ใครมีปัญหาก็มาเคลียร์กันตรงนี้เลย
            ไม่ต้องมาบังคับฉัน
            """
        ),
        (
            "Type 9 (The Peacemaker)",
            """
            อะไรก็ได้แหละ ตามนั้น
            อย่าทะเลาะกันเลย
            สบายๆ นะทุกคน
            ช่างเถอะ ไม่เป็นไร
            """
        ),
        (
            "INFJ 5w4 (เคสครู)",
            """
            ผมคิดว่าผมเป็น INFJ 5w4 ครับ 
            แต่เพื่อนบอกว่าไม่ใช่หรอก มันต้องแบบนี้ๆ 
            ผมเถียงสู้เขาไม่ได้ 
            ผมก็เลยถามว่างั้น ให้กูเป็นไรละ 
            มันบอกไม่รู้สิ 
            เอ้า แล้วกูทำข้อสอบมาแล้วบอกกูงี้ 
            มึงไปเถียงคนออกข้อสอบสิ
            """
        ),
        (
            "ENTJ 3w2 (หน้ากาก)",
            """
            ผมเป็น ENTJ 3w2 ครับ 
            ใครอยากรู้เรื่อง MBTI + Enneagram 
            comment มาเดี๋ยวอธิบายให้!
            ผมศึกษาเรื่องนี้มาเยอะมาก 
            #MBTI #Enneagram #Success
            """
        ),
    ]
    
    print("=" * 60)
    print("PERSON ANALYZER V3.0 — Hybrid (Tuned: Dominant Filtering + Enneagram Bias)")
    print("=" * 60)
    
    for i, (name, text) in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {name}")
        print(f"{'='*60}")
        result = analyzer.analyze(text)
        print(formatter.to_markdown(result))
    
    # 📊 สรุป
    print(f"\n{'='*60}")
    print("📊 สรุปผลการทดสอบทั้งหมด")
    print(f"{'='*60}")
    
    for i, (name, text) in enumerate(test_cases, 1):
        result = analyzer.analyze(text)
        top_mbti = result.mbti_ranking[0] if result.mbti_ranking else None
        top_ennea = result.enneagram_ranking[0] if result.enneagram_ranking else None
        
        mbti_str = f"{top_mbti.type_code} ({top_mbti.confidence}%)" if top_mbti else "N/A"
        ennea_str = f"{top_ennea.type_code} ({top_ennea.confidence}%)" if top_ennea else "N/A"
        
        print(f"  {i:2}. {name:<35} → MBTI: {mbti_str:<20} | Ennea: {ennea_str}")