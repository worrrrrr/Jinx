# tools/jyotish.py — โหราศาสตร์อินเดีย (Vedic / Jyotish) เวอร์ชันวิเคราะห์เจาะลึกทางสถิติจิตวิทยา

"""
Jyotish (Vedic Astrology) — ใช้ sidereal zodiac (Lahiri ayanamsa)
คำนวณ Rashi, Graha, Nakshatra, Lagna, Bhava, Dasha, Yoga
พร้อมระบบร้อยเรียงคำพยากรณ์สังเคราะห์เป้าหมายชะตาชีวิตรายบุคคล (Vedic Spiritual Reading)

Dependencies:
    - pyswisseph (ตำแหน่งดาวจริง)
"""

import datetime
import re
import math
import os
from typing import Dict, List, Tuple, Optional, Any

try:
    import swisseph as swe
    _SWE_AVAILABLE = True
except ImportError:
    _SWE_AVAILABLE = False
    swe = None


# ═══════════════════════════════════════════
# CONSTANTS & METADATA
# ═══════════════════════════════════════════

RASHI = [
    ("Mesha",     "เมษ",   "🐏", "Aries",     "ไฟ",   "เคลื่อนที่", "อังคาร"),
    ("Vrishabha", "พฤษภ",  "🐂", "Taurus",    "ดิน",   "มั่นคง",    "ศุกร์"),
    ("Mithuna",   "เมถุน",  "👫", "Gemini",    "ลม",    "ปรับตัว",   "พุธ"),
    ("Karka",     "กรกฎ",  "🦀", "Cancer",    "น้ำ",   "อารมณ์",    "จันทร์"),
    ("Simha",     "สิงห์",  "🦁", "Leo",       "ไฟ",    "คงที่",     "อาทิตย์"),
    ("Kanya",     "กันย์",  "👩", "Virgo",     "ดิน",    "วิเคราะห์", "พุธ"),
    ("Tula",      "ตุลย์",  "⚖️", "Libra",     "ลม",    "สมดุล",    "ศุกร์"),
    ("Vrishchika","พิจิก",  "🦂", "Scorpio",   "น้ำ",    "เข้มข้น",  "อังคาร"),
    ("Dhanus",    "ธนู",   "🏹", "Sagittarius","ไฟ",    "ขยายตัว",  "พฤหัส"),
    ("Makara",    "มังกร",  "🐐", "Capricorn", "ดิน",    "ทะเยอทะยาน","เสาร์"),
    ("Kumbha",    "กุมภ์",  "🏺", "Aquarius",  "ลม",    "อิสระ",    "เสาร์"),
    ("Meena",     "มีน",   "🐟", "Pisces",    "น้ำ",    "จินตนาการ","พฤหัส"),
]

GRAHA = [
    (swe.SUN,     "Sun",     "อาทิตย์", "☀️", "วิญญาณ อำนาจ เกียรติยศ", "Atma (Soul)"),
    (swe.MOON,    "Moon",    "จันทร์",  "🌙", "จิตใจ อารมณ์ ความรู้สึก", "Mana (Mind)"),
    (swe.MARS,    "Mars",    "อังคาร", "🔥", "พลัง ขับเคลื่อน ความกล้า", "Prana (Energy)"),
    (swe.MERCURY, "Mercury", "พุธ",    "💬", "ปัญญา การเจรจา การค้า", "Budhi (Intellect)"),
    (swe.JUPITER, "Jupiter", "พฤหัส",  "⭐", "โชคลาภ ปัญญา ความเจริญ", "Guru (Wisdom)"),
    (swe.VENUS,   "Venus",   "ศุกร์",  "💖", "ความรัก ความสุข ศิลปะ", "Shukra (Devotion)"),
    (swe.SATURN,  "Saturn",  "เสาร์",  "⛰️", "กรรม อุปสรรค อดกลั้น", "Kharma (Discipline)"),
    (swe.MEAN_NODE, "Rahu", "ราหู",   "🐉", "มายา ความทะยาน อยากเด่น", "Maya (Desire)"),
    (swe.MEAN_APOG, "Ketu", "เกตุ",   "🌀", "ธรรมะ ลี้ลับ ความหลุดพ้น", "Moksha (Liberation)"),
]
GRAHA_IDS = [g[0] for g in GRAHA]

NAKSHATRA = [
    ("Ashwini",    "อัศวินี",  "🍎", "Ashwini Kumaras", "Ket"),
    ("Bharani",    "ภรณี",    "👤", "Yama",            "Ven"),
    ("Krittika",   "กฤติกา",  "🔪", "Agni",            "Sun"),
    ("Rohini",     "โรหิณี",  "🚗", "Brahma",          "Moon"),
    ("Mrigashira", "มฤคศิระ", "🦌", "Soma",            "Mars"),
    ("Ardra",      "อาทรา",   "💎", "Rudra",           "Rah"),
    ("Punarvasu",  "ปุนัพสุ",  "🏹", "Aditi",           "Jup"),
    ("Pushya",      "ปุชย",   "🌸", "Brihaspati",      "Sat"),
    ("Ashlesha",   "อาศเลษา", "🐍", "Sesha",            "Mer"),
    ("Magha",      "มฆะ",     "👑", "Pitris",           "Ket"),
    ("Purva Phalguni", "บุรพาฬผลคุณี", "🛏️", "Bhaga",     "Ven"),
    ("Uttara Phalguni", "อุตตราฬผลคุณี", "🛌", "Aryaman", "Sun"),
    ("Hasta",      "หัสต",    "✋", "Savitr",           "Moon"),
    ("Chitra",     "จิตรา",   "💍", "Tvashtar",         "Mars"),
    ("Swati",      "สวาตี",   "🌿", "Vayu",             "Rah"),
    ("Vishakha",   "วิศาขา",  "🌳", "Indra-Agni",       "Jup"),
    ("Anuradha",   "อนุราธา", "🌟", "Mitra",            "Sat"),
    ("Jyeshtha",   "เชษฐา",   "☂️", "Indra",            "Mer"),
    ("Mula",       "มูละ",    "🌱", "Nirriti",          "Ket"),
    ("Purva Ashadha","บุรพาษาฒ","🌊", "Apas",            "Ven"),
    ("Uttara Ashadha","อุตตราษาฒ","🐘", "Vishvadevas",   "Sun"),
    ("Shravana",   "ศรวณะ",   "👂", "Vishnu",           "Moon"),
    ("Dhanishtha", "ธนิษฐา",  "🥁", "Vasus",            "Mars"),
    ("Shatabhisha","ศตพิสมัย", "💊", "Varuna",           "Rah"),
    ("Purva Bhadrapada","บุรพภัทรบท","🔥", "Aja Ekapada","Jup"),
    ("Uttara Bhadrapada","อุตตรภัทรบท","🐍", "Ahir Budhyana","Sat"),
    ("Revati",     "เรวดี",   "🐟", "Pushan",           "Mer"),
]

DASHA_YEARS = {
    "Ket": 7, "Ven": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rah": 18, "Jup": 16, "Sat": 19, "Mer": 17,
}
DASHA_ORDER = ["Ket", "Ven", "Sun", "Moon", "Mars", "Rah", "Jup", "Sat", "Mer"]

BHAVA = [
    (1,  "ตน",    "Tanu",    "ตัวตน บุคลิกภาพ รูปร่าง และวาสนาชีวิตหลัก"),
    (2,  "ทรัพย์", "Dhana",  "การเงิน ทรัพย์สมบัติ ครอบครัว และคำพูดพารวย"),
    (3,  "ความเพียร", "Sahaja", "ความกล้าหาญ การเจรจาต่อรอง สังคม และพี่น้อง"),
    (4,  "รากฐาน", "Bandhu", "บ้าน ที่ดิน ยานพาหนะ มารดา และความสุขสงบในใจ"),
    (5,  "สร้างสรรค์", "Putra",  "บุตร ปัญญาเก่า ความก้าวหน้า การเรียนรู้ และความรัก"),
    (6,  "อุปสรรค", "Ripu",   "หนี้สิน โรคภัย ศัตรู และการสู้ชีวิตต่อสู้"),
    (7,  "ปฏิสัมพันธ์", "Yuvati", "คู่ครอง หุ้นส่วน คู่ค้า และการครองเรือนทางโลก"),
    (8,  "ความลับ/มรณะ", "Randhra","การสูญเสีย วิกฤติ มรดก และศาสตร์เร้นลับจิตวิญญาณ"),
    (9,  "ศุภะ/ปัญญา", "Dharma", "ความเจริญ โชคลาภ ความดีงามเก่า บิดา และคุณธรรม"),
    (10, "กรรมภาพ", "Karma",  "หน้าที่การงาน อาชีพ เกียรติยศชื่อเสียง และการกระทำ"),
    (11, "โชคลาภ", "Labha",  "ผลกำไร ผลประโยชน์ มิตรภาพ และความสมหวัง"),
    (12, "วิมุติ/สูญเสีย", "Vyaya",  "การใช้จ่าย ต่างแดน การสละละวาง และการหลุดพ้น"),
]


# ═══════════════════════════════════════════
# CORE CALCULATORS (Swiss Ephemeris Support)
# ═══════════════════════════════════════════

def _jd_from_dt(dt: datetime.datetime) -> float:
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)


def _get_sidereal_planets(jd: float) -> Dict:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    planets = {}
    for pid in GRAHA_IDS:
        try:
            flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
            res = swe.calc_ut(jd, pid, flags)
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


def _get_lagna(jd: float, lat: float = 13.75, lon: float = 100.5) -> Dict:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    try:
        hsys = b"P"
        flags = swe.FLG_SIDEREAL
        result = swe.houses_ex(jd, lat, lon, hsys, flags)
        houses = result[0]
        asc_lon = result[1][0]
        sign = int(asc_lon / 30)
        deg = asc_lon - sign * 30
        return {"lon": asc_lon, "sign": sign, "deg": deg, "mc": houses[9]}
    except Exception:
        return {"lon": 0, "sign": 0, "deg": 0, "mc": None}


def _get_nakshatra(lon: float) -> Dict:
    step = 13 * 60 + 20  # 13°20' in minutes
    pos_min = lon * 60
    idx = int(pos_min / step) % 27
    pada = int((pos_min % step) / (step / 4)) + 1
    n = NAKSHATRA[idx]
    return {
        "idx": idx, "sanskrit": n[0], "thai": n[1],
        "symbol": n[2], "deity": n[3], "lord_abbr": n[4],
        "pada": min(pada, 4),
    }


def _get_dasha(moon_nakshatra_idx: int, birth_year: int) -> List[Dict]:
    nk = NAKSHATRA[moon_nakshatra_idx]
    lord_abbr = nk[4]
    start_idx = DASHA_ORDER.index(lord_abbr)
    
    dashes = []
    current_age = 0
    dasha_names = {"Ket": "เกตุ", "Ven": "ศุกร์", "Sun": "อาทิตย์", "Moon": "จันทร์", "Mars": "อังคาร", "Rah": "ราหู", "Jup": "พฤหัส", "Sat": "เสาร์", "Mer": "พุธ"}
    dasha_emojis = {"Ket": "🌀", "Ven": "💖", "Sun": "☀️", "Moon": "🌙", "Mars": "🔥", "Rah": "🐉", "Jup": "⭐", "Sat": "⛰️", "Mer": "💬"}
    
    for i in range(12):
        idx = (start_idx + i) % 9
        planet = DASHA_ORDER[idx]
        years = DASHA_YEARS[planet]
        start = birth_year + current_age
        end = start + years
        dashes.append({
            "planet": dasha_names.get(planet, planet),
            "emoji": dasha_emojis.get(planet, ""),
            "years": years,
            "age_start": current_age,
            "year_start": start,
            "year_end": end,
        })
        current_age += years
        if current_age > 100:
            break
    return dashes


def _get_yogas(planets: Dict, lagna: Dict) -> List[str]:
    yogas = []
    lagna_sign = lagna["sign"]
    
    def _in_sign(pid, s_idx):
        return pid in planets and planets[pid]["sign"] == s_idx
        
    if _in_sign(swe.JUPITER, lagna_sign) or _in_sign(swe.JUPITER, (lagna_sign + 6) % 12):
        yogas.append("Gaja Kesari Yoga — จันทร์ร่วมพฤหัสเด่น บ่งชี้ถึงสติปัญญาที่ฉลาดเฉลียว มีเกียรติยศ และโชคลาภที่เกื้อหนุนอย่างถูกจังหวะเวลา")
        
    if swe.SUN in planets and swe.SATURN in planets:
        if abs(planets[swe.SUN]["lon"] - planets[swe.SATURN]["lon"]) < 10:
            yogas.append("Surya-Shani Yoga — อาทิตย์และเสาร์ร่วมสถิต บ่งชี้ถึงวิถีชีวิตที่ต้องตรากตรำ ทนทาน และใช้ฝีมือแก้ไขปัญหาอย่างอดทนพิเศษ")
            
    if swe.VENUS in planets and planets[swe.VENUS]["sign"] in [1, 6, 11]:  
        yogas.append("Malavya Yoga — ดาวศุกร์เปล่งพลังเด่นตระการตา บ่งบอกถึงความเป็นผู้มีรสนิยมล้ำเลิศ สุนทรีภาพเด่น และมีโชคลาภเสน่ห์ติดตัว")

    if not yogas:
        yogas.append("ไม่มีเกณฑ์ดาวใหญ่โยกพิเศษชะตา — มิติชีวิตจะดำเนินไปตามกำลังการส่องสว่างของเจ้าเรือนภพหลักอย่างสอดคล้อง")
        
    return yogas[:4]


def _get_sign_lord_idx(sign_idx: int) -> int:
    """ส่งคืนรหัส Graha ID สำหรับดาวเจ้าเรือนประจำราศี"""
    mapping = {
        0: swe.MARS, 1: swe.VENUS, 2: swe.MERCURY, 3: swe.MOON,
        4: swe.SUN, 5: swe.MERCURY, 6: swe.VENUS, 7: swe.MARS,
        8: swe.JUPITER, 9: swe.SATURN, 10: swe.SATURN, 11: swe.JUPITER,
    }
    return mapping.get(sign_idx, swe.SUN)


# ═══════════════════════════════════════════
# DEEP INTERPRETATION ENGINES (ลอจิกแปลดวงเจาะลึก)
# ═══════════════════════════════════════════

LAGNA_DESCS = {
    0: ("ราศีเมษ (Mesha)", "อังคาร", "คนลุย ๆ ใจร้อน รักอิสระ ไม่ชอบอยู่ใต้คำสั่งใคร รักพวกพ้องและกล้าชนกับปัญหาอย่างตรงไปตรงมา"),
    1: ("ราศีพฤษภ (Vrishabha)", "ศุกร์", "คนหนักแน่น รักความสงบ ชื่นชอบความสะดวกสบาย รสนิยมดี และให้คุณค่าความมั่นคงทางวัตถุสูงสุด"),
    2: ("ราศีเมถุน (Mithuna)", "พุธ", "คนสมองปราดเปรียว เรียนรู้เร็ว เจรจาวาทศิลป์เป็นเลิศ ปรับตัวเก่งเหมือนน้ำและโอบอ้อมอารี"),
    3: ("ราศีกรกฎ (Karka)", "จันทร์", "คนเมตตา อ่อนไหว รักครอบครัว ใช้ลางสังหรณ์นำทางชีวิตและมีหัวใจเป็นที่พักพิงให้ผู้ตกทุกข์ได้ยาก"),
    4: ("ราศีสิงห์ (Simha)", "อาทิตย์", "คนสง่างาม รักเกียรติยศศักดิ์ศรีดั่งราชสีห์ รักษาสัจจะ ใจกว้างใหญ่ และเกลียดการโดนบังคับไร้เหตุผล"),
    5: ("ราศีกันย์ (Kanya)", "พุธ", "คนประณีต ละเอียดละออ มีระเบียบวินัย ชื่นชอบความสมบูรณ์แบบ (Perfectionist) และเป็นนักสแกนจับผิดแก้ไขปัญหาเก่ง"),
    6: ("ราศีตุลย์ (Tula)", "ศุกร์", "คนรักความยุติธรรม ประนีประนอมสูง มีศิลปะและวาทศิลป์ในการประสานสิบทิศ ชื่นชอบงานดีไซน์สวยงาม"),
    7: ("ราศีพิจิก (Vrishchika)", "อังคาร", "คนลึกลับ เก็บความรู้สึกเก่ง หยั่งรู้ทันคน มีความทรหดอดทนระดับวิกฤตที่ล้มแล้วจะลุกขึ้นแกร่งกว่าเดิม"),
    8: ("ราศีธนู (Dhanus)", "พฤหัส", "คนมองโลกในแง่ดี รักอิสระและการสืบค้นสัจธรรม ฝักใฝ่การศึกษาหาปัญญา จิตใจดีงามและชอบความยุติธรรม"),
    9: ("ราศีมังกร (Makara)", "เสาร์", "คนทรหด มุ่งมั่น มีวินัย แบกภาระหน่วงหนักเพื่อวางรากฐานชีวิต ค่อย ๆ เติบโตอย่างยั่งยืนไม่มีส้มหล่น"),
    10: ("ราศีกุมภ์ (Kumbha)", "เสาร์", "คนคิดแปลกใหม่ มองการณ์ไกลล้ำสมัย อุดมการณ์สูง รักมนุษยธรรมและต้องการช่วยเหลือผู้คนในวงกว้าง"),
    11: ("ราศีมีน (Meena)", "พฤหัส", "คนจินตนาการสูง เมตตา อ่อนโยน ขี้สงสารคน และมีสัมผัสพิเศษลี้ลับที่คอยคุ้มครองภัยเสมอ"),
}

NAKSHATRA_DESCS = {
    "Ashwini": "เด่นความรวดเร็ว ว่องไวในการตัดสินใจแก้ไขปัญหาเฉพาะหน้า เป็นสายลุยที่ชอบงานบุกเบิกริเริ่ม",
    "Bharani": "แบกความกดดันและภาระสูง ทรหดอดกลั้นอารมณ์ มีรสนิยมทางศิลปะที่ลึกซึ้งเฉพาะทาง",
    "Krittika": "เฉียบคม รักษาสัจจะ มีบารมีและรัศมีที่ทำให้คนเกรงใจ แต่อารมณ์ร้อนรุนแรงเมื่อถึงจุดเดือด",
    "Rohini": "มีเสน่ห์เมตตามหานิยมดึงดูดทรัพย์ ดนตรี รื่นรมย์ ได้รับความเอ็นดูเกื้อหนุนจากผู้ใหญ่อย่างโดดเด่น",
    "Mrigashira": "กระหายปัญญาความรู้ ชอบแสวงหาความจริง ไม่ยอมหยุดนิ่งและปรับตัวเข้ากับกระแสสังคมได้เร็ว",
    "Ardra": "เผชิญพายุรีเซ็ตเปลี่ยนชีวิตขนานใหญ่เพื่อเข้าสัจธรรมโลก เหมาะกับงานเทคโนโลยีล้ำสมัย",
    "Punarvasu": "ล้มแล้วตั้งหลักชีวิตใหม่ได้เสมอ ได้รับการฟื้นฟูเยียวยาจิตใจและดึงโชคลาภกลับมาได้ทุกคราว",
    "Pushya": "มีกินมีใช้ไม่ขัดสน ฝักใฝ่ปัญญาธรรม ได้รับความรักและการค้ำจุนจากสิ่งศักดิ์สิทธิ์และเจ้านาย",
    "Ashlesha": "ฉลาดลึกซึ้ง มีความละเอียดในการวางแผน รักพวกพ้อง ยอดเยี่ยมในเชิงชั้นธุรกิจและการรักษาความลับ",
    "Magha": "รักศักดิ์ศรี อดีต บรรพบุรุษ มีความทะนงใจที่จะสร้างผลงานอันเป็นที่ยอมรับและสืบทอดครอบครัว",
    "Purva Phalguni": "มีเทสต์ดี รักศิลปะและดนตรี ละเมียดละไมในความสุนทรี และมีศิลปะทางคำพูดที่คนรักคนหลง",
    "Uttara Phalguni": "จิตใจกตัญญู ซื่อสัตย์ รักมิตรภาพรอบข้าง และรักการช่วยเหลือผู้อื่นโดยไม่หวังผลกำไร",
    "Hasta": "ฝีมือประณีต ชำนาญเชิงทฤษฎีและปฏิบัติ พึ่งพาหยาดเหงื่อแรงกายสร้างฐานะสำเร็จงดงาม",
    "Chitra": "มีพรสวรรค์สร้างสรรค์ มีศิลปะการออกแบบตกแต่งสิ่งสวยงาม และดึงดูดแต้มโชคลาภกะทันหัน",
    "Swati": "รักอิสระเหนือสิ่งอื่นใด ปราดเปรียว ยืดหยุ่น และมีไหวพริบยอดเยี่ยมในการทำมาหากินในโลกกว้าง",
    "Vishakha": "ความมุ่งมั่นทะเยอทะยานระดับสูงมาก ตั้งเป้าหมายชีวิตไว้ไกลและมีแรงบุกบั่นที่จะพุ่งชนความสำเร็จโดยไม่ท้อถอย",
    "Anuradha": "มีบารมีและสายสัมพันธ์คอนเนคชันที่เหนียวแน่น อบอุ่น และมักแคล้วคลาดจากวิกฤติได้ด้วยโชคช่วย",
    "Jyeshtha": "มีความเป็นพี่ใหญ่หรือผู้นำที่เด็ดเดี่ยว ทะนงในศักดิ์ศรีปัญญา และพร้อมปกป้องดูแลผู้ที่อ่อนแอกว่า",
    "Mula": "รากแก้วแห่งปัญญา มักต้องผ่านมรสุมหรือการรีเซ็ตชีวิตขนานใหญ่ก่อนจะเบิกเนตรเข้าใจสัจธรรมสงบมั่นคง",
    "Purva Ashadha": "ทรหดต่อสู้ ยอดเยี่ยมในการบุกฟื้นฟูสถานการณ์วิกฤติ และมีสัญชาตญาณมีชัยชนะเหนือคู่แข่ง",
    "Uttara Ashadha": "มุ่งมั่นสร้างความเจริญมั่นคงในโครงสร้างภาพรวม ได้รับความไว้วางใจให้คุมภารกิจหรือทีมสำคัญ",
    "Shravana": "ใฝ่รู้ รอบคอบ ชื่นชอบการรับฟังและตกผลึกข้อมูลข่าวสารอย่างเป็นระบบเพื่อใช้ตัดสินใจอย่างแม่นยำ",
    "Dhanishtha": "เก่งด้านจังหวะ ดนตรี และการจัดการทรัพย์สมบัติ มีโชคลาภงอกเงยไหลเวียนจากเพื่อนฝูง",
    "Shatabhisha": "ลึกลับ มีเซนส์แก้ปัญหาเก่งกาจและรักษาโรคได้ดี เหมาะกับสายงานวิทยาศาสตร์ ไอที หรือแพทย์เยียวยาคน",
    "Purva Bhadrapada": "มีความเชื่อมั่นสูง รักความยุติธรรม กล้าปฏิวัติล้มกฎเกณฑ์ล้าสมัย มีความคิดเฉพาะทางและรักในความยุติธรรมขั้นสูง",
    "Uttara Bhadrapada": "จิตใจสงบ ลุ่มลึก ฝักใฝ่ในธรรมะหรือศาสตร์ลี้ลับชั้นสูง มีสมาธิดีและสามารถถอดวางกิเลสทางโลกเพื่อค้นหาความสงบที่แท้จริงได้ง่าย",
    "Revati": "เปี่ยมเมตตา มีโชคดีจากการประสานงานทางไกล ได้รับความอบอุ่นและรักใคร่เอ็นดูจากสิ่งแวดล้อม",
}

DASHA_INTERPRETATIONS = {
    "อาทิตย์": "เกียรติยศ เกียรติยศ และรากฐานชีวิต เป็นช่วงวัยที่คุณจะโฟกัสเรื่องความก้าวหน้า หน้าที่การงาน การสร้างเครดิตความน่าเชื่อถือ และความพยายามสร้างความมั่นคงเชิงโครงสร้างให้ตนเองอย่างยิ่งยวด",
    "จันทร์": "อารมณ์ความรู้สึก จิตวิญญาณ และการคืนกลับสู่ความสงบ คุณจะเริ่มผ่อนคลายความบ้าพลังทางโลกหันมาสนใจความสุขที่แท้จริงในจิตใต้สำนึก สภาพแวดล้อม ความรู้สึกในครอบครัว และมีเกณฑ์เดินทางไกลต่างแดนหรือฝักใฝ่เรื่องธรรมะสัจธรรมชีวิต",
    "อังคาร": "การบุกเบิก การลงแรงเหน็ดเหนื่อย และกิจกรรมใหม่ ๆ คุณจะมีความกระตือรือร้นและแรงพลังในการริเริ่มโปรเจกต์ ค้าขาย ลุยทำงานหนักเพื่อเอาชนะคู่แข่ง มีลาภผลเงินทองหลั่งไหลตามกำลังหยาดเหงื่อแรงกาย",
    "ราหู": "กิเลส มายา และความทะยานอยากได้อยากมี เป็นวัยวัดใจที่จะขับเคลื่อนคุณไปหาเม็ดเงินก้อนโต การเสี่ยงโชค หรือขยายการค้าระหว่างประเทศรวดเร็วแบบก้าวกระโดด แต่ต้องควบคุมกิเลสและระวังภัยหักหลังจากความโลภให้ดี",
    "พฤหัส": "สติปัญญา ศีลธรรม และผู้ใหญ่อุปถัมภ์ เป็นจังหวะชีวิตที่ยอดเยี่ยมที่สุดในดวงชะตา คุณจะได้รับการสนับสนุนผลักดันให้รุ่งโรจน์ ได้รับการศึกษา ความมั่งคั่งที่สุภาพสง่างาม และดึงดูดผู้มีศีลธรรมเข้ามานำทางชีวิต",
    "เสาร์": "กรรมสะสาง อุปสรรค และภาระความรับผิดชอบที่หลีกเลี่ยงไม่ได้ คุณจะได้รับมอบหมายงานที่ยากที่สุดในชีวิต ต้องแบกรับปัญหาขององค์กรหรือครอบครัว ต้องอดทนอดกลั้นฟันฝ่า แต่สุดท้ายจะแปลงเป็นทรัพย์สินอสังหาริมทรัพย์ถาวรในตอนบั้นปลาย",
    "พุธ": "ปัญญา วาทศิลป์ และการพาณิชย์เจรจา สมองและปากจะพารวยแบบก้าวกระโดด เหมาะกับงานขาย นายหน้า ธุรกิจเครือข่าย หรือติดต่อสื่อสาร มีความสนุกสนานและได้รับความช่วยเหลือรอบตัว",
    "เกตุ": "วิมุติ ปล่อยวาง และจิตวิญญาณลึกลับ คุณจะเกิดสภาวะเบื่อหน่ายความวุ่นวายใจทางโลก สนใจเรื่องศาสตร์ลี้ลับ พลังงาน สุขภาพทางเลือก หรือการปฏิบัติธรรม มีสัมผัสพิเศษแม่นยำและได้รับการปกป้องรอดพ้นจากภัยวิกฤตอย่างอัศจรรย์",
    "ศุกร์": "เงินทองไหลมาเทมา ความรัก ความสวยงาม และศิลปะความรื่นรมย์ เป็นบทชีวิตสีชมพูที่แวดล้อมด้วยความสะดวกสบายทางโลก มีโชคดีในด้านทรัพย์สมบัติและดึงดูดความรักที่สมบูรณ์แบบเข้ามาพยุงชะตาชีวิต",
}


def _fmt_date(dt: datetime.datetime) -> str:
    th_months = {1:'มกราคม',2:'กุมภาพันธ์',3:'มีนาคม',4:'เมษายน',5:'พฤษภาคม',6:'มิถุนายน',
                 7:'กรกฎาคม',8:'สิงหาคม',9:'กันยายน',10:'ตุลาคม',11:'พฤศจิกายน',12:'ธันวาคม'}
    return f"{dt.day} {th_months[dt.month]} พ.ศ. {dt.year+543} ({dt.hour:02d}:{dt.minute:02d} น.)"


def _bhavas_from_lagna(planets: Dict, lagna: Dict) -> Dict[int, List[int]]:
    """จัดตำแหน่งดวงดาวเคราะห์ลงสู่โครงสร้าง 12 ภพเรือนชะตา"""
    lagna_sign = lagna["sign"]
    bhavas = {i: [] for i in range(1, 13)}
    for pid, data in planets.items():
        house = (data["sign"] - lagna_sign + 12) % 12 + 1
        graha_idx = GRAHA_IDS.index(pid)
        bhavas[house].append(graha_idx)
    return bhavas


def _bhavas_detailed_synthesis(bhavas: Dict, lagna: Dict, planets: Dict) -> List[str]:
    """คำนวณและแปลความหมายดวงดาวประจำภพเรือนชะตาเด่นที่มีคุณลักษณะกรรมลิขิต"""
    readings = []
    lagna_sign = lagna["sign"]
    
    # คำนวณหาดาวประจำตัว (Lagna Lord) และตรวจสอบตำแหน่งเรือน
    lagna_lord_id = _get_sign_lord_idx(lagna_sign)
    lord_data = planets.get(lagna_lord_id)
    if lord_data:
        lord_house = (lord_data["sign"] - lagna_sign + 12) % 12 + 1
        g_name = next((g[2] for g in GRAHA if g[0] == lagna_lord_id), "ดาวประจำตัว")
        b_info = BHAVA[lord_house-1]
        readings.append(
            f"  • **ดาวประจำตัวหลักของคุณ (ดาว{g_name}) วิ่งไปสถิตภพที่ {lord_house} ({b_info[1]}):** "
            f"บ่งบอกว่าเจตจำนงเสรี พละกำลัง และพลังในการสร้างชีวิตของคุณทั้งหมด จะถูกเหวี่ยงไปโฟกัสเพื่อบรรลุความสำเร็จในเรื่องของ **{b_info[3]}** เป็นเป้าหมายสูงสุด"
        )

    # วนลูปหาดาวดวงอื่น ๆ สถิตภพหลัก
    for h in range(1, 13):
        b = BHAVA[h-1]
        grahas_in = bhavas.get(h, [])
        if not grahas_in:
            continue
            
        for g_idx in grahas_in:
            g_id = GRAHA_IDS[g_idx]
            if g_id == lagna_lord_id:
                continue
                
            g_name = GRAHA[g_idx][2]
            g_desc = GRAHA[g_idx][4]
            
            if h == 1:
                readings.append(f"  • **ดาว{g_name}สถิตภพเรือนชะตาที่ 1 (ตนุ - ตัวตน):** ส่งผลให้บุคลิกภาพ รัศมีกาย และจิตวิญญาณของคุณจะถูกชี้นำด้วยพลังงานของดวงดาว บ่งชี้ว่าคุณจะมีคุณลักษณะของ{g_desc}แสดงออกชัดเจน")
            elif h == 2:
                readings.append(f"  • **ดาว{g_name}สถิตภพเรือนชะตาที่ 2 (ธนะ - การเงิน):** บ่งชี้ว่ากระแสการเงินและทรัพย์สมบัติของคุณจะได้รับอิทธิพลจากพลังงานของดวงดาว บ่งชี้ว่าช่องทางทำเงินจะมาจากการใช้{g_desc}")
            elif h == 4:
                readings.append(f"  • **ดาว{g_name}สถิตภพเรือนชะตาที่ 4 (พันธุ - รากฐานความสุข):** บ้าน ที่ดิน ยานพาหนะ และมารดาของคุณจะเกี่ยวข้องกับพลังงานดวงดาว บ่งบอกว่าความสุขในครอบครัวจะมาจากความสุนทรีย์และ{g_desc}")
            elif h == 7:
                readings.append(f"  • **ดาว{g_name}สถิตภพเรือนชะตาที่ 7 (ปัตนิ - คู่ครอง/หุ้นส่วน):** วิถีการเจรจา หุ้นส่วน หรือคู่ครองของคุณจะถูกดาวเคราะห์ดวงนี้ควบคุม มักได้คู่ที่มีนิสัยหรือทำงานเกี่ยวกับโครงสร้างพลังของ{g_desc}")
            elif h == 9:
                readings.append(f"  • **ดาว{g_name}สถิตภพเรือนชะตาที่ 9 (ศุภะ - โชคลาภความดีงาม):** ได้รับแต้มบุญและผู้ใหญ่อุปถัมภ์ที่เด่นชัดเป็นพิเศษ พลังของ{g_desc}จะทำหน้าที่นำทางชี้แนะและคุ้มครองชีวิตคุณให้อยู่รอดปลอดภัย")
            elif h == 10:
                readings.append(f"  • **ดาว{g_name}สถิตภพเรือนชะตาที่ 10 (กรรมะ - การงาน/อาชีพ):** หน้าที่การงานและเกียรติยศชื่อเสียงของคุณถูกกำหนดชะตาไว้ด้วยดาว{g_name} บ่งบอกว่าอาชีพที่เจริญรุ่งเรืองจะต้องอ้างอิงกับพลังของ{g_desc}")
            elif h in [6, 8, 12]:
                readings.append(f"  • **ดาว{g_name}สถิตภพเรือนทุสถานะที่ {h} ({b[1]}):** ดวงดาวแห่ง{g_name}ต้องเผชิญเกณฑ์ท้าทาย บ่งชี้ถึงกรรมเก่าที่จะต้องแก้ไข แนะนำให้ใช้ความอดทนและการปล่อยวางเพื่อประคองชีวิตให้ผ่านพ้น")
            else:
                readings.append(f"  • **ดาว{g_name}สถิตภพเรือนชะตาที่ {h} ({b[1]}):** ส่งเสริมคุณลักษณะเรื่อง **{b[3]}** อย่างสอดคล้อง")
                
    return readings


# ═══════════════════════════════════════════
# REPORT FORMATTER
# ═══════════════════════════════════════════

def _format_reading(dt: datetime.datetime, planets: Dict, lagna: Dict, nakshatra: Dict, dashes: List[Dict], bhavas: Dict, yogas: List[str]) -> str:
    lines = []
    r = RASHI[lagna["sign"]]
    
    # 1. HEADER
    lines.append(f"## 🕉️ Jyotish (อินเดีย) — ผลพยากรณ์โหราศาสตร์ชะตาชีวิตเจาะลึกเชิงลึก")
    lines.append(f"# 🕉️ รายงานวิเคราะห์เจาะลึกดวงชะตากรรมลิขิต (Vedic Jyotish Deep Reading)")
    lines.append(f"*(ระบบจัดสมผุสพิกัดดวงดาวดาราศาสตร์ Sidereal Zodiac - Lahiri Ayanamsa)*")
    lines.append("")
    lines.append(f"**⏰ วันเกิดคำนวณ:** {_fmt_date(dt)}")
    lines.append("")
    lines.append("> *\"ชะตาชีวิตไม่ได้ขึ้นอยู่กับการเรียงตัวของดวงดาวเพียงอย่างเดียว แต่ขึ้นอยู่กับการตระหนักรู้ในพลังงานของดวงดาวเหล่านั้นและน้อมนำมาใช้พัฒนาสติปัญญาตนเองเพื่อการชดใช้กรรมและเข้าสู่วิมุติหลุดพ้น\"*")
    lines.append("")
    
    # 2. SECTION I: ตนเองคือใคร? (Lagna & Nakshatra Synthesis)
    lines.append("## Ⅰ. สรุปภาพรวม \"เราเป็นคนอย่างไร?\" (Core Personality Synthesis)")
    lines.append("")
    lines.append("โครงสร้างในดวงชะตาของคุณ บ่งชี้ถึงสภาวะ **'ความย้อนแย้งและซับซ้อนในตนเองสูงมาก'** ระหว่างภาพรวมภายนอกที่ผู้อื่นมองเห็น และสภาวะอารมณ์ความรู้สึกส่วนตัวลึก ๆ ภายในใจ ดังนี้ครับ:")
    lines.append("")
    
    lines.append(f"1. **บุคลิกภาพเปลือกนอกที่คุณแสดงออก (ลัคนาราศีเกิด):** ลัคนาสถิตใน {r[2]} **ราศี{r[1]} ({r[0]})** ธาตุ{r[4]} | เกณฑ์สภาวะ: {r[5]}")
    lines.append(f"   - **คุณลักษณะภายนอก:** {LAGNA_DESCS.get(lagna['sign'], ('', '', ''))[2]}")
    lines.append(f"2. **โลกส่วนตัวทางอารมณ์และจิตใต้สำนึก (จันทร์สถิตกลุ่มดาวนักษัตร):** สถิตในกลุ่มดาวจันทร์ลำดับที่ {nakshatra['idx']+1} **{nakshatra['sanskrit']} ({nakshatra['thai']})** {nakshatra['symbol']} | Pada {nakshatra['pada']}/4 ครองดาวเจ้าเรือน: ดาว{nakshatra['lord_abbr']}")
    lines.append(f"   - **คุณลักษณะภายในใจ:** {NAKSHATRA_DESCS.get(nakshatra['sanskrit'], '')}")
    lines.append("")
    lines.append(f"**💡 บทสรุปตัวตนสะท้อนกลับ:** ชะตาชีวิตของคุณเปรียบดั่ง **'นักสู้ผู้มีจิตวิญญาณนักปราชญ์ซ่อนอยู่ภายใน'** เปลือกนอกคนจะมองเห็นคุณเป็นคนมุ่งมั่น แกร่ง และใจร้อนรักอิสระ แต่เมื่อใดที่คุณได้กลับมาอยู่กับตัวเอง จิตวิญญาณภายในใจจะกลับกลายเป็นผู้อ่อนไหว ช่างสังเกต ปรารถนาความสงบ และมักตื่นตัวในการสืบค้นสัจธรรมชีวิตอย่างน่าอัศจรรย์ใจครับ")
    lines.append("")
    
    # 3. SECTION II: อะไรที่ส่งผลให้เราเป็นแบบนี้? (Vedic Bhava Analysis)
    lines.append("---")
    lines.append("## Ⅱ. วิเคราะห์ปัจจัยชะตาชีวิต \"อะไรที่ส่งผลให้เราเป็นเช่นนี้?\" (Vedic Bhava Synthesis)")
    lines.append("")
    lines.append("ตามแผนผังตำแหน่งดาวเคราะห์ประชิดลัคนาหลัก (D-1 Rasi Chart) พิกัดการสถิตของดวงดาวในบ้านเกิดแต่ละภพ (Bhavas) ได้สร้างแรงดึงดูดและกรรมลิขิตที่สอดคล้องกับพฤติกรรมของคุณดังนี้ครับ:")
    lines.append("")
    
    detailed_bhavas = _bhavas_detailed_synthesis(bhavas, lagna, planets)
    for reading in detailed_bhavas:
        lines.append(reading)
    lines.append("")
    
    # 4. SECTION III: ส่งผลอย่างไรต่อชีวิตในปัจจุบัน? (Vimshottari Dasha Dynamic)
    lines.append("---")
    lines.append("## Ⅲ. ทางเดินเวลา \"ส่งผลอย่างไรต่อชีวิตในปัจจุบันและอนาคต?\" (Active Dasha Timeline)")
    lines.append("")
    
    current_year = datetime.datetime.now().year
    current_age = current_year - dt.year
    active_dasha = None
    for d in dashes:
        if d["year_start"] <= current_year <= d["year_end"]:
            active_dasha = d
            break
            
    if active_dasha:
        dasha_desc = DASHA_INTERPRETATIONS.get(active_dasha["planet"], "พลังงานดวงดาวคุมธาตุชะตาชีวิตตามลำดับ")
        lines.append(f"📌 **สถานะดวงชะตาปัจจุบันใน พ.ศ. {current_year+543} (อายุ {current_age} ปี):**")
        lines.append(f"คุณกำลังก้าวเข้าสู่บทเรียนชีวิตหลักภายใต้ **'ดาว{active_dasha['planet']} เสวยอายุอย่างเต็มกำลัง'** (ช่วงปี พ.ศ. {active_dasha['year_start']+543} - {active_dasha['year_end']+543})")
        lines.append(f"- **ทิศทางที่ส่งผลต่อชีวิตช่วงนี้:** {dasha_desc}")
        lines.append("")
        
    lines.append("### 🗓️ ตารางลำดับบทบาทกาลเวลาของชีวิตดวงชะตาคุณ (Vimshottari Dasha):")
    for d in dashes[:8]:
        is_active = "👉 *[วัยปัจจุบัน]*" if d["year_start"] <= current_year <= d["year_end"] else ""
        lines.append(f"- {d['emoji']} **ดาว{d['planet']}เสวยอายุ ({d['years']} ปี):** ช่วงอายุ {d['age_start']} - {d['age_start'] + d['years']} ปี (พ.ศ. {d['year_start'] + 543} - {d['year_end'] + 543}) {is_active}")
    lines.append("")
    
    # 5. SECTION IV: YOGA & KARMA
    lines.append("---")
    lines.append("## Ⅳ. ปรากฏการณ์เกณฑ์พิเศษดวงดาว (Vedic Yoga)")
    lines.append("")
    lines.append("ในโครงสร้างดวงกำเนิดของคุณ ปรากฏกลุ่มเกณฑ์พิเศษดวงดาว (Yoga) ที่ส่งสัญญาณเด่นชัดออกมาดังนี้:")
    lines.append("")
    for y in yogas:
        lines.append(f"- {y}")
    lines.append("")
    
    # 6. SUMMARY
    lines.append("---")
    lines.append("## 📝 บทสรุปและแนวทางการพัฒนาชีวิต")
    lines.append("")
    lines.append(f"ดวงชะตาชิ้นนี้มีเป้าหมายสูงสุดคือการสร้างสมดุลระหว่างไฟภายนอกและน้ำภายในใจ แนะนำให้น้อมนำคุณลักษณะ **'ความกล้าหาญเด็ดเดี่ยวบุกเบิกราศีเกิด'** มาขับเคลื่อนเป้าหมาย และใช้ความสงบนิ่ง มีวินัยของดาวเสาร์เรือนการงานมาประคับประคอง ความสุขและความมั่งคั่งที่ยั่งยืนจะปรากฏขึ้นอย่างมั่นคงเหนือกาลเวลาแน่นอนครับ")
    lines.append("")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════
# TABLE GENERATOR
# ═══════════════════════════════════════════

def _make_table(planets, lagna, nakshatra, bhavas):
    rows = []
    for i, pid in enumerate(GRAHA_IDS):
        if pid not in planets:
            continue
        p = planets[pid]
        g = GRAHA[i]
        r = RASHI[p["sign"]]
        house = (p["sign"] - lagna["sign"] + 12) % 12 + 1
        rows.append([g[3], g[2], r[2]+r[0], f"{p['deg']:.2f}°", str(house), g[4]])
    return {
        "title": "Jyotish Rasi Chart Table",
        "columns": ["", "Graha", "Rashi", "องศา", "House", "Karakatwa"],
        "rows": rows,
        "nakshatra": nakshatra,
        "lagna": {"rashi": RASHI[lagna["sign"]][0], "deg": f"{lagna['deg']:.2f}°"},
    }


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
                if y > 2500:
                    y -= 543
                h, mi = 12, 0
                tm = re.search(r"(\d{1,2})[.:](\d{1,2})", text)
                if tm:
                    h, mi = map(int, tm.groups())
                return datetime.datetime(y, num, d, h, mi)
            except (ValueError, IndexError):
                pass
    return None


def jyotish_handler(action: str, inp: str, entities: list) -> dict:
    """
    วิเคราะห์คำนวณและพยากรณ์ดวงชะตาชีวิตตามหลักโหราศาสตร์อินเดียโบราณ (Vedic Astrology)
    """
    if not _SWE_AVAILABLE:
        return {
            "status": "fail", 
            "message": "Security Alert: ไม่สามารถเรียกใช้งาน Swiss Ephemeris ไลบรารีได้ในระบบปัจจุบัน"
        }

    dt = _parse_datetime(inp)
    if dt is None:
        return {
            "status": "fail", 
            "message": "ไม่สามารถระบุวันเกิดและเวลาตกฟากของดวงชะตาได้ กรุณาระบุในรูปแบบสากล เช่น 20/8/1992 16:49 น."
        }

    try:
        jd = _jd_from_dt(dt)
        planets = _get_sidereal_planets(jd)
        lagna = _get_lagna(jd)

        # 🔗 เรียกใช้งานตัวช่วยจัดเรือนดาวประจำภพจากลัคนา
        bhavas = _bhavas_from_lagna(planets, lagna)

        moon_lon = planets.get(swe.MOON, {}).get("lon", 0)
        nakshatra = _get_nakshatra(moon_lon)

        birth_year = dt.year
        dashes = _get_dasha(nakshatra["idx"], birth_year)
        yogas = _get_yogas(planets, lagna)

        # ประมวลผลบทสรุปพยากรณ์แบบไดนามิกระดับสูงสุด
        reading = _format_reading(dt, planets, lagna, nakshatra, dashes, bhavas, yogas)
        table = _make_table(planets, lagna, nakshatra, bhavas)

        return {
            "status": "success",
            "result": reading,
            "direct_response": True,  # บังคับพิมพ์มาร์กดาวน์พยากรณ์เชิงวิเคราะห์โดยตรง
            "table": table,
        }

    except Exception as e:
        return {
            "status": "fail",
            "message": f"กระบวนการพยากรณ์ทางเทคนิคเกิดข้อผิดพลาด: {type(e).__name__} - {str(e)}",
        }


# ═══════════════════════════════════════════
# TOOL REGISTRATION COUPLING
# ═══════════════════════════════════════════

def get_tools() -> Dict:
    """ส่งคืนเครื่องมือสำหรับการลงทะเบียนระบบวิเคราะห์ของ ExecutionEngine"""
    return {
        "jyotish": jyotish_handler,
        "vedic": jyotish_handler,
        "ดูดวงอินเดีย": jyotish_handler,
    }