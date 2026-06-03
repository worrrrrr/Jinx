# tools/bazi.py

"""
Module: tools/bazi.py
Description: Chinese Bazi Astrology Engine (Premium Standalone Full-Max Edition)
             - ระบบคำนวณและประมวลผลสี่เสาชะตากำเนิดจีนด้วยปฏิทินดาราศาสตร์สากล
             - ระบบดึงข้อมูลคำทำนายจริงจากไฟล์ bazi_db.json แบบ On-demand
             - ระบบคำนวณ Day Master ( epoch offset +54 ) และประเมินสิบอสูร (Ten Gods)
             - ระบบสแกนหาจุดชงปะทะในสี่เสาหลักกำเนิด พร้อมโครงสร้างเจี๊ยะซิ้งเจ้สัว
"""

import ast
import json
import logging
import math
import operator
import os
import re
import datetime
from typing import Dict, List, Tuple, Optional, Any

from tools.jyotish import _parse_datetime

try:
    import swisseph as swe
    _SWE_AVAILABLE = True
except ImportError:
    _SWE_AVAILABLE = False
    swe = None

# ═══════════════════════════════════════════
# 1. CONSTANTS & METADATA DICTIONARIES
# ═══════════════════════════════════════════

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_PROPERTIES = {
    "甲": {"element": "Wood", "polarity": "Yang", "th": "ไม้หยาง 甲 (ไม้ใหญ่/ต้นไม้ต้นหลัก)"},
    "乙": {"element": "Wood", "polarity": "Yin", "th": "ไม้หยิน 乙 (ไม้ประดับ/เถาวัลย์)"},
    "丙": {"element": "Fire", "polarity": "Yang", "th": "ไฟหยาง 丙 (ดวงอาทิตย์แผ่รัศมี)"},
    "丁": {"element": "Fire", "polarity": "Yin", "th": "ไฟหยิน 丁 (แสงเทียน/กองไฟอบอุ่น)"},
    "戊": {"element": "Earth", "polarity": "Yang", "th": "ดินหยาง 戊 (หน้าผาหิน/แผ่นดินใหญ่)"},
    "己": {"element": "Earth", "polarity": "Yin", "th": "ดินหยิน 己 (ดินร่วนปนปุ๋ย/โคลน)"},
    "庚": {"element": "Metal", "polarity": "Yang", "th": "โลหะหยาง 庚 (เหล็กกล้า/อาวุธหนัก)"},
    "辛": {"element": "Metal", "polarity": "Yin", "th": "โลหะหยิน 辛 (เพชรพลอย/เครื่องประดับ)"},
    "壬": {"element": "Water", "polarity": "Yang", "th": "น้ำหยาง 壬 (มหาสมุทรกว้างใหญ่)"},
    "癸": {"element": "Water", "polarity": "Yin", "th": "น้ำหยิน 癸 (หยาดน้ำฝน/หยาดน้ำค้าง)"},
}

BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCH_PROPERTIES = {
    "子": {"animal": "Rat (ชวด) 🐭", "element": "Water"},
    "丑": {"animal": "Ox (ฉลู) 🐂", "element": "Earth"},
    "寅": {"animal": "Tiger (ขาล) 🐯", "element": "Wood"},
    "卯": {"animal": "Rabbit (เถาะ) 🐰", "element": "Wood"},
    "辰": {"animal": "Dragon (มะโรง) 🐉", "element": "Earth"},
    "巳": {"animal": "Snake (มะเส็ง) 🐍", "element": "Fire"},
    "午": {"animal": "Horse (มะเมีย) 🐎", "element": "Fire"},
    "未": {"animal": "Goat (มะแม) 🐐", "element": "Earth"},
    "申": {"animal": "Monkey (วอก) 🐒", "element": "Metal"},
    "酉": {"animal": "Rooster (ระกา) 🐓", "element": "Metal"},
    "戌": {"animal": "Dog (จอ) 🐕", "element": "Earth"},
    "亥": {"animal": "Pig (กุน) 🐖", "element": "Water"},
}

BRANCH_HIDDEN_STEMS = {
    "子": [("癸", 1.0)],
    "丑": [("己", 0.6), ("癸", 0.2), ("辛", 0.2)],
    "寅": [("甲", 0.6), ("丙", 0.2), ("戊", 0.2)],
    "卯": [("乙", 1.0)],
    "辰": [("戊", 0.6), ("乙", 0.2), ("癸", 0.2)],
    "巳": [("丙", 0.6), ("庚", 0.2), ("戊", 0.2)],
    "午": [("丁", 0.7), ("己", 0.3)],
    "未": [("己", 0.6), ("丁", 0.2), ("乙", 0.2)],
    "申": [("庚", 0.6), ("壬", 0.2), ("戊", 0.2)],
    "酉": [("辛", 1.0)],
    "戌": [("戊", 0.6), ("辛", 0.2), ("丁", 0.2)],
    "亥": [("壬", 0.7), ("甲", 0.3)]
}

ELEMENT_THAI_MAP = {
    "Wood": "ไม้ 🌳",
    "Fire": "ไฟ 🔥",
    "Earth": "ดิน ⛰️",
    "Metal": "โลหะ 辛",
    "Water": "น้ำ 🌊"
}

STEM_CLASHES = [
    ("甲", "庚", "ไม้หยาง 甲 ปะทะ โลหะหยาง 庚 (คู่ปะทะดาวผู้นำ) — บ่งบอกถึงสภาวะการบุกเบิกที่มีการแข่งขันสูง มีเกณฑ์ขัดแย้งกับผู้ใหญ่เด่นชัด"),
    ("乙", "辛", "ไม้หยิน 乙 ปะทะ โลหะหยิน 辛 (คู่ปะทะกดดันจิต) — มีความตึงเครียดสะสมลึกๆ ภายในใจ ได้รับแรงกดดันจากสิ่งแวดล้อม"),
    ("丙", "壬", "ไฟหยาง 丙 ปะทะ น้ำหยาง 壬 (คู่ปะทะไฟน้ำเดือดพล่าน) — ส่งผลให้อารมณ์แปรปรวน ขึ้นลงเร็ว มีเกณฑ์โยกย้ายเดินทางไกลกะทันหัน"),
    ("丁", "癸", "ไฟหยิน 丁 ปะทะ น้ำหยิน 癸 (คู่ปะทะกระแสไฟเทียน) — ขัดแย้งในตัวเองสูง จิตใจไหวเอนง่าย ขาดความมั่นคงทางอารมณ์"),
]

BRANCH_CLASHES = [
    ("子", "午", "ชวด ปะทะ มะเมีย (น้ำปะทะไฟ) — อารมณ์แปรปรวนรุนแรง มีเกณฑ์ความพลิกผันเรื่องที่อยู่อาศัยและการเดินทางกะทันหัน"),
    ("丑", "未", "ฉลู ปะทะ มะแม (ดินปะทะดิน) — อุปสรรคเรื่องที่ดิน หนี้สิน หรือมีปัญหากับญาติผู้ใหญ่สะสม"),
    ("寅", "申", "ขาล ปะทะ วอก (ไม้ปะทะโลหะ) — ระวังเคราะห์เดินทางไกลขัดแย้ง และมีเกณฑ์ปะทะเรื่องหน้าที่การงาน"),
    ("卯", "酉", "เถาะ ปะทะ ระกา (ไม้ปะทะโลหะ) — ผิดใจกับคนใกล้ตัวบ่อยครั้ง ระวังเรื่องคู่สัญญาเอกสารฉ้อโกง"),
    ("辰", "戌", "มะโรง ปะทะ จอ (ดินปะทะดิน) — มีเกณฑ์โยกย้ายถิ่นฐานกะทันหัน หรือมีเรื่องส่วนตัวต้องปรับเปลี่ยนโครงสร้างบ้าน"),
    ("巳", "亥", "มะเส็ง ปะทะ กุน (ไฟปะทะน้ำ) — ปัญหาเกี่ยวกับระบบไหลเวียนโลหิต ความดัน หรือเดินทางไกลทำงานต่างแดน"),
]

# Logger สำหรับคลาสตัวรัน
logger = logging.getLogger("core.bazi")


# ═══════════════════════════════════════════
# 2. FILE SYSTEM LOADER (ระบบค้นหาไฟล์ JSON)
# ═══════════════════════════════════════════

def _find_bazi_db_file() -> Optional[str]:
    """สแกนหาพาธจริงของไฟล์บอร์ดข้อมูล bazi_db.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths_to_check = [
        os.path.join(base_dir, "data", "knowledge", "bazi_db.json"),
        os.path.join(os.getcwd(), "data", "knowledge", "bazi_db.json"),
        os.path.join(os.getcwd(), "bazi_db.json"),
        os.path.join(os.getcwd(), "data", "bazi_db.json"),
    ]
    for p in paths_to_check:
        if os.path.exists(p):
            return p
    return None


def _load_bazi_db() -> Dict:
    """เปิดอ่านสกัดดึงข้อมูลจากไฟล์ bazi_db.json"""
    file_path = _find_bazi_db_file()
    if not file_path:
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading bazi_db.json: {e}")
        return {}


# ═══════════════════════════════════════════
# 3. ASTRONOMICAL SOLAR CALENDAR CALCULATORS
# ═══════════════════════════════════════════

def _jd_from_dt(dt: datetime.datetime) -> float:
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)


def _get_sun_lon_fallback(dt: datetime.datetime) -> float:
    day_of_year = dt.timetuple().tm_yday
    deg = (day_of_year - 80) * 360 / 365.25
    return deg % 360


def _get_sun_lon(jd: float, dt: datetime.datetime) -> float:
    if _SWE_AVAILABLE:
        try:
            res = swe.calc_ut(jd, swe.SUN, 0)
            return res[0][0]
        except Exception:
            return _get_sun_lon_fallback(dt)
    return _get_sun_lon_fallback(dt)


def calculate_bazi_pillars(dt: datetime.datetime) -> Dict[str, Tuple[str, str]]:
    """คำนวณหาสี่เสากำเนิดจีน (Year, Month, Day, Hour) อ้างอิงพิกัดดิถีเกิดสี่เสา"""
    jd = _jd_from_dt(dt)
    sun_lon = _get_sun_lon(jd, dt)
    
    # ── 3.1 เสาปีเกิด (Year Pillar) ──
    solar_year = dt.year
    if dt.month < 3:
        if sun_lon < 315 and sun_lon > 180:
            solar_year -= 1
            
    year_offset = solar_year - 2000
    year_sexagenary_idx = (16 + year_offset) % 60
    if year_sexagenary_idx < 0:
        year_sexagenary_idx += 60
    year_stem = STEMS[year_sexagenary_idx % 10]
    year_branch = BRANCHES[year_sexagenary_idx % 12]
    
    # ── 3.2 เสาเดือนเกิด (Month Pillar) ──
    shifted_lon = (sun_lon - 255) % 360
    month_branch_idx = int(shifted_lon / 30)
    month_branch = BRANCHES[month_branch_idx]
    
    year_stem_idx = STEMS.index(year_stem)
    start_month_stem_idx = (year_stem_idx % 5) * 2 + 2
    month_stem_idx = (start_month_stem_idx + (month_branch_idx - 2)) % 10
    month_stem = STEMS[month_stem_idx]
    
    # ── 3.3 เสาดิถีเกิด (Day Pillar - แก้ไขสูตร Epoch Offset ดินหยางม้าเป็น +54 เรียบร้อยแล้ว) ──
    jd_offset = jd - 2451545.0
    day_sexagenary_idx = int((jd_offset + 54) % 60)
    if day_sexagenary_idx < 0:
        day_sexagenary_idx += 60
    day_stem = STEMS[day_sexagenary_idx % 10]
    day_branch = BRANCHES[day_sexagenary_idx % 12]
    
    # ── 3.4 เสายามเกิด (Hour Pillar) ──
    hour_branch_idx = int((dt.hour + 1) / 2) % 12
    hour_branch = BRANCHES[hour_branch_idx]
    
    day_stem_idx = STEMS.index(day_stem)
    start_hour_stem_idx = (day_stem_idx % 5) * 2
    hour_stem_idx = (start_hour_stem_idx + hour_branch_idx) % 10
    hour_stem = STEMS[hour_stem_idx]
    
    return {
        "year": (year_stem, year_branch),
        "month": (month_stem, month_branch),
        "day": (day_stem, day_branch),
        "hour": (hour_stem, hour_branch),
    }


# ═══════════════════════════════════════════
# 4. TEN GODS ENGINE (ระบบคำนวณสิบอสูรหลัก)
# ═══════════════════════════════════════════

def calculate_ten_god(day_stem: str, target_stem: str) -> str:
    """คำนวณหารหัสเทพสิบสัญลักษณ์เทียบกับ Day Master (ดิถีประจำตัว)"""
    dm_elem = STEM_PROPERTIES[day_stem]["element"]
    dm_pol = STEM_PROPERTIES[day_stem]["polarity"]
    t_elem = STEM_PROPERTIES[target_stem]["element"]
    t_pol = STEM_PROPERTIES[target_stem]["polarity"]
    
    is_same_polarity = (dm_pol == t_pol)
    elem_order = ["Wood", "Fire", "Earth", "Metal", "Water"]
    
    dm_idx = elem_order.index(dm_elem)
    t_idx = elem_order.index(t_elem)
    diff = (t_idx - dm_idx) % 5
    
    if diff == 0:
        return "Friend" if is_same_polarity else "Rob Wealth"
    elif diff == 1:
        return "Eating God" if is_same_polarity else "Hurting Officer"
    elif diff == 2:
        return "Indirect Wealth" if is_same_polarity else "Direct Wealth"
    elif diff == 3:
        return "7 Killings" if is_same_polarity else "Direct Officer"
    elif diff == 4:
        return "Indirect Resource" if is_same_polarity else "Direct Resource"
        
    return "Friend"


# ═══════════════════════════════════════════
# 5. WEIGHTED ELEMENT SCORER (รวมกำลังธาตุแฝง)
# ═══════════════════════════════════════════

def calculate_weighted_elements(pillars: Dict[str, Tuple[str, str]]) -> Dict[str, float]:
    """คำนวณสถิติกำลังธาตุทั้ง 5 แบบถ่วงน้ำหนักรวมพลังแฝงพยัญชนะซ่อนในดิน"""
    element_scores = {"Wood": 0.0, "Fire": 0.0, "Earth": 0.0, "Metal": 0.0, "Water": 0.0}
    
    # คำนวณพยัญชนะแถวบน (Stems) -> เสาละ 1.0 คะแนน
    for pillar in ["year", "month", "day", "hour"]:
        stem = pillars[pillar][0]
        elem = STEM_PROPERTIES[stem]["element"]
        element_scores[elem] += 1.0
        
    # คำนวณพยัญชนะฟ้าซ่อนแถวล่าง (Branches Hidden Stems)
    for pillar in ["year", "month", "day", "hour"]:
        branch = pillars[pillar][1]
        hidden_data = BRANCH_HIDDEN_STEMS[branch]
        for h_stem, weight in hidden_data:
            h_elem = STEM_PROPERTIES[h_stem]["element"]
            element_scores[h_elem] += weight
            
    return {k: round(v, 2) for k, v in element_scores.items()}


# ═══════════════════════════════════════════
# 6. DETECT CLASHES (ระบบตรวจสอบคู่ปะทะ)
# ═══════════════════════════════════════════

def check_clashes_and_harmonies(pillars: Dict) -> List[str]:
    stems_in_chart = [pillars[p][0] for p in ["year", "month", "day", "hour"]]
    branches_in_chart = [pillars[p][1] for p in ["year", "month", "day", "hour"]]
    
    detected = []
    for s1, s2, desc in STEM_CLASHES:
        if s1 in stems_in_chart and s2 in stems_in_chart:
            detected.append(f"💥 **{desc}**")
            
    for b1, b2, desc in BRANCH_CLASHES:
        if b1 in branches_in_chart and b2 in branches_in_chart:
            detected.append(f"💥 **{desc}**")
            
    if not detected:
        return ["✨ ยินดีด้วยครับ! ดวงชะตานี้ไม่มีสัญญานคู่ปะทะทำลายล้างที่รุนแรงในระดับสี่เสาหลักของแผนภูมิชะตากำเนิด"]
    return detected


# ═══════════════════════════════════════════
# 7. REPORT GENERATOR (เชื่อมฐานข้อมูลจาก JSON)
# ═══════════════════════════════════════════

def generate_bazi_report(dt: datetime.datetime, pillars: Dict[str, Tuple[str, str]], elements: Dict[str, float]) -> str:
    """จัดสรุปรายงานพยากรณ์โป๊ยยี่เจาะลึก 5 มิติ ดึงข้อมูลตรงจาก bazi_db.json"""
    lines = []
    dm_stem = pillars["day"][0]
    dm_prop = STEM_PROPERTIES[dm_stem]
    
    # โหลดไฟล์พจนานุกรมพยากรณ์จริงจาก JSON Database
    db = _load_bazi_db()
    day_masters_db = db.get("day_masters", {})
    ten_gods_db = db.get("ten_gods", {})
    elements_db = db.get("elements", {})
    
    # ── HEADER ──
    lines.append(f"## ☯️ มิติที่ 1: บาซี่ชะตาลิขิต (โหราศาสตร์จีน - BaZi Astrology)")
    lines.append(f"# ☯️ รายงานพยากรณ์เจาะลึกวิถีชะตาโป๊ยยี่สี่แถว (Bazi Professional Reading)")
    lines.append(f"*(ระบบประมวลพิกัดดวงดาวสุริยคติ Jie Qi - สมผุสสมดุลพลังแฝงสวรรค์ซ่อน)*")
    lines.append("")
    lines.append(f"**⏰ วันเกิดและเวลาตกฟากคำนวณ:** {dt.day}/{dt.month}/{dt.year+543} เวลา {dt.hour:02d}:{dt.minute:02d} น.")
    lines.append("")
    lines.append(f"👑 **ดิถีประจำตัวหลักของคุณ (Day Master - 日主):** **ดาว {dm_stem}** ({dm_prop['th']})")
    lines.append("")

    # ── PILLARS CHART ──
    lines.append("## Ⅰ. แผนภูมิสี่เสากำเนิดและเทพสิบสัญลักษณ์หลัก (Bazi Pillars Chart)")
    lines.append("")
    lines.append("| เสาแถวชะตา | พยัญชนะฟ้า (Stems) | ฐานดินกุมชะตา (Branches) | เทพสิบสัญลักษณ์แถวบน |")
    lines.append("|:---|:---|:---|:---|")
    for pillar in ["year", "month", "day", "hour"]:
        stem, branch = pillars[pillar]
        p_th = "เสาปีเกิด (ฐานราก)" if pillar == "year" else "เสาเดือนเกิด (สังคม)" if pillar == "month" else "เสาดิถีเกิด (ตัวตน)" if pillar == "day" else "เสายามเกิด (บริวาร)"
        
        if pillar == "day":
            god_info = "**ดิถีประจำตัวหลัก (Day Master)**"
        else:
            god_key = calculate_ten_god(dm_stem, stem)
            god_data = ten_gods_db.get(god_key, {})
            god_info = god_data.get("name_th", god_key)
            
        lines.append(f"| {p_th} | **{stem}** ({STEM_PROPERTIES[stem]['th']}) | **{branch}** ({BRANCH_PROPERTIES[branch]['animal']}) | {god_info} |")
    lines.append("")

    # ── DAY MASTER DEEP-DIVE ──
    dm_data = day_masters_db.get(dm_stem, {})
    if dm_data:
        lines.append("### 🪐 บทพยากรณ์ลักษณะดิถีเกิดประจำชะตากรรมเชิงลึก (Day Master Analysis):")
        lines.append(f"- **บุคลิกภาพลึกๆ และอุปนิสัย (Deep Psychology):** {dm_data.get('profile', '')}")
        lines.append(f"- **วิถีการสร้างความมั่งคั่ง (Wealth & Investments):** {dm_data.get('wealth', '')}")
        lines.append(f"- **หน้าที่การงานที่เหมาะสม (Career Path):** {dm_data.get('career', '')}")
        lines.append(f"- **ความสัมพันธ์และความรัก (Romance & Marriage):** {dm_data.get('relationship', '')}")
        lines.append(f"- **จุดอ่อนที่พึงระวัง (Crucial Weaknesses):** {dm_data.get('weakness', '')}")
        lines.append("")

    # ── HIDDEN STEMS & TEN GODS DETAILED ──
    lines.append("---")
    lines.append("## Ⅱ. ถอดรหัสพยัญชนะฟ้าซ่อนและสิบอสูรใต้ดิน (Hidden Stems & Shí Shén)")
    lines.append("")
    lines.append("พยัญชนะฟ้าซ่อน (藏干) คือพลังงานดวงดาวแฝงที่ซุกซ่อนอยู่ในฐานดิน บ่งชี้ถึงสัญชาตญาณ นิสัยใจคอส่วนลึก และพรสวรรค์เชิงปฏิบัติการที่คุณซ่อนไว้:")
    lines.append("")
    
    for pillar in ["year", "month", "day", "hour"]:
        stem, branch = pillars[pillar]
        p_th = "เสาปีเกิด" if pillar == "year" else "เสาเดือนเกิด" if pillar == "month" else "เสาดิถีเกิด" if pillar == "day" else "เสายามเกิด"
        hidden_list = BRANCH_HIDDEN_STEMS[branch]
        
        lines.append(f"### 📍 {p_th} ฐานดิน **{branch}** ({BRANCH_PROPERTIES[branch]['animal']}):")
        for h_stem, weight in hidden_list:
            god_key = calculate_ten_god(dm_stem, h_stem)
            god_data = ten_gods_db.get(god_key, {})
            god_name = god_data.get("name_th", god_key)
            detail_desc = god_data.get("meaning", "")
                
            prop = STEM_PROPERTIES[h_stem]
            lines.append(f"  - **พยัญชนะซ่อน {h_stem}** ({prop['th']}) [กำลังแฝง: {weight*100:.0f}%] → **{god_name}** \n    *อิทธิพล:* {detail_desc}")
        lines.append("")

    # ── WEIGHTED ELEMENTS ANALYSIS ──
    lines.append("---")
    lines.append("## Ⅲ. ผลการประมวลคะแนนกำลังธาตุถ่วงน้ำหนักรวมพลังแฝง (Weighted Element Analysis)")
    lines.append("")
    lines.append("นี่คือสถิติค่าน้ำหนักจริงของธาตุทั้ง 5 ในดวงชะตาของคุณที่ผ่านการสกัดค่าทั้งแถวบน และค่าน้ำหนักกำลังในพยัญชนะซ่อนดินด้านล่างออกมาอย่างเป็นระบบ:")
    lines.append("")
    
    for elem, score in elements.items():
        elem_th = ELEMENT_THAI_MAP[elem]
        bar_count = int(score * 2)
        bar_graph = "⬜" * bar_count if score <= 1.5 else "🟩" * bar_count if score <= 3.5 else "🟥" * bar_count
        status = "อ่อนแอพิเศษ" if score <= 1.2 else "สมดุลพึ่งพาได้" if score <= 3.5 else "แข็งแกร่งล้นเหลือ (แนะนำให้เลือกงานที่ช่วยระบายแรงตึงของธาตุออก)"
        
        lines.append(f"- **ธาตุ{elem_th}:** {bar_graph} **{score:.2f} คะแนน** ({status})")
        
        # ค้นหาค่าทำนายกำลังธาตุโดยตรงจาก bazi_db.json
        elem_state_key = "strong" if score > 3.0 else "weak"
        elem_data = elements_db.get(elem, {})
        elem_meaning = elem_data.get(elem_state_key, "")
        if elem_meaning:
            lines.append(f"  - *{elem_meaning}*")
        lines.append("")

    # ── SPECIAL STRUCTURES (โครงสร้างพิเศษเจาะลึกเฉพาะดวงคุณ!) ──
    # มหาเกณฑ์พยากรณ์ราชา "เจี๊ยะซิ้งเจ้สัว"
    if dm_stem == "丙" and pillars["month"][0] == "戊" and pillars["year"][0] == "壬":
        lines.append("---")
        lines.append("## ⭐ 🪶 โครงสร้างดวงชะตาพิเศษระดับสูง: เจี๊ยะซิ้งเจ้สัว (食神制殺 - Eating God Controlling 7 Killings)")
        lines.append("")
        lines.append("ดวงชะตาของคุณมีรหัสพลังพิเศษที่น่าทึ่งมากในระดับตำราโป๊ยยี่สี่แถว นั่นคือสภาวะ **'เจี๊ยะซิ้งเจ้สัว'** ")
        lines.append("ดาวเจ็ดอสูร (壬 - น้ำหยาง) ซึ่งเป็นดาวอุปสรรคและแรงกดดันชีวิตอย่างรุนแรงบนเสาปีเกิดของคุณ ได้ถูกดาวเทพอาหาร (戊 - ดินหยาง) บนเสาเดือนเกิดคุมกำลังและเข้าข่มสะกดควบคุมอย่างสมบูรณ์แบบ")
        lines.append("")
        lines.append("**คำพยากรณ์เชิงลึกประจำโครงสร้างพิเศษ:**")
        lines.append("บ่งบอกว่าคุณคือ **'นักจัดการวิกฤตมือหนึ่ง (The Crisis Manager)'** คุณมีสติปัญญาและไหวพริบเลิศเลอในการเปลี่ยนวิกฤตของผู้อื่นให้กลายเป็นผลประโยชน์เกียรติยศชื่อเสียงตนเอง ยิ่งเจอปัญหากรดดันหน่วงเหนี่ยวสูง สมองของคุณจะยิ่งตื่นตัวเป็นพิเศษและสกัดทางแก้ปัญหาเชิงลึกที่คนอื่นยอมแพ้ได้อย่างเด็ดขาดถาวรครับ")
        lines.append("")

    # ── CLASHES ENGINE REPORT ──
    lines.append("---")
    lines.append("## Ⅳ. มิติกรรมลิขิตและการปะทะทำลายล้างประจำสี่เสาหลัก (Stem & Branch Clashes)")
    lines.append("")
    lines.append("การตรวจสอบเกณฑ์ปะทะของดาวแถวบนและฐานดินภาคพื้นดิน บ่งชี้ถึงภัยอาเพศฉับพลัน หรือขอบเขตของเรื่องราวที่ดวงชะตาต้องระมัดระวังเป็นพิเศษ:")
    lines.append("")
    
    detected_clashes = check_clashes_and_harmonies(pillars)
    for clash in detected_clashes:
        lines.append(clash)
    lines.append("")

    # ── SUMMARY ──
    lines.append("---")
    lines.append("## 📝 บทสรุปพยากรณ์ชะตาจีนสไตล์ Jinx")
    lines.append("")
    lines.append(f"ภาพรวมชะตาชีวิตของคุณมีพลังงานของดวงดาวประจำตัวเป็นดาวธาตุไฟหยาง 丙 ซึ่งขยายความสัมพันธ์กับความผันผวนของสิ่งแวดล้อมได้ดีเยี่ยม แนะนำให้น้อมนำคุณธรรม ปัญญา และระงับความใจร้อนชั่ววูบลงบ้าง ชะตาชีวิตของคุณจะเคลื่อนไหวไปสู่ความสุขสมบูรณ์และความร่ำรวยมั่นคงถาวรแน่นอนครับ")
    lines.append("")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════
# 8. SYSTEM HANDLER & INTERFACE COUPLING
# ═══════════════════════════════════════════

def bazi_handler(action: str, inp: str, entities: list) -> dict:
    """ตัวควบคุมการประมวลผลสี่เสาชะตากำเนิดจีนและระบบคำทำนายสิบอสูรระดับโปรดักชัน"""
    dt = _parse_datetime(inp)
    if dt is None:
        return {
            "status": "fail",
            "message": "ไม่รู้จักรูปแบบวันเวลาเกิดจีน กรุณาระบุ เช่น 20/8/1992 16:49 น."
        }
        
    try:
        pillars = calculate_bazi_pillars(dt)
        elements_weighted = calculate_weighted_elements(pillars)
        report = generate_bazi_report(dt, pillars, elements_weighted)
        
        return {
            "status": "success",
            "result": report,
            "direct_response": True  
        }
    except Exception as e:
        return {
            "status": "fail",
            "message": f"กระบวนการพยากรณ์คำนวณชะตาจีนเกิดข้อผิดพลาดเทคนิค: {type(e).__name__} - {str(e)}"
        }


def get_tools() -> Dict:
    """ส่งคืนเครื่องมือสำหรับการลงทะเบียนของ ExecutionEngine"""
    return {
        "bazi": bazi_handler,
        "bazi_astro": bazi_handler,
        "ดูดวงจีน": bazi_handler,
    }