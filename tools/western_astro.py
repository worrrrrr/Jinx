# tools/western_astro.py — โหราศาสตร์สากล (Western Astrology) เวอร์ชันสังเคราะห์จิตวิทยารายบุคคล

"""
Western Tropical Astrology — ใช้ tropical zodiac (ไม่มี ayanamsa)
คำนวณ Sun Sign, Moon Sign, Rising, Planets in Signs, Houses, Aspects
พร้อมเครื่องยนต์สังเคราะห์บทวิเคราะห์เชิงลึกตามหลักจิตวิทยาของคาร์ล ยุง (Carl Jung's Persona & Shadow)

Dependencies:
    - pyswisseph (ตำแหน่งดาวจริง)
"""

import datetime
import re
import math
from typing import Dict, List, Optional, Tuple, Any

try:
    import swisseph as swe
    _SWE_AVAILABLE = True
except ImportError:
    _SWE_AVAILABLE = False
    swe = None


# ═══════════════════════════════════════════
# CONSTANTS & METADATA
# ═══════════════════════════════════════════

SIGNS = [
    ("Aries",       "เมษ",     "🐏", "ไฟ",  "Cardinal (แม่ธาตุ - ผู้นำและการริเริ่ม)",   "Mars"),
    ("Taurus",      "พฤษภ",    "🐂", "ดิน",  "Fixed (รักษาธาตุ - ความมั่นคงยั่งยืน)",       "Venus"),
    ("Gemini",      "เมถุน",    "👫", "ลม",   "Mutable (ปลายธาตุ - ความยืดหยุ่นและปรับตัว)",     "Mercury"),
    ("Cancer",      "กรกฎ",    "🦀", "น้ำ",   "Cardinal (แม่ธาตุ - ผู้นำและการริเริ่ม)",   "Moon"),
    ("Leo",         "สิงห์",    "🦁", "ไฟ",  "Fixed (รักษาธาตุ - ความมั่นคงยั่งยืน)",       "Sun"),
    ("Virgo",       "กันย์",    "👩", "ดิน",  "Mutable (ปลายธาตุ - ความยืดหยุ่นและปรับตัว)",     "Mercury"),
    ("Libra",       "ตุลย์",    "⚖️", "ลม",   "Cardinal (แม่ธาตุ - ผู้นำและการริเริ่ม)",   "Venus"),
    ("Scorpio",     "พิจิก",    "🦂", "น้ำ",   "Fixed (รักษาธาตุ - ความมั่นคงยั่งยืน)",       "Pluto"),
    ("Sagittarius", "ธนู",     "🏹", "ไฟ",  "Mutable (ปลายธาตุ - ความยืดหยุ่นและปรับตัว)",     "Jupiter"),
    ("Capricorn",   "มังกร",    "🐐", "ดิน",  "Cardinal (แม่ธาตุ - ผู้นำและการริเริ่ม)",   "Saturn"),
    ("Aquarius",    "กุมภ์",    "🏺", "ลม",   "Fixed (รักษาธาตุ - ความมั่นคงยั่งยืน)",       "Uranus"),
    ("Pisces",      "มีน",     "🐟", "น้ำ",   "Mutable (ปลายธาตุ - ความยืดหยุ่นและปรับตัว)",     "Neptune"),
]
SIGN_NAMES = [s[0] for s in SIGNS]

PLANETS = [
    (swe.SUN,     "Sun",      "อาทิตย์", "☀️",  "ตัวตน อีโก้ และเจตจำนงสำนึกหลัก"),
    (swe.MOON,    "Moon",     "จันทร์",  "🌙",  "จิตใต้สำนึก อารมณ์ และความต้องการทางใจส่วนลึก"),
    (swe.MERCURY, "Mercury",  "พุธ",    "💬",  "กระบวนการคิด การสื่อสาร และสติปัญญา"),
    (swe.VENUS,   "Venus",    "ศุกร์",   "💖",  "ความรัก รสนิยม ค่านิยม และแรงดึงดูดเสน่หา"),
    (swe.MARS,    "Mars",     "อังคาร", "🔥",  "พลังขับเคลื่อน ความปรารถนา และการลงมือทำ"),
    (swe.JUPITER, "Jupiter",  "พฤหัส",  "⭐",  "โชคลาภ การขยายตัว โอกาส และจริยธรรมปัญญา"),
    (swe.SATURN,  "Saturn",   "เสาร์",   "⛰️",  "บทเรียนชีวิต ความอดทน วินัย และความรับผิดชอบ"),
    (swe.URANUS,  "Uranus",   "ยูเรนัส", "⚡",  "ความแปลกใหม่ นวัตกรรม และการเปลี่ยนแปลงฉับพลัน"),
    (swe.NEPTUNE, "Neptune",  "เนปจูน", "🌊",  "จินตนาการ จิตวิญญาณภาพ และความว่างเปล่า"),
    (swe.PLUTO,   "Pluto",    "พลูโต",  "👻",  "การทำลายล้างเพื่อเกิดใหม่ พลังอำนาจ และจิตวิญญาณ"),
]
PLANET_IDS = [p[0] for p in PLANETS]

HOUSES = [
    (1,  "ตน",      "Self",     "ตัวตน บุคลิกภาพ รูปลักษณ์ และหน้ากากแรกทางสังคม (Persona)"),
    (2,  "ทรัพย์",   "Money",    "การหาเงิน ทรัพย์สิน ความมั่นคง และสิ่งที่คุณให้คุณค่า"),
    (3,  "สื่อสาร",  "Communication", "กระบวนการคิด สังคมคนใกล้ชิด การเรียนรู้ระยะสั้น"),
    (4,  "รากฐาน",   "Home",     "ครอบครัว พลังรากเหง้า ที่อยู่อาศัย และพื้นที่ส่วนตัวปลอดภัย"),
    (5,  "สร้างสรรค์","Creativity","ความรัก ศิลปะ ความสนุกสนาน การลงทุน และเด็กน้อยภายในใจ"),
    (6,  "สุขภาพ",   "Health",   "งานประจำ กิจวัตรประจำวัน สุขภาพ และจิตใจการบริการ"),
    (7,  "คู่ครอง",   "Partnership","ความสัมพันธ์ระยะยาว คู่ครอง หุ้นส่วนธุรกิจ และเงาสะท้อนทางสังคม"),
    (8,  "เปลี่ยน",  "Transformation","การสูญเสียครั้งใหญ่ เซ็กส์ ความลึกลับ และมรดกที่เกิดจากการสูญเสีย"),
    (9,  "ปรัชญา",  "Philosophy","ความรู้ชั้นสูง ปรัชญา ธรรมะ การต่างแดน และการเดินทางไกล"),
    (10, "อาชีพ",    "Career",   "อาชีพ เป้าหมายชีวิตสูงสุด ชื่อเสียง และความสำเร็จในที่สาธารณะ"),
    (11, "สังคม",    "Friends",  "ความปรารถนา มิตรสหาย กลุ่มสังคม และอุดมการณ์ร่วม"),
    (12, "วิมุติ",   "Unconscious","จิตใต้สำนึกส่วนลึก ศัตรูที่มองไม่เห็น การสละ และเรื่องราวลึกลับ"),
]

ASPECTS = [
    (0,   "Conjunction", "ประชิด", "0°",   "ผสานกำลังงานเป็นหนึ่งเดียวกันอย่างรุนแรง"),
    (30,  "Sextile",     "กึ่งสัมพันธ์", "30°",  "โอกาสที่ดี การสนับสนุนและการเกื้อกูลอ่อนๆ"),
    (60,  "Sextile",     "กึ่งสัมพันธ์", "60°",  "โอกาสในการเจรจา ช่องทางที่ดี และความกลมกลืน"),
    (90,  "Square",      "ขัดแย้งมุมฉาก","90°",  "ความตึงเครียด อุปสรรค และการขัดแย้งเพื่อกระตุ้นให้เติบโต"),
    (120, "Trine",       "ส่งเสริมตรีโกณ", "120°", "พรสวรรค์ตามธรรมชาติ พลังงานไหลลื่นสมดุลสูงสุด"),
    (180, "Opposition",  "ตรงข้ามประชันกัน","180°", "การเผชิญหน้า ขัดแย้งเพื่อหาจุดสมดุลระหว่างกัน"),
]

ORB = {0: 8, 60: 6, 90: 6, 120: 6, 180: 8}


# ═══════════════════════════════════════════
# CORE CALCULATORS (Vedic Bug Solved!)
# ═══════════════════════════════════════════

def _jd_from_dt(dt: datetime.datetime) -> float:
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)


def _get_planet_positions(jd: float) -> Dict:
    planets = {}
    for pid in PLANET_IDS:
        try:
            res = swe.calc_ut(jd, pid, swe.FLG_SPEED)
            lon, lat, dist, speed = res[0][:4]
            sign = int(lon / 30)
            deg = lon - sign * 30
            planets[pid] = {
                "lon": lon, "lat": lat, "dist": dist, "speed": speed,
                "sign": sign, "deg": deg,
            }
        except Exception:
            continue
    return planets


def _get_ascendant(jd: float, lat: float = 13.75, lon: float = 100.5) -> Dict:
    """ Rising Sign (Ascendant) — พิกัดสากลแบบ Tropical แท้ร้อยเปอร์เซ็นต์ (แก้ไขบั๊กดาวอินเดีย) """
    try:
        hsys = b"P"  # Placidus House System
        # 💡 ปรับเปลี่ยนจาก swe.FLG_SIDEREAL เป็น 0 เพื่อให้ระบบประมวลพิกัดแบบสากลแท้ (Tropical) ไม่ย้อนรอยองศา
        flags = 0  
        result = swe.houses_ex(jd, lat, lon, hsys, flags)
        houses = result[0]
        asc_lon = result[1][0]
        sign = int(asc_lon / 30)
        deg = asc_lon - sign * 30
        return {"lon": asc_lon, "sign": sign, "deg": deg, "mc": houses[9]}
    except Exception:
        return {"lon": 0, "sign": 0, "deg": 0, "mc": None}


def _get_aspects(planets: Dict) -> List[Dict]:
    aspects = []
    pids = list(planets.keys())
    for i in range(len(pids)):
        for j in range(i + 1, len(pids)):
            pid1, pid2 = pids[i], pids[j]
            lon1 = planets[pid1]["lon"]
            lon2 = planets[pid2]["lon"]
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            for asp_deg, asp_name, asp_th, _, _ in ASPECTS:
                orb = ORB.get(asp_deg, 6)
                if abs(diff - asp_deg) <= orb:
                    aspects.append({
                        "p1": pid1, "p2": pid2,
                        "lon1": lon1, "lon2": lon2,
                        "diff_deg": diff,
                        "aspect": asp_name,
                        "aspect_th": asp_th,
                        "deg": asp_deg,
                        "orb": abs(diff - asp_deg),
                    })
                    break
    return aspects


def _houses_from_asc(planets, asc):
    asc_sign = asc["sign"]
    h = {i: [] for i in range(1, 13)}
    for pid, data in planets.items():
        house = (data["sign"] - asc_sign + 12) % 12 + 1
        h[house].append(pid)
    return h


def _get_sign_ruler(sign_idx: int) -> int:
    mapping = {0: swe.MARS, 1: swe.VENUS, 2: swe.MERCURY, 3: swe.MOON,
               4: swe.SUN, 5: swe.MERCURY, 6: swe.VENUS, 7: swe.PLUTO,
               8: swe.JUPITER, 9: swe.SATURN, 10: swe.URANUS, 11: swe.NEPTUNE}
    return mapping.get(sign_idx, swe.SUN)


# ═══════════════════════════════════════════
# PSYCHOLOGICAL TRANSLATORS (สัญญานพยากรณ์เชิงลึก)
# ═══════════════════════════════════════════

SUN_SIGN_DESCS = {
    0: "ผู้บุกเบิกและแรงพลังชีวิตอันบริสุทธิ์ ขับเคลื่อนเป้าหมายชีวิตด้วยการกระทำอันรวดเร็ว เด็ดขาด",
    1: "ผู้แสวงหาเสถียรภาพและความมั่นคงทางโลก ใจเย็น อดทน มุ่งเน้นผลลัพธ์ในเชิงปฏิบัติและพึ่งพาได้",
    2: "ผู้เชื่อมต่อข่าวสารและปัญญาอันรวดเร็ว มีทักษะการเจรจา ค้นคว้า มีความลื่นไหลสูงและปรับตัวไว",
    3: "ผู้อุปถัมภ์ที่อบอุ่นและเปี่ยมด้วยเมตตา มีพลังในการปกป้องพวกพ้อง รักครอบครัว และสัญชาตญาณสูง",
    4: "ราชาผู้ยิ่งใหญ่ที่มีรัศมีและเกียรติยศชื่อเสียงนำทาง มีหัวใจที่ใจกว้าง ทะนงในศักดิ์ศรีและความถูกต้อง",
    5: "นักคิดวิเคราะห์ผู้ประณีต ชื่นชอบความเรียบร้อยและระบบความสมบูรณ์แบบ รักการบริการช่วยเหลือผู้อื่น",
    6: "สัญญลักษณ์แห่งความสมดุลและความสัมพันธ์อันงดงาม รักความยุติธรรม ประสานสิบทิศและรักศิลปะ",
    7: "พลังชีวิตอันลึกลับและแรงดึงดูดที่ยิ่งล้มจะยิ่งแกร่ง รักความเข้มข้นทางอารมณ์ และเป็นนักปฏิรูปชะตา",
    8: "ผู้แสวงหาความจริงสูงสุดและเสรีภาพชีวิต ฝักใฝ่การเดินทาง ปรัชญา และโชคลาภที่ขยายตัวตลอดเวลา",
    9: "ผู้ทรหดปีนป่ายหน้าผาชีวิตด้วยวินัยและความรับผิดชอบ อดกลั้น เก่งกาจในการสร้างฐานะระยะยาว",
    10: "ผู้พิทักษ์อุดมการณ์และมนุษยธรรมเพื่อสังคมส่วนรวม รักในความแตกต่าง นวัตกรรม และมีโลกส่วนตัวสูง",
    11: "ศิลปินผู้จินตนาการกว้างไกล มีเมตตา อารมณ์ละเอียดอ่อน และเข้าอกเข้าใจผู้อื่นเหนือระดับปกติ",
}

MOON_SIGN_DESCS = {
    0: "มีความต้องการทางอารมณ์ที่รวดเร็ว ตรงไปตรงมา กระตือรือร้นและพร้อมปกป้องผลประโยชน์ทันทีเมื่อถูกกระทบ",
    1: "ต้องการความเสถียรและความนิ่งทางใจอย่างยิ่งยวด มีความอารมณ์เย็นและรักสงบอย่างลึกซึ้ง",
    2: "ต้องการสื่อสาร ระบายความคิด ชื่นชอบการเจรจาเพื่อผ่อนคลายสภาวะตึงเครียดทางอารมณ์",
    3: "โหยหาพื้นที่ปลอดภัยที่อบอุ่น อ่อนไหวง่าย ขี้กังวล และต้องการการดูแลเอาใจใส่จากคนรักสูง",
    4: "ต้องการความเคารพยกย่อง อบอุ่น ใจกว้าง และภาคภูมิใจในตัวตนของคนใกล้ชิดในกลุ่มสังคม",
    5: "วิเคราะห์และแยกแยะความรู้สึกในใจ ขี้กังวล และมักแสดงความรักผ่านการเข้าไปช่วยเหลือดูแลอย่างเป็นระบบ",
    6: "เกลียดความขัดแย้งเป็นที่สุด ต้องการสภาวะแวดล้อมที่กลมกลืนและประนีประนอมทุกปัญหา",
    7: "อารมณ์เข้มข้น รักแรงเกลียดแรง มีความหวงแหนและเก็บซ่อนความรู้สึกลึกซึ้งที่ยากจะให้ใครล่วงรู้",
    8: "ต้องการอิสรภาพทางใจสูง เกลียดการถูกควบคุม บีบคั้น และชอบขยายขอบเขตความรู้ความสุขตลอดเวลา",
    9: "ควบคุมความรู้สึกเก่งเยี่ยม อดทน แต่อมทุกข์หรือวิตกกังวลสะสมลึกๆ เรื่องหน้าที่การงาน",
    10: "รักสันโดษ มีความรู้สึกร่วมกับอุดมการณ์ทางสังคม และต้องการรักษาพื้นที่ส่วนตัวอย่างชัดเจน",
    11: "อ่อนไหวอย่างที่สุด รับรู้อารมณ์คนรอบข้างได้ไวราวกับฟองน้ำ มีความเห็นใจและจินตนาการไร้ขอบเขต",
}

RISING_SIGN_DESCS = {
    0: "ลัคนาเมษ (Aries Rising) — มีบุคลิกภาพภายนอกที่กระฉับกระเฉง ทำงานรวดเร็ว และมีออร่าของนักริเริ่มที่พร้อมวิ่งเข้าชนเป้าหมายในทันที",
    1: "ลัคนาพฤษภ (Taurus Rising) — มีบุคลิกภายนอกที่ดูสง่างาม นิ่ง สงบ ดูสุภาพ น่าเชื่อถือ และรักษาระดับท่าทางได้อย่างมั่นคง",
    2: "ลัคนาเมถุน (Gemini Rising) — มีบุคลิกที่ดูคล่องตัว พูดคุยเก่ง ช่างสังเกต ปราดเปรียว และทันต่อข่าวสารบ้านเมืองรอบตัวอย่างยิ่ง",
    3: "ลัคนากรกฎ (Cancer Rising) — มีแววตาและใบหน้าที่อ่อนโยน ใจดี ขี้อายในตอนแรก และมีรัศมีแห่งผู้น่าเชื่อถือที่ปลอดภัย",
    4: "ลัคนาสิงห์ (Leo Rising) — โดดเด่น มีเสน่ห์สะดุดตา มีมาดผู้นำที่ทำให้ตนเองกลายเป็นจุดสนใจของสังคมในทันทีที่ปรากฏตัว",
    5: "ลัคนากันย์ (Virgo Rising) — บุคลิกสุขุม เรียบร้อย สะอาดสะอ้าน วางตัวถูกต้องตามกาลเทศะ และดูรอบคอบในทุกกิริยา",
    6: "ลัคนาตุลย์ (Libra Rising) — มีเสน่ห์ที่กลมกลืน ท่าทางสง่างาม ยิ้มแย้มเข้าหาคนง่าย และรักในการวางตัวให้เป็นที่ประทับใจของผู้คน",
    7: "ลัคนาพิจิก (Scorpio Rising) — แววตาลึกซึ้ง ลึกลับ น่าเกรงขาม วางตัวนิ่งสงบแต่แฝงด้วยความเข้มข้นที่สัมผัสได้จากภายนอก",
    8: "ลัคนาธนู (Sagittarius Rising) — เปิดเผย ตรงไปตรงมา อารมณ์ดี ร่าเริง และดูเป็นมิตรไร้พิษภัยกับคนรอบข้างโดยธรรมชาติ",
    9: "ลัคนามังกร (Capricorn Rising) — บุคลิกที่ดูเป็นผู้ใหญ่ สุขุม เอาจริงเอาจัง มีความภูมิฐานน่าเกรงขาม และวางท่าระเบียบวินัยดีเยี่ยม",
    10: "ลัคนากุมภ์ (Aquarius Rising) — วางตัวเป็นตัวของตัวเองอย่างเด่นชัด มีรสนิยมที่แตกต่าง แตกแยกจากกรอบทั่วไปของสังคมและรักอิสระ",
    11: "ลัคนามีน (Pisces Rising) — แววตาอบอุ่นราวกับอยู่ในโลกแห่งความฝัน มีความอ่อนโยน เมตตา และมีเสน่ห์ทางศิลปะที่น่าค้นหา",
}


# ═══════════════════════════════════════════
# REPORT GENERATOR
# ═══════════════════════════════════════════

def _fmt_date(dt: datetime.datetime) -> str:
    th_months = {1:'มกราคม',2:'กุมภาพันธ์',3:'มีนาคม',4:'เมษายน',5:'พฤษภาคม',6:'มิถุนายน',
                 7:'กรกฎาคม',8:'สิงหาคม',9:'กันยายน',10:'ตุลาคม',11:'พฤศจิกายน',12:'ธันวาคม'}
    return f"{dt.day} {th_months[dt.month]} พ.ศ. {dt.year+543} ({dt.hour:02d}:{dt.minute:02d} น.)"


def _fmt_reading(dt: datetime.datetime, planets: Dict, asc: Dict, aspects: List[Dict], houses: Dict) -> str:
    lines = []

    sun_sig = planets.get(swe.SUN, {}).get("sign", 0)
    moon_sig = planets.get(swe.MOON, {}).get("sign", 0)

    # ── Ⅰ. HEADER ──
    lines.append("🌟 พยากรณ์โหราศาสตร์สากลเชิงลึก (Western Tropical Astrology Deep Reading)")
    lines.append(f"*(จัดสมผุสพารามิเตอร์ดวงดาวพิกัดปฏิทินสากลระบบ Tropical - Placidus House System)*")
    lines.append("")
    lines.append(f"**⏰ วันเกิดคำนวณ:** {_fmt_date(dt)}")
    lines.append("")
    lines.append("> *\"ดวงชะตาบอกแนวทางของแนวโน้มชีวิต แต่การตระหนักรู้และการใช้เจตจำนงเสรี (Free Will) คือผู้ลิขิตความสำเร็จสูงสุดที่แท้จริง\"*")
    lines.append("")

    # ── Ⅱ. THE BIG THREE SYNTHESIS ──
    lines.append("## Ⅰ. สังเคราะห์กลุ่มดาวสำคัญ \"The Big Three\" (ตัวตน จิตใจ และหน้ากากสังคม)")
    lines.append("")
    lines.append("ในระบบจิตวิทยาโหราศาสตร์สากล กลุ่มดาวบิ๊กทรีเปรียบเสมือนแกนหลักทางจิตใต้สำนึกและพฤติกรรมของคุณ โดยมีการผสานกันดังนี้ครับ:")
    lines.append("")
    
    s = SIGNS[sun_sig]
    lines.append(f"1. **ราศีอาทิตย์ (Sun Sign - อัตตาหลัก):** {s[2]} **ราศี{s[1]} ({s[0]})** | ธาตุ{s[3]}")
    lines.append(f"   - **คุณลักษณะภายในแกนหลัก:** {SUN_SIGN_DESCS.get(sun_sig, '')}")
    
    m = SIGNS[moon_sig]
    lines.append(f"2. **ราศีจันทร์ (Moon Sign - ความรู้สึกภายใน):** {m[2]} **ราศี{m[1]} ({m[0]})** | ธาตุ{m[3]}")
    lines.append(f"   - **ความต้องการลึกๆ ทางอารมณ์:** {MOON_SIGN_DESCS.get(moon_sig, '')}")
    
    a = SIGNS[asc["sign"]]
    lines.append(f"3. **ราศีลัคนา (Rising / Ascendant - หน้ากากสังคม):** {a[2]} **ราศี{a[1]} ({a[0]})** | ธาตุ{a[3]}")
    lines.append(f"   - **ภาพลักษณ์ที่แสดงออกภายนอก:** {RISING_SIGN_DESCS.get(asc['sign'], '')}")
    lines.append("")
    lines.append(f"**💡 บทสรุปตัวตนแบบผสานพลัง:** ชะตาชีวิตของคุณมีแกนหลักของอีโก้เป็นราศี **{s[1]}** ซึ่งแสดงออกภายนอกสังคมผ่านลัคนา **{a[1]}** และมีตัวควบคุมอารมณ์ความนึกคิดส่วนตัวในบ้านหลังสุดท้ายคือราศี **{m[1]}** แนะนำให้ประสานพลังของธาตุเด่นเหล่านี้เข้าด้วยกันเพื่อสลัดภาพความลังเลและก้าวขึ้นสู่ความก้าวหน้าอย่างสมดุล")
    lines.append("")

    # ── Ⅲ. PLANETS & HOUSES ──
    lines.append("---")
    lines.append("## Ⅱ. ตำแหน่งดวงดาวและภพเรือนชะตา (Planetary & House Placements)")
    lines.append("")
    lines.append("ตำแหน่งดาวเคราะห์ประชิดเรือนชะตาสัญญลักษณ์ทางโลก บ่งบอกถึงโฟกัสชีวิตที่เด่นชัดในมิติต่าง ๆ:")
    lines.append("")
    
    for i, pid in enumerate(PLANET_IDS):
        if pid not in planets:
            continue
        p = planets[pid]
        pl = PLANETS[i]
        _s = SIGNS[p["sign"]]
        house = (p["sign"] - asc["sign"] + 12) % 12 + 1
        h_desc = HOUSES[house-1]
        
        # เขียนประโยควิเคราะห์แบบสังเคราะห์เชิงลึก
        if pid == swe.SUN:
            lines.append(f"  • **{pl[3]} ดาวอาทิตย์เสถียรในบ้าน{house} ({h_desc[1]}):** ส่งผลให้เป้าหมายแกนกลาง ความทะเยอทะยาน และเกียรติยศชื่อเสียงของคุณจะส่องสว่างเด่นในเรื่อง **{h_desc[3]}**")
        elif pid == swe.MOON:
            lines.append(f"  • **{pl[3]} ดาวจันทร์เสถียรในบ้าน{house} ({h_desc[1]}):** ส่งผลให้ความมั่นคงปลอดภัยทางอารมณ์ และความสุขในระดับจิตใต้สำนึกของคุณจะผูกพันโดยตรงกับเรื่อง **{h_desc[3]}**")
        elif pid == swe.SATURN:
            lines.append(f"  • **{pl[3]} ดาวเสาร์สถิตในบ้าน{house} ({h_desc[1]}):** บ่งชี้ถึงบทเรียนกรรมและภาระหน้าที่ที่คุณต้องใช้ความอดทน วินัย และระยะเวลาอันยาวนานเพื่อชดใช้แก้ไขในเรื่อง **{h_desc[3]}**")
        else:
            lines.append(f"  • {pl[3]} ดาว**{pl[2]}**สถิตในเรือนชะตาที่ {house} ({h_desc[1]}) เกื้อหนุนเรื่อง **{h_desc[3]}** ด้วยอิทธิพลของ{pl[4]}")
            
    lines.append("")

    # ── Ⅳ. ASPECTS ──
    lines.append("---")
    lines.append("## Ⅲ. กระแสความสัมพันธ์ระหว่างดวงดาว (Planetary Aspects)")
    lines.append("")
    lines.append("มุมสัมพันธ์ระหว่างดวงดาวคือลวดลายที่ร้อยเรียงทัศนคติในจิตวิทยาของคุณให้แสดงผลออกมาเด่นชัดดังนี้ครับ:")
    lines.append("")
    
    if aspects:
        for asp in aspects:
            n1 = next(p[2] for p in PLANETS if p[0] == asp["p1"])
            n2 = next(p[2] for p in PLANETS if p[0] == asp["p2"])
            aspect_desc = next(a[4] for a in ASPECTS if a[1] == asp["aspect"])
            lines.append(f"  • **ดาว{n1} — ทำมุม{asp['aspect_th']} ({asp['aspect']}) กับดาว{n2}:** ส่งสัญญานแรงดึงดูดแบบ **{aspect_desc}** (ค่าความเบี่ยงเบน orb: {asp['orb']:.1f}°)")
    else:
        lines.append("  ไม่ปรากฏความสัมพันธ์ระหว่างดวงดาวใหญ่ที่รุนแรงเฉียบพลันในโครงสร้างดวงกำเนิด")
    lines.append("")

    # ── Ⅴ. ELEMENT BALANCE ──
    lines.append("---")
    lines.append("## Ⅳ. สมดุลธาตุและโครงสร้างทางจิตวิทยา (Element & Modalities Balance)")
    lines.append("")
    
    elements = {"ไฟ": 0, "ดิน": 0, "ลม": 0, "น้ำ": 0}
    for pid, p in planets.items():
        sig = p["sign"]
        elem = SIGNS[sig][3]
        elements[elem] = elements.get(elem, 0) + 1
        
    for elem, cnt in elements.items():
        bar = "🔥" * cnt if elem == "ไฟ" else "⛰️" * cnt if elem == "ดิน" else "💨" * cnt if elem == "ลม" else "🌊" * cnt
        lines.append(f"  - **ธาตุ{elem}:** {bar} ({cnt} พลังดวงดาว)")
        
    dom = max(elements, key=elements.get)
    lines.append("")
    lines.append(f"**🌟 การประเมินธาตุหลักดวงชะตา:** คุณมี **'ธาตุ{dom}'** โดดเด่นทรงพลังสูงสุดในโครงสร้างชะตา บ่งบอกว่าจิตวิทยาหลักของคุณจะสะท้อนคุณลักษณะของ **{_element_desc(dom)}** เป็นหลักในการสร้างเป้าหมายชีวิต")
    lines.append("")

    # ── Ⅵ. SUMMARY ──
    lines.append("---")
    lines.append("## 📝 บทสรุปดวงชะตาสากลสไตล์ Jinx")
    lines.append("")
    lines.append(f"ภาพรวมชะตาชีวิตของคุณมีพลังงานที่น่าทึ่งมากในการริเริ่มสร้างสรรค์ แนะนำให้นำแรงขับของราศี **{s[1]}** มาผสมผสานกับหน้ากากสังคมของลัคนา **{a[1]}** เพื่อใช้โอกาสจากการกระตุ้นโยคะดวงดาวในมุมสัมพันธ์ต่าง ๆ นำพาชีวิตของคุณไปสู่ความมั่นคงและอิสระที่ร่ำรวยทั้งกำลังทรัพย์และจิตวิญญาณอย่างสุภาพครับ")
    lines.append("")

    return "\n".join(lines)


# ═══════════════════════════════════════════
# TABLE GENERATOR
# ═══════════════════════════════════════════

def _make_table(planets, asc, aspects):
    rows = []
    for i, pid in enumerate(PLANET_IDS):
        if pid not in planets:
            continue
        p = planets[pid]
        pl = PLANETS[i]
        s = SIGNS[p["sign"]]
        house = (p["sign"] - asc["sign"] + 12) % 12 + 1
        rows.append([pl[3], pl[2], s[2]+s[0], f"{p['deg']:.2f}°", str(house), pl[4]])
    return {
        "title": "Western Tropical Chart Table",
        "columns": ["", "Planet", "Sign", "องศา", "House", "Meaning"],
        "rows": rows,
        "ascendant": {"sign": SIGNS[asc["sign"]][0], "deg": f"{asc['deg']:.2f}°"},
    }


def _element_desc(elem):
    descs = {
        "ไฟ": "ความปรารถนาอันรุนแรง พลังบุกเบิก การลงมือทำด้วยความกระตือรือร้นและแรงบันดาลใจสร้างสรรค์",
        "ดิน": "ความหนักแน่นสถิตเสถียร การใช้งานได้จริงในทางโลก ความคิดเป็นแบบแผนและการสร้างฐานะที่แตะต้องได้",
        "ลม": "สติปัญญาระดับสูง กระบวนการสื่อสาร วาทศิลป์ สังคม คอนเนคชัน และความยืดหยุ่นทางความคิด",
        "น้ำ": "อารมณ์ความรู้สึกอันลุ่มลึก สัญชาตญาณ หยั่งรู้ เซนส์ลี้ลับ และพละกำลังแห่งความเห็นอกเห็นใจโอบอุ้ม",
    }
    return descs.get(elem, "")


# ═══════════════════════════════════════════
# SYSTEM HANDLER & INTERFACE COUPLING
# ═══════════════════════════════════════════

def _parse_datetime(text: str) -> Optional[datetime.datetime]:
    text = text.strip()
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2})[.:](\d{1,2})", text)
    if m:
        d, mo, y, h, mi = map(int, m.groups())
        return datetime.datetime(y, mo, d, h, mi)
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        d, mo, y = map(int, m.groups())
        return datetime.datetime(y, mo, d, 12, 0)
        
    thai_months = {
        'ม.ค.':1,'ก.พ.':2,'มี.ค.':3,'เม.ย.':4,'พ.ค.':5,'มิ.ย.':6,
        'ก.ค.':7,'ส.ค.':8,'ก.ย.':9,'ต.ค.':10,'พ.ย.':11,'ธ.ค.':12,
        'มกรา':1,'กุมภา':2,'มีนา':3,'เมษา':4,'พฤษภา':5,'มิถุนา':6,
        'กรกฎา':7,'สิงหา':8,'กันยา':9,'ตุลา':10,'พฤศจิกา':11,'ธันวา':12,
    }
    for name, num in thai_months.items():
        if name in text:
            parts = text.split()
            try:
                d = int(parts[0])
                y = int(parts[2]) if len(parts) > 2 else 2024
                if y > 2500: y -= 543
                h, mi = 12, 0
                tm = re.search(r"(\d{1,2})[.:](\d{1,2})", text)
                if tm: h, mi = map(int, tm.groups())
                return datetime.datetime(y, num, d, h, mi)
            except (ValueError, IndexError):
                pass
    return None


def western_astro_handler(action: str, inp: str, entities: list) -> dict:
    """วิเคราะห์คำนวณและพยากรณ์โครงสร้างชะตาสากลตามหลักจิตวิทยาเชิงลึก"""
    if not _SWE_AVAILABLE:
        return {
            "status": "fail", 
            "message": "Security Alert: ไม่สามารถเรียกใช้งาน Swiss Ephemeris ไลบรารีได้ในระบบปฏิบัติการปัจจุบัน"
        }

    dt = _parse_datetime(inp)
    if dt is None:
        return {
            "status": "fail", 
            "message": "ไม่สามารถระบุวันเกิดและเวลาตกฟากได้ กรุณาระบุในรูปแบบสากล เช่น 20/8/1992 16:49 น."
        }

    try:
        jd = _jd_from_dt(dt)
        planets = _get_planet_positions(jd)
        asc = _get_ascendant(jd)
        aspects = _get_aspects(planets)
        houses = _houses_from_asc(planets, asc)

        reading = _fmt_reading(dt, planets, asc, aspects, houses)
        table = _make_table(planets, asc, aspects)

        return {
            "status": "success",
            "result": reading,
            "direct_response": True,  # พ่นเฉพาะ Markdown วิเคราะห์ดวงชะตาสากลเชิงลึกออกมาโดยตรง
            "table": table,
        }

    except Exception as e:
        return {
            "status": "fail",
            "message": f"กระบวนการพยากรณ์ทางเทคนิคเกิดข้อผิดพลาด: {type(e).__name__} - {str(e)}",
        }


def get_tools() -> Dict:
    """ส่งคืนเครื่องมือสำหรับการลงทะเบียนของ ExecutionEngine"""
    return {
        "western": western_astro_handler,
        "western_astro": western_astro_handler,
        "ดูดวงฝรั่ง": western_astro_handler,
    }