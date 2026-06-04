# tools/synthesis.py

import datetime
from typing import Dict, Any, List, Optional
from tools.bazi import calculate_bazi_pillars, STEM_PROPERTIES, BRANCH_PROPERTIES
from tools.jyotish import _parse_datetime, _get_sidereal_planets, _get_lagna, RASHI, NAKSHATRA, _get_nakshatra
from tools.western_astro import _get_planet_positions, _get_ascendant, SIGNS
import swisseph as swe

# ═══════════════════════════════════════════
# 4-ASTROLOGY SYNTHESIS ENGINE (Advanced Core)
# ═══════════════════════════════════════════

def get_astrology_elements(dm_stem: str, vedic_rashi: str, west_rashi: str, thai_day: str) -> Dict[str, str]:
    """สกัดและจับคู่ธาตุของแต่ละศาสตร์เพื่อเปรียบเทียบ"""
    # 1. จีน (BaZi Day Master Element)
    bazi_elem_raw = STEM_PROPERTIES[dm_stem]["element"]
    bazi_elem_th = "ไม้" if bazi_elem_raw == "Wood" else "ไฟ" if bazi_elem_raw == "Fire" else "ดิน" if bazi_elem_raw == "Earth" else "โลหะ" if bazi_elem_raw == "Metal" else "น้ำ"
    
    # 2. อินเดีย (Jyotish Vedic Lagna Element)
    # ค้นหาธาตุจากตาราง RASHI
    vedic_elem = "ดิน"
    for r in RASHI:
        if r[1] == vedic_rashi:
            vedic_elem = r[4]
            break

    # 3. สากล (Western Rising Element)
    west_elem = "ดิน"
    for s in SIGNS:
        if s[1] == west_rashi:
            west_elem = s[3]
            break

    # 4. ไทย (ทักษาปกรณ์ - วันเกิดบอกกำลังธาตุ)
    thai_elem_map = {
        "อาทิตย์": "ไฟ", "จันทร์": "ดิน", "อังคาร": "ลม", "พุธกลางวัน": "น้ำ",
        "พฤหัสบดี": "ดิน", "ศุกร์": "น้ำ", "เสาร์": "ไฟ", "พุธกลางคืน": "ลม"
    }
    thai_elem = thai_elem_map.get(thai_day, "ดิน")

    return {
        "bazi": bazi_elem_th,
        "vedic": vedic_elem,
        "western": west_elem,
        "thai": thai_elem
    }

def generate_synthesis_report(inp: str) -> str:
    """วิเคราะห์สังเคราะห์เปรียบเทียบ 4 ศาสตร์ หาจุดร่วม จุดต่าง เพื่อประกอบเป็นสรุปตัวตนที่แท้จริง"""
    dt = _parse_datetime(inp)
    if dt is None:
        return "❌ รูปแบบวันเวลาเกิดไม่ถูกต้อง กรุณาระบุ เช่น 20/8/1992 16:49 น."

    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

    # 1. จีน (BaZi)
    bazi_pillars = calculate_bazi_pillars(dt)
    dm_stem = bazi_pillars["day"][0]
    dm_desc = STEM_PROPERTIES[dm_stem]["th"]
    animal_year = BRANCH_PROPERTIES[bazi_pillars["year"][1]]["animal"]

    # 2. อินเดีย (Jyotish Vedic)
    vedic_planets = _get_sidereal_planets(jd)
    vedic_lagna = _get_lagna(jd)
    vedic_rashi = RASHI[vedic_lagna["sign"]][1]
    moon_lon = vedic_planets.get(swe.MOON, {}).get("lon", 0)
    vedic_nk = _get_nakshatra(moon_lon)
    vedic_nakshatra = f"{vedic_nk['sanskrit']} ({vedic_nk['thai']})"

    # 3. สากล (Western Tropical)
    west_planets = _get_planet_positions(jd)
    west_asc = _get_ascendant(jd)
    west_rashi = SIGNS[west_asc["sign"]][1]
    sun_lon = west_planets.get(swe.SUN, {}).get("lon", 0)
    west_sun_rashi = SIGNS[int(sun_lon / 30)][1]

    # 4. โหราศาสตร์ไทย (วันเกิด)
    day_names = ["อาทิตย์", "จันทร์", "อังคาร", "พุธกลางวัน", "พฤหัสบดี", "ศุกร์", "เสาร์"]
    weekday_idx = dt.weekday()
    thai_weekday_idx = (weekday_idx + 1) % 7
    thai_day = day_names[thai_weekday_idx]

    # ดึงค่าธาตุของแต่ละศาสตร์มาวิเคราะห์จุดร่วม-จุดต่าง (Synthesis)
    elements = get_astrology_elements(dm_stem, vedic_rashi, west_rashi, thai_day)

    # คำนวณความถี่ของธาตุในทุกระบบเพื่อหาจุดร่วมและจุดต่าง
    elem_counts = {}
    for k, v in elements.items():
        elem_counts[v] = elem_counts.get(v, 0) + 1

    # หาธาตุเด่นร่วม (Dominant Convergence Element)
    dominant_elems = [k for k, v in elem_counts.items() if v == max(elem_counts.values())]
    dominant_elem = dominant_elems[0] if dominant_elems else "ดิน"
    dominance_level = elem_counts.get(dominant_elem, 1)

    # ═══════════════════════════════════════════
    # ANALYSIS: CONVERGENCES (จุดร่วมที่ส่งเสริมกัน)
    # ═══════════════════════════════════════════
    convergences = []
    if dominance_level >= 3:
        convergences.append(f"🔥 **พลังธาตุร่วมที่ทรงคุณค่าล้นพ้น:** ชะตานี้มี **ธาตุ{dominant_elem}** ปรากฏร่วมกันถึง {dominance_level} ใน 4 ศาสตร์ ส่งผลให้ตัวตนแก่นแท้ของคุณมีความเป็นอันหนึ่งอันเดียวกันอย่างมั่นคงสูงมาก")
    else:
        convergences.append(f"✨ **พลังงานธาตุแบบผสมผสานสมดุล:** ศาสตร์ต่างๆ บ่งบอกถึงพลังงานที่กระจายตัวอย่างสมดุล ชะตาชีวิตมีความยืดหยุ่นสูง ปรับตัวเข้ากับสถานการณ์และโอกาสใหม่ๆ ได้ดี")

    if vedic_rashi == west_rashi:
        convergences.append(f"🤝 **จุดเชื่อมลัคนาไร้รอยต่อ (Lagna Convergence):** ลัคนาพิกัดอินเดียและสากลสถิตตรงกันที่ **ราศี{vedic_rashi}** บ่งชี้ว่าตัวตนที่แสดงออกสังคมและวิถีกรรมด้านในไม่มีความขัดแย้งเชิงขั้ว")

    # ═══════════════════════════════════════════
    # ANALYSIS: DIVERGENCES (จุดต่างที่ขัดแย้งหรือต้องปรับสมดุล)
    # ═══════════════════════════════════════════
    divergences = []
    # ค้นหาธาตุที่เป็นปฏิปักษ์กันในระบบชะตา เช่น ไฟ ปะทะ น้ำ
    all_elements_present = set(elements.values())
    if "ไฟ" in all_elements_present and "น้ำ" in all_elements_present:
        divergences.append("⚡ **สภาวะน้ำปะทะไฟ (Fire & Water Conflict):** ชะตามีทั้งขั้วพลังไฟ (ความกระตือรือร้น ใจร้อน) และน้ำ (อารมณ์ความรู้สึก ความลื่นไหล) ประชันกัน บ่อยครั้งทำให้เกิดการตัดสินใจที่ใช้อารมณ์ปะทะกับเหตุผลอย่างรวดเร็ว")
    if "ลม" in all_elements_present and "ดิน" in all_elements_present:
        divergences.append("🌪️ **สภาวะดินขัดแย้งลม (Earth & Air Tension):** พลังลม (ความคิดสร้างสรรค์ ลื่นไหล ความคิดเยอะ) ปะทะกับดิน (ความต้องการความมั่นคง จับต้องได้) ส่งผลให้บางช่วงมีความคิดโปรเจกต์มหาศาลแต่ยังลงมือทำให้เป็นจริงได้ยาก")

    if not divergences:
        divergences.append("✅ **พลังงานชะตาราบเรียบ:** ไม่พบจุดขัดแย้งรุนแรงระหว่างธาตุคู่ศัตรูในแผนภูมิชะตาทั้ง 4 ระบบ")

    # ═══════════════════════════════════════════
    # FINAL SYNTHESIZED PERSONA (สรุปตัวตนที่แท้จริง)
    # ═══════════════════════════════════════════
    # สรุปโครงสร้างตามหลัก Synthesis: เพิ่มส่วนที่ร่วม ปรับส่วนที่ต่าง
    synthesized_persona = ""
    if dominant_elem == "ดิน":
        synthesized_persona = "คุณคือ **'แผ่นดินใหญ่ผู้พิทักษ์ความมั่นคง (The Guardian)'** เป็นคนหนักแน่น ไว้ใจได้สูง มีระบบระเบียบในชีวิต วางแผนระยะยาวได้ดีเยี่ยม"
    elif dominant_elem == "ไฟ":
        synthesized_persona = "คุณคือ **'ผู้นำผู้ปลุกพลังแสงสว่าง (The Visionary Leader)'** เต็มไปด้วยแรงขับเคลื่อนสร้างสรรค์ กล้าหาญ มุ่งมั่นสร้างการเปลี่ยนแปลงอย่างเด็ดเดี่ยว"
    elif dominant_elem == "น้ำ":
        synthesized_persona = "คุณคือ **'สายน้ำแห่งปัญญาและเมตตาธรรม (The Intuitive Healer)'** ลึกซึ้ง มีความเข้าอกเข้าใจผู้คนสูง มีลางสังหรณ์แม่นยำ ปรับตัวเก่งเลิศ"
    elif dominant_elem == "ลม":
        synthesized_persona = "คุณคือ **'นักปรัชญาและผู้นำข่าวสารปัญญา (The Communicator)'** สมองปราดเปรียว รักอิสระ คอนเนคชันดีเลิศ มีไอเดียแปลกใหม่นำสมัยอยู่เสมอ"

    # สร้างเลย์เอาต์รายงานสังเคราะห์เปรียบเทียบดวงชะตา
    report = f"""# 🔮 รายงานการวิเคราะห์สังเคราะห์บูรณาการดวงชะตา 4 ศาสตร์ (Astro-Synthesis Portrait)
## ข้อมูลพื้นฐาน: วันเวลาเกิด {dt.day}/{dt.month}/{dt.year+543} เวลา {dt.hour:02d}:{dt.minute:02d} น.

---

### 📊 ตารางเปรียบเทียบพิกัดชะตาเชิงระบบ (Systems Matrix)

| ศาสตร์พยากรณ์ | พิกัดดวงดาวสำคัญ (Placement) | ธาตุเจ้าเรือนประจำศาสตร์ (Active Element) | มิติบทบาทพยากรณ์ชะตาชีวิต |
|:---|:---|:---|:---|
| **จีน (BaZi)** | ดิถีประจำตัว: **ดาว {dm_stem}** | ธาตุ{elements['bazi']} ({dm_desc}) | วิเคราะห์เสาหลักชีวิต 5 ธาตุกำเนิดและสัตว์ปีเกิดปี {animal_year} |
| **อินเดีย (Jyotish)** | ลัคนากรรมลิขิต: **ราศี{vedic_rashi}** | ธาตุ{elements['vedic']} (ดาวจันทร์ใน {vedic_nakshatra}) | วิเคราะห์หนทางแห่งกรรมเก่าและกระแสเวลาเสวยอายุของดวงดาว |
| **สากล (Western)** | ลัคนาพฤติกรรม: **ราศี{west_rashi}** | ธาตุ{elements['western']} (อาทิตย์ใน ราศี{west_sun_rashi}) | วิเคราะห์จิตวิทยาบุคลิกภาพ พฤติกรรมศาสตร์ภายนอกและอีโก้ (Persona) |
| **ไทย (Thai Astro)** | ทักษาประจำวันเกิด: **วัน{thai_day}** | ธาตุ{elements['thai']} | วิเคราะห์สิริมงคล การพิจารณาอักษรกาลกิณี และการวางฤกษ์มงคล |

---

### 🧠 มิติจุดร่วมและจุดต่างเชิงโครงสร้าง (Convergences & Divergences)

#### 🤝 1. จุดร่วมที่ส่งเสริมกัน (Convergences - เพิ่มกำลังด้านดี)
{"\n".join([f"- {c}" for c in convergences])}

#### ⚡ 2. จุดต่างที่ต้องปรับสมดุล (Divergences - ส่วนที่ต้องปรับแต่งเพื่อลดแรงต้าน)
{"\n".join([f"- {d}" for d in divergences])}

---

### 👑 บทสรุปโครงสร้างตัวตนสังเคราะห์ที่แท้จริง (Synthesized Core Identity)
จากการสกัด วิเคราะห์ และคานอำนาจเปรียบเทียบของดวงดาวและธาตุทั้ง 4 ระบบหลัก:

> ### **{synthesized_persona}**

*   **แนวทางการพัฒนาชีวิตบูรณาการ (Integrated Action Plan):**
    1.  **จุดส่งเสริมสูงสุด (Leverage):** นำพลังของธาตุเด่นร่วมคือ **ธาตุ{dominant_elem}** มาขับเคลื่อนเป้าหมายในสายอาชีพและการสร้างความมั่งคั่งหลัก
    2.  **จุดป้องกันความผันผวน (Mitigate):** ตระหนักรู้สภาวะความขัดแย้งของธาตุที่เป็นปฏิปักษ์ในชะตาเพื่อลดทอนอารมณ์ชั่ววูบและการตัดสินใจที่ผิดพลาด
    3.  **มงคลชีวิตนำทาง (Auspicious Guide):** หลีกเลี่ยงอักษรกาลกิณีประจำวันเกิด **วัน{thai_day}** และมุ่งเสริมสร้างพลังบารมีผ่านการค้ำจุนของดาวจันทร์ในกลุ่มดาวฤกษ์ **{vedic_nakshatra}** เพื่อประคองชะตาชีวิตให้ก้าวหน้ามั่นคงถาวรครับ
"""
    return report

def get_tools() -> Dict:
    return {
        "synthesis": lambda args: {"result": generate_synthesis_report(args.get("birth_datetime", ""))}
    }
