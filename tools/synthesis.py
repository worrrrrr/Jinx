import datetime
from typing import Dict, Any, List, Optional
import swisseph as swe

# Import ภายในโปรเจกต์ Jinx
try:
    from tools.bazi import calculate_bazi_pillars, STEM_PROPERTIES, BRANCH_PROPERTIES
    from tools.jyotish import _parse_datetime, _get_lagna, RASHI
    from tools.western_astro import _get_ascendant, SIGNS
except ImportError:
    from bazi import calculate_bazi_pillars, STEM_PROPERTIES
    from jyotish import _parse_datetime, _get_lagna, RASHI
    from western_astro import _get_ascendant, SIGNS

def get_astrology_elements(dm_stem: str, vedic_rashi: str, west_rashi: str, thai_day: str) -> Dict[str, str]:
    """สกัดธาตุจาก 4 ศาสตร์"""
    bazi_elem_raw = STEM_PROPERTIES.get(dm_stem, {}).get("element", "Earth")
    bazi_map = {"Wood": "ไม้", "Fire": "ไฟ", "Earth": "ดิน", "Metal": "ทอง", "Water": "น้ำ"}
    bazi_elem_th = bazi_map.get(bazi_elem_raw, "ดิน")
    
    # ดึงธาตุจากอินเดีย
    vedic_elem = "ดิน"
    for r in RASHI:
        if r[1] == vedic_rashi:
            vedic_elem = r[4]
            break

    # ดึงธาตุจากสากล
    west_elem = "ดิน"
    for s in SIGNS:
        if s[1] == west_rashi:
            west_elem = s[3]
            break

    # ดึงธาตุจากไทย
    thai_elem_map = {
        "อาทิตย์": "ไฟ", "จันทร์": "ดิน", "อังคาร": "ลม", "พุธกลางวัน": "น้ำ",
        "พฤหัสบดี": "ดิน", "ศุกร์": "น้ำ", "เสาร์": "ไฟ", "พุธกลางคืน": "ลม"
    }
    thai_elem = thai_elem_map.get(thai_day, "ดิน")

    return {
        "จีน (BaZi)": bazi_elem_th,
        "อินเดีย (Vedic)": vedic_elem,
        "สากล (Western)": west_elem,
        "ไทย (ทักษา)": thai_elem
    }

def generate_synthesis_report(inp: str) -> str:
    """วิเคราะห์สังเคราะห์ 4 ศาสตร์ (เวอร์ชันแก้ Syntax Error)"""
    dt = _parse_datetime(inp)
    if dt is None:
        return "❌ รูปแบบวันเวลาเกิดไม่ถูกต้อง"

    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

    # 1. จีน, 2. อินเดีย, 3. สากล, 4. ไทย
    bazi_pillars = calculate_bazi_pillars(dt)
    dm_stem = bazi_pillars["day"][0]
    vedic_lagna = _get_lagna(jd)
    vedic_rashi = RASHI[vedic_lagna["sign"]][1]
    west_asc = _get_ascendant(jd)
    west_rashi = SIGNS[west_asc["sign"]][1]
    day_names = ["จันทร์", "อังคาร", "พุธกลางวัน", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    thai_day = day_names[dt.weekday()]

    elements = get_astrology_elements(dm_stem, vedic_rashi, west_rashi, thai_day)

    # นับธาตุเด่น
    elem_counts = {}
    for v in elements.values():
        elem_counts[v] = elem_counts.get(v, 0) + 1
    
    sorted_elems = sorted(elem_counts.items(), key=lambda x: x[1], reverse=True)
    dominant_elem, count = sorted_elems[0]

    # สร้างผลลัพธ์โดยไม่ใช้ Backslash ใน f-string
    report_lines = [
        "🔮 **สรุปผลวิเคราะห์สังเคราะห์อัตลักษณ์ (Synthesis)**",
        f"📅 ข้อมูล: {dt.strftime('%d/%m/%Y %H:%M')}",
        "---"
    ]
    
    for k, v in elements.items():
        report_lines.append(f"• {k}: ธาตุ{v}")
    
    report_lines.append("---")
    if count >= 3:
        report_lines.append(f"✅ **พลังธาตุเด่น:** ธาตุ{dominant_elem} (มีอิทธิพลสูงถึง {count} ศาสตร์)")
    else:
        report_lines.append(f"✨ **ธาตุประธาน:** ธาตุ{dominant_elem} (พลังงานมีความหลากหลาย)")

    return "\n".join(report_lines)