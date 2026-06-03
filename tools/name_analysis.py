# tools/name_analysis.py

"""
Module: tools/name_analysis.py
Description: Name & Numerology Analysis Engine (Premium Full Max Edition)
             ระบบคำนวณและพยากรณ์นามศาสตร์ เลขศาสตร์ อายตนะ 6 และทักษาปกรณ์ภาษาไทย
             แบบสังเคราะห์บทความเชิงจิตวิทยาอักษรมงคลขั้นสูง
"""

import re
import os
from typing import Dict, List, Tuple, Optional, Any

# ═══════════════════════════════════════════
# CONSTANTS & DETAILED DICTIONARIES
# ═══════════════════════════════════════════

# ตารางกำลังดาวเลขศาสตร์ไทยที่ได้รับความรับรองว่าคำนวณ วรกฤช=14 / สุนทรธรรมนิติ=51
THAI_NUM_TABLE = {
    'ก': 1, 'ด': 1, 'ถ': 1, 'ท': 1, 'ภ': 1, 'ฤ': 1, 'า': 1, 'อุ': 1, 'ำ': 1, '่': 1, 'ุ': 1,
    'ข': 2, 'ช': 2, 'ง': 2, 'บ': 2, 'ป': 2, 'เ': 2, 'แ': 2, 'ู': 2, '้': 2,
    'ฆ': 3, 'ต': 3, 'ฑ': 3, 'ฒ': 3, 'ฃ': 3, '๋': 3,
    'ค': 4, 'ธ': 4, 'ญ': 4, 'ร': 4, 'ษ': 4, 'ฅ': 4, 'ะ': 4, 'ิ': 4, 'โ': 4, 'ั': 4,
    'ฉ': 5, 'ณ': 5, 'ฌ': 5, 'น': 5, 'ม': 5, 'ห': 5, 'ฎ': 5, 'ฬ': 5, 'ฮ': 5, 'ึ': 5,
    'จ': 6, 'ล': 6, 'ว': 6, 'อ': 6, 'ใ': 6,
    'ซ': 7, 'ศ': 7, 'ส': 7, 'ี': 7, 'ื': 7, '๊': 7,
    'ย': 8, 'พ': 8, 'ฟ': 8, 'ผ': 8, 'ฝ': 8, '็': 8,
    'ฏ': 9, 'ฐ': 9, 'ไ': 9, '์': 9
}

THAI_AYATANA_TABLE = {
    'ก':1,'ข':1,'ค':1,'ฆ':1,'ง':1,
    'จ':2,'ฉ':2,'ช':2,'ซ':2,'ฌ':2,'ญ':2,
    'ฎ':3,'ฏ':3,'ฐ':3,'ฑ':3,'ฒ':3,'ณ':3,
    'ด':4,'ต':4,'ถ':4,'ท':4,'ธ':4,'น':4,
    'บ':5,'ป':5,'ผ':5,'ฝ':5,'พ':5,'ฟ':5,'ภ':5,'ม':5,
    'ย':6,'ร':6,'ล':6,'ว':6,'ฤ':6,
    'ศ':7,'ษ':7,'ส':7,'ห':7,'ฬ':7,'ฮ':7,
    'อ':8,
}

THAI_AYATANA_MEANINGS = {
    1: (
        "ราชา/ราชินี — เปรียบดังราชาหรือราชินีผู้ครองแผ่นดิน มีพลังออร่าแห่งบารมีและความเป็นผู้นำสูงเด่น "
        "เป็นที่เคารพยำเกรงแก่ผู้พบเห็นทั่วไป มักมีคนคอยช่วยเหลือเกื้อกูลและคอยฟังคำสั่งอย่างนอบน้อมดั่งข้าแผ่นดิน "
        "ชีวิตมักได้รับการหนุนนำให้ขึ้นสู่ระดับบริหารหรือจุดสูงสุดของสายงานด้วยสิทธิ์อำนาจเฉียบขาด"
    ),
    2: (
        "มาตา — เปรียบดังเพศแม่ผู้เปี่ยมด้วยความเมตตาและอารมณ์ความอ่อนโยนดึงดูดใจ มีสัญชาตญาณของการโอบอุ้มชูชุบ "
        "และคอยดูแลช่วยเหลือผู้อื่น ใครได้พูดคุยหรือทำงานร่วมด้วยมักจะเกิดความรักใคร่เอ็นดูและคล้อยตามคำเจรจาได้ง่ายมาก "
        "มีดวงนารีอุปถัมภ์หรือผู้เมตตาพยุงชะตาชีวิตอย่างเหนียวแน่น เดินทางไปที่ใดมักไม่เคยขาดแคลนมิตรสหาย"
    ),
    3: (
        "ปิตา — เปรียบดั่งบิดาผู้เด็ดเดี่ยว แข็งแกร่ง และเปี่ยมด้วยวินัยความรับผิดชอบ เป็นคนจริงจัง รักสัจจะ "
        "และมักทำหน้าที่เป็นที่พึ่งพาให้แก่บริวารที่อ่อนแอกว่า มีความทรหดอดทนสูง มีพละกำลังในการก้าวผ่านปัญหาอุปสรรคต่าง ๆ "
        "และฟื้นคืนจากความยากลำบากได้ด้วยเจตจำนงของตนเองอย่างสง่างาม"
    ),
    4: (
        "เจดีย์ — เปรียบดั่งยอดเจดีย์อันสูงส่ง มั่นคง และสว่างไสวด้วยคุณธรรมสมาธิปัญญา เป็นคนฝักใฝ่ในเรื่องศีลธรรม "
        "ความถูกต้อง ชื่นชอบการสะสมวิชาความรู้ ชะตาชีวิตมักได้รับการเลื่อมใสศรัทธาจากมหาชนรอบข้าง มีจิตใจที่สงบเสงี่ยม "
        "และมักทำหน้าที่เป็นที่ปรึกษาหรือผู้นำทางจิตใจที่ผู้คนต่างให้ความไว้วางใจสูงสุด"
    ),
    5: (
        "อุโบสถ — เปรียบดั่งพระอุโบสถอันเป็นสถานที่ศักดิ์สิทธิ์ สงบเย็น และสะอาดบริสุทธิ์ มีจิตใจดีงามเป็นเลิศ "
        "ชอบการทำกุศลหรืองานช่วยเหลือผู้ตกทุกข์ได้ยาก มีดวงชะตาที่แคล้วคลาดปลอดภัยจากภยันตรายร้ายแรงทั้งหลาย "
        "ด้วยอำนาจศีลธรรมและสิ่งศักดิ์สิทธิ์คอยคุ้มครองประคองชะตาชีวิต"
    ),
    6: (
        "อู่ข้าวอู่น้ำ — เปรียบดั่งคลังเสบียงและท้องพระคลังอันอุดมสมบูรณ์ มีกระแสทรัพย์สินเงินทองและโชคลาภไหลเวียนเข้ามาไม่ขาดสาย "
        "ทำมาค้าขายหรือเริ่มโปรเจกต์มักออกดอกออกผลเป็นประโยชน์มหาศาล ชีวิตมีเกณฑ์สุขสบายทางโลกสูงมาก "
        "มักมีลาภลอยหรือแต้มบุญเก่าหนุนนำให้ไม่เคยตกอับขัดสนเรื่องปัจจัยสี่"
    ),
    7: (
        "ยักษ์ — เปรียบดั่งยักษ์ผู้มีฤทธิ์เด่น มีพละกำลังสูงและความมุ่งมั่นไม่ยอมแพ้ระดับรุนแรง เป็นคนตรงไปตรงมา "
        "รักใครรักจริงและเกลียดความคดโกงเป็นที่สุด มีความทรหดเอาจริงเอาจังเป็นเลิศ สามารถฝ่าฟันและแก้ปัญหาโครงสร้างยาก ๆ "
        "ที่คนทั่วไปถอยหนีจนประสบความสำเร็จได้อย่างเด็ดขาดด้วยฝีมือตนเอง"
    ),
    8: (
        "พระราชา — เปรียบดั่งบารมีแห่งพระมหากษัตริย์ผู้ทรงเดชและวาสนาสูงสุดในการปกครองบริวารและแว่นแคว้น "
        "ดึงดูดทั้งชื่อเสียง เกียรติยศชื่อเสียง ยศถาบรรดาศักดิ์ และการสนับสนุนค้ำจุนจากผู้มีอำนาจบารมีเหนือกว่า "
        "ชีวิตมักถูกผลักดันให้ขึ้นคุมบังเหียนตำแหน่งสำคัญที่มีสิทธิ์เสียงเด็ดขาดในการชี้ขาด"
    ),
    9: (
        "อัศวิน — เปรียบดั่งอัศวินผู้กล้าหาญ ปราดเปรียว ว่องไว และรักในเสรีภาพสูงสุด เกลียดการโดนกักขังบีบคั้นจิตใจ "
        "ชื่นชอบการเดินทางไกล การแสวงหาความท้าทายใหม่ ๆ และปรับตัวเข้ากับสถานการณ์ผันผวนได้อย่างรวดเร็ว "
        "มีทักษะไหวพริบเอาตัวรอดได้ในทุกสภาพแวดล้อมอย่างเป็นเลิศ"
    ),
}

THAKSA_CATEGORIES = ["บริวาร", "อายุ", "เดช", "ศรี", "มูละ", "อุตสาหะ", "มนตรี", "กาลกิณี"]

THAKSA_GROUPS = {
    "อาทิตย์": set("อกขคฆง"),
    "จันทร์": set("จฉชซฌญ"),
    "อังคาร": set("ฎฏฐฑฒณ"),
    "พุธกลางวัน": set("ดตถทธน"),
    "เสาร์": set("บปผฝพฟภม"),
    "พฤหัส": set("ยรลว"),
    "ราหู": set("ศษสหฬฮ"),
    "ศุกร์": set("อ"),
}

THAKSA_STAR_ORDER = ["อาทิตย์","จันทร์","อังคาร","พุธกลางวัน","เสาร์","พฤหัส","ราหู","ศุกร์"]

VOWELS = set("ะาิีึืุูเะแโใไ็่้๊๋์")


def _load_data():
    try:
        from core.numerology_loader import get_numerology_data
        return get_numerology_data()
    except ImportError:
        return {}

_num_data = _load_data()
THAI_NAME_WORDS = _num_data.get("THAI_NAME_WORDS", {})


# ═══════════════════════════════════════════
# คลังระบบสืบค้นข้อมูลพยากรณ์จากไฟล์ความรู้
# ═══════════════════════════════════════════

def _find_numerology_file() -> Optional[str]:
    """สแกนหาที่ตั้งจริงของไฟล์ความรู้เลขศาสตร์แบบไดนามิกเพื่อความยืดหยุ่นทางพาธสถาปัตยกรรม"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths_to_check = [
        os.path.join(base_dir, "data", "knowledge", "numerology.md"),
        os.path.join(os.getcwd(), "data", "knowledge", "numerology.md"),
        os.path.join(os.getcwd(), "numerology.md"),
        os.path.join(os.getcwd(), "data", "numerology.md"),
    ]
    for p in paths_to_check:
        if os.path.exists(p):
            return p
    return None


def get_numerology_description_from_file(number: int, parent_header_level: int = 4) -> str:
    """ดึงบทวิเคราะห์เต็มรูปแบบจากไฟล์ พร้อมทั้งปรับจัดระดับหัวข้อให้อยู่ในสัดส่วนที่ถูกต้องเพื่อความสวยงาม"""
    file_path = _find_numerology_file()
    if not file_path:
        return f"*(ไม่พบไฟล์รายละเอียดคำทำนายของหมายเลข {number} บนพาธระบบ)*"
            
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        pattern = rf"^##\s+(?:เข้าสู่\s*)?หมายเลข\s*{number}\b"
        matches = list(re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE))
        if not matches:
            return f"*(ไม่พบบทวิเคราะห์ดวงดาวสำหรับหมายเลข {number} ในคลังไฟล์ความรู้)*"
            
        start = matches[0].start()
        next_heading = re.search(r"^##\s+", content[matches[0].end():], re.MULTILINE)
        if next_heading:
            end = matches[0].end() + next_heading.start()
        else:
            end = len(content)
            
        section_raw = content[start:end].strip()
        lines = section_raw.split("\n")
        adjusted_lines = []
        for line in lines:
            if line.strip() == "---":
                continue
            
            h_match = re.match(r"^(#+)\s*(.*)$", line)
            if h_match:
                curr_level = len(h_match.group(1))
                h_text = h_match.group(2).strip()
                new_level = curr_level + (parent_header_level - 2)
                adjusted_lines.append(f"{'#' * new_level} {h_text}")
            else:
                adjusted_lines.append(line)
                
        return "\n".join(adjusted_lines).strip()
    except Exception as e:
        return f"*(ข้อผิดพลาดการดึงข้อมูลจากไฟล์: {e})*"


def get_numerology_summary_from_file(number: int) -> str:
    """ดึงข้อมูลหัวข้อและคะแนนพลังงานของดวงดาวแบบสรุปกระชับปราศจากเครื่องหมายยุ่งเหยิง"""
    full_desc = get_numerology_description_from_file(number, parent_header_level=4)
    if full_desc.startswith("*"):
        return f"หมายเลข {number}"
        
    lines = [line.strip() for line in full_desc.split("\n") if line.strip()]
    if not lines:
        return f"หมายเลข {number}"
        
    title = re.sub(r"^#+\s*", "", lines[0]).strip()
    title = re.sub(r"^หมายเลข\s*\d+\s*:\s*", "", title, flags=re.IGNORECASE)
    
    energy_score = ""
    for line in lines[1:4]:
        if "คะแนนพลังงาน" in line:
            energy_score = re.sub(r"^[-*\s]*\**คะแนนพลังงาน\**\s*:\s*", "", line, flags=re.IGNORECASE).strip()
            energy_score = energy_score.replace("**", "")
            break
            
    if energy_score:
        return f"**{title}** (ค่าคะแนนพลังงาน: {energy_score})"
    return f"**{title}**"


def get_friendly_name_interpretation(name: str) -> str:
    """ถอดรหัสความหมายพยัญชนะไทยหลักในชื่อมาเรียงร้อยเปรียบเทียบกรณีไม่มีข้อมูลในคลังรากศัพท์"""
    meanings = {
        'ก': "ความเป็นหนึ่ง ความเป็นผู้นำ และเจตจำนงเสรีที่เด็ดเดี่ยว",
        'ข': "ความเพียรพยายาม การต่อสู้บุกเบิก และพลังการรักษาทรัพย์สมบัติ",
        'ค': "สติปัญญาหลักแหลม ไหวพริบความรวดเร็ว และการประสานเจรจาพารวย",
        'ฆ': "ความหนักแน่น ทรหด และความสามารถในการคุมอารมณ์ต่อสู้",
        'ง': "ความอ่อนโยน โอบอ้อมอารี และความลื่นไหลปรับตัวเก่งดั่งน้ำ",
        'จ': "ความสุนทรี รสนิยมทางโลกที่สง่างาม และมีจินตนาการกว้างไกล",
        'ฉ': "ความเมตตาธรรมสูงส่ง การโอบอุ้มชูชุบ และผู้ชี้ทางสมาธิปัญญา",
        'ช': "ชัยชนะเหนืออุปสรรค พลังขับเคลื่อนงานใหญ่ และความมั่นคงในหน้าที่",
        'ซ': "ความอดทนอดกลั้น ความตั้งใจจริง และความเชื่อมั่นเด็ดเดี่ยว",
        'ญ': "ปัญญาชั้นสูง ปฏิภาณไหวพริบ และความคิดสร้างสรรค์ล้ำสมัย",
        'ฎ': "ความตรงไปตรงมา รักความยุติธรรม และจิตใจที่ซื่อสัตย์",
        'ฏ': "ความมีระเบียบวินัย ความเอาจริงเอาจัง และการจัดระบบได้ดีเยี่ยม",
        'ฐ': "ความมั่นคงแข็งแกร่ง รากแก้วแห่งชะตาชีวิตที่ยากจะสั่นคลอน",
        'ณ': "ความกตัญญู มีคุณธรรมสูงส่ง และการเป็นที่รักของมหาชน",
        'ด': "เกียรติยศชื่อเสียง ความเป็นผู้นำ และมีบารมีคนเกรงใจ",
        'ต': "วินัยเหล็กในการสู้ชีวิต ความรับผิดชอบ และมุ่งมั่นลุยงานหนัก",
        'ถ': "การพึ่งพาตนเอง ความประหยัดมัธยัสถ์ และวิถีความพอเพียงมั่นคง",
        'ท': "พละกำลังทางกายภาพ การลงแรงสู้ชีวิต และความอดทนเป็นเลิศ",
        'ธ': "ทรัพย์สินเงินทอง ความอุดมสมบูรณ์ และมีโชคลาภความเจริญรุ่งเรือง",
        'น': "คุณธรรม จิตใจดีงาม มีเมตตาเอ็นดู และกตัญญูต่อผู้มีพระคุณ",
        'บ': "ความร่มเย็นเป็นสุขในครอบครัว ยานพาหนะ และรากฐานที่อยู่อาศัย",
        'ป': "การปกป้องคุ้มครองบริวารหมู่มาก และความกว้างขวางทางสังคม",
        'ผ': "เสน่ห์ดึงดูดเมตตามหานิยมสูง ได้รับความรักใคร่เอ็นดูจากสิ่งแวดล้อม",
        'ฝ': "ความมุมานะพยายาม และมีไหวพริบในการสลัดปัญหาพ้นเคราห์กรรม",
        'พ': "ความงอกงามงอกเงยทางการเงิน และผลประโยชน์กำไรธุรกิจหลัก",
        'ฟ': "สมองเฉียบคม ทันเล่ห์เหลี่ยม ทันคน และเรียนรู้ข่าวสารว่องไว",
        'ภ': "โอกาสเดินทางไกล ต่างถิ่นแดนไกล หรือแต้มโชคดีกะทันหัน",
        'ม': "ความโอบอ้อมอารี จิตใจดี และได้รับการสนับสนุนรอบตัว",
        'ย': "ความโดดเด่นสะดุดตาสังคม และรสนิยมสุนทรีศิลปะความงาม",
        'ร': "ความเจริญรุ่งโรจน์ มั่งคั่ง ยศถาบรรดาศักดิ์ และมหาบารมีค้ำชู",
        'ล': "สุนทรีภาพในการครองตน รักธรรมชาติ ดนตรี และความรื่นรมย์สบายใจ",
        'ว': "ระเบียบวินัยในตนเอง วาจาสัจจะศักดิ์สิทธิ์ และวาทศิลป์สร้างเงิน",
        'ศ': "ความสงบเย็น ความรอบรู้ใฝ่ธรรมะ และมีสิ่งศักดิ์สิทธิ์หนุนชะตา",
        'ษ': "ความกล้าหาญ เด็ดเดี่ยว และการเป็นเสาหลักพึ่งพาให้บริวาร",
        'ส': "สติปัญญาหลักแหลม มีเป้าหมายยิ่งใหญ่ และกล้าท้าทายเปลี่ยนแปลง",
        'ห': "ความเมตตาสูง มีหัวใจเกื้อหนุนคน และได้รับการช่วยเหลือจากผู้ใหญ่",
        'ฬ': "ความทรหดแข็งแกร่ง และความสำเร็จจากผลงานความพยายามจริง",
        'อ': "ออร่าเมตตามหานิยมสูงสุด ดึงดูดมิตรภาพและคนอุปถัมภ์ค้ำจุน",
    }
    
    # สกัดเฉพาะพยัญชนะไทยหลัก
    consonants = [char for char in name if char in meanings]
    if not consonants:
        return "ผู้มีพลังแห่งความสร้างสรรค์ ปัญญาโชคลาภ และดึงดูดสิ่งมงคลความเจริญรุ่งเรืองอย่างมั่นคงถาวร"
        
    parts = []
    # เลือกพยัญชนะเด่นสุด 4 ตัวแรกมาเขียนเรียบเรียงบททำนายอักขระมงคล
    for char in consonants[:4]:
        parts.append(meanings[char])
        
    combined_text = " ประสานร่วมกับ ".join(parts)
    return f"เป็นลักษณะของ **{combined_text}** ส่งผลให้ชะตาชีวิตมีแรงขับเคลื่อนที่ดี ได้รับอิทธิพลของอักขระนำคอยปกป้องคุ้มครองและเบิกทางความก้าวหน้าอย่างสม่ำเสมอครับ"


# ═══════════════════════════════════════════
# CORE CALCULATORS (Thai Numerology Logic)
# ═══════════════════════════════════════════

def calculate_numerology(name: str) -> Dict:
    clean = name.replace(" ", "")
    details = []
    total = 0
    for char in clean:
        val = THAI_NUM_TABLE.get(char, 0)
        total += val
        details.append((char, val))

    reduced_chain = [total]
    while total > 9:
        total = sum(int(d) for d in str(total))
        reduced_chain.append(total)

    meanings = []
    for v in reduced_chain:
        m = get_numerology_summary_from_file(v)
        meanings.append({"value": v, "meaning": m})

    return {
        "raw_sum": reduced_chain[0],
        "reduced": reduced_chain[-1],
        "chain": reduced_chain,
        "meanings": meanings,
        "details": details,
    }


def calculate_ayatana(name: str) -> Dict:
    clean = name.replace(" ", "")
    total = 0
    for char in clean:
        total += THAI_AYATANA_TABLE.get(char, 0)

    result = total % 9
    if result == 0 and total > 0:
        result = 9

    return {
        "total": total,
        "value": result,
        "meaning": THAI_AYATANA_MEANINGS.get(result, ""),
    }


def get_thaksa_map(birth_day: str) -> Dict[str, str]:
    day_map = {
        "อาทิตย์": 0, "จันทร์": 1, "อังคาร": 2, "พุธ": 3, "พุธกลางวัน": 3,
        "เสาร์": 4, "พฤหัส": 5, "พฤหัสบดี": 5, "ราหู": 6, "พุธกลางคืน": 6, "ศุกร์": 7
    }
    start = day_map.get(birth_day.replace("วัน","").strip(), 0)

    result = {}
    for i, cat in enumerate(THAKSA_CATEGORIES):
        star = THAKSA_STAR_ORDER[(start + i) % 8]
        for char in THAKSA_GROUPS.get(star, set()):
            result[char] = cat
    return result


def analyze_thaksa(name: str, thaksa_map: Dict[str, str]) -> Dict:
    clean = name.replace(" ", "")
    gala_chars = []
    sri_chars = []
    dech_chars = []
    sri_power = 0
    dech_power = 0

    for char in clean:
        cat = thaksa_map.get(char, "บริวาร")
        is_vowel = char in VOWELS
        if cat == "กาลกิณี" and not is_vowel:
            gala_chars.append(char)
        elif cat == "ศรี":
            sri_chars.append(char)
            sri_power += 1
        elif cat == "เดช":
            dech_chars.append(char)
            dech_power += 1

    gala = len(set(gala_chars))
    if gala >= 2:
        level = "ไม่แนะนำอย่างยิ่ง (กาลกิณีทับซ้อนบั่นทอนดวงชะตา)"
    elif gala == 1:
        level = "ไม่แนะนำ (ปรากฏอักษรต้องห้ามกาลกิณีขัดขวางโชค)"
    elif sri_chars and dech_chars:
        level = "ดีเยี่ยม (โครงสร้างชื่อกุมเกณฑ์ดาวทั้งอำนาจและโชคทรัพย์ครบถ้วน)"
    else:
        level = "ดีมาก (พลังอักษรส่งเสริมความก้าวหน้าอย่างกลมกลืน)"

    return {
        "gala_count": gala,
        "gala_chars": list(set(gala_chars)),
        "sri_chars": list(set(sri_chars)),
        "dech_chars": list(set(dech_chars)),
        "sri_power": sri_power,
        "dech_power": dech_power,
        "level": level,
    }


def find_word_roots(name: str) -> List[Tuple[str, str]]:
    found = []
    remaining = name
    for word in sorted(THAI_NAME_WORDS.keys(), key=len, reverse=True):
        if word in remaining:
            meaning = THAI_NAME_WORDS[word]
            found.append((word, meaning[0] if isinstance(meaning, list) else meaning))
    return found


# ═══════════════════════════════════════════
# REPORT GENERATOR
# ═══════════════════════════════════════════

def generate_name_report(name: str) -> str:
    """สร้างรายงานวิเคราะห์ชื่อ 5 มิติเจาะลึกสูงสุดสมบูรณ์แบบปราศจากการย่อรหัส"""
    parts = name.split()
    first_name = parts[0] if parts else name
    last_name = parts[1] if len(parts) > 1 else ""

    lines = [
        f"# 🔮 รายงานวิเคราะห์เจาะลึกชื่อศาสตร์โบราณ 5 มิติเชิงวิชาการ: {name}",
        "",
        "## 🔬 มิติที่ 1: อักษรศาสตร์และสัญชาตญาณรากศัพท์มงคล",
        "",
    ]

    # มิติ 1
    for i, p in enumerate(parts):
        title = "ชื่อจริง" if i == 0 else "นามสกุล"
        roots = find_word_roots(p)
        lines.append(f"### {title}: {p}")
        if roots:
            for w, m in roots:
                lines.append(f"- **{w}**: {m}")
            meaning_str = " — ".join([m.split()[0] for _, m in roots])
            lines.append(f"- **ความหมายรวมรากศัพท์:** \"{meaning_str}\"")
        else:
            # 🔗 สังเคราะห์ความหมายของพยัญชนะตัวเด่นให้ผู้ใช้อ่านอย่างเข้าใจในรากอักษรศาสตร์
            friendly_meaning = get_friendly_name_interpretation(p)
            lines.append(f"- **บทพยากรณ์โครงสร้างอักขระมงคล:** {friendly_meaning}")
        lines.append("")

    if len(parts) > 1:
        lines.append("### ปฏิสัมพันธ์เชิงลึกของชื่อและนามสกุล:")
        lines.append("โครงสร้างทางภาษาศาสตร์ระบุว่าชื่อจริงและนามสกุลของคุณประสานคลื่นเสียงและแรงขับเคลื่อนไปทางเดียวกัน ช่วยลดความหน่วงในเกณฑ์ชะตาชีวิตอย่างลงตัว")
        lines.append("")

    # มิติ 2
    lines.append("---")
    lines.append("## 🪐 มิติที่ 2: เลขศาสตร์ดวงดาวและอัตราพลังงานเชิงลึก (Numerology Deep-Dive)")
    lines.append("")
    lines.append("ตัวอักษรและสระทั้งหมดถูกสลักรหัสตัวเลขศาสตร์อ้างอิงกำลังดวงดาวจริงของไทย ดังนี้ครับ:")
    lines.append("")

    total = 0
    for i, p in enumerate(parts):
        title = "ชื่อจริง" if i == 0 else "นามสกุล"
        num = calculate_numerology(p)
        total += num["raw_sum"]
        detail_str = " + ".join(f"{char}({v})" for char, v in num["details"])
        lines.append(f"### {title}: {p}")
        lines.append(f"- **โครงสร้างสมการคำนวณอักษร:** {detail_str} = **{num['raw_sum']}**")
        lines.append(f"- **รหัสเลขลดทอนกำลังชีวิต:** {num['reduced']}")
        
        meaning_summary = get_numerology_summary_from_file(num['raw_sum'])
        lines.append(f"- **บทวิเคราะห์ดวงดาวประจำเรือนชะตา:** {meaning_summary}")
        lines.append("")

    if len(parts) > 1:
        combined = calculate_numerology(name)
        chain_str = " → ".join(str(v) for v in combined["chain"])
        lines.append(f"### 🌟 ผลรวมดวงชะตารวมสูงสุดของชีวิตคุณ: {total}")
        lines.append(f"- **สูตรการรวมรวมดวงชะตา:** {' + '.join(str(calculate_numerology(p)['raw_sum']) for p in parts)} = **{total}**")
        lines.append(f"- **การลดทอนกำลังรวมดวงชะตาตามลำดับ:** {chain_str}")
        lines.append(f"- **เลขเด่นหลักวิถีชะตาชีวิต:** {combined['reduced']}")
        lines.append("")
        
        # 🔗 ดึงข้อมูลวิเคราะห์ตัวเต็มของผลรวมสูงสุดจากไฟล์ความรู้หลักมาพ่นให้อ่านแบบเจาะลึก
        lines.append("#### 📑 รายงานวิเคราะห์เจาะลึกของรหัสตัวเลขอภิมหาพลังงานสูงสุด:")
        lines.append(get_numerology_description_from_file(total, parent_header_level=5))
        lines.append("")

    # มิติ 3
    lines.append("---")
    lines.append("## 🌀 มิติที่ 3: พลังอายตนะ 6 (พลังดึงดูดและออร่าทางสังคม)")
    lines.append("")
    lines.append("พลังอายตนะ 6 เปรียบเสมือน 'แรงดึงดูดทางจิตใต้สำนึก' ที่มีอิทธิพลต่อบุคคลรอบกายยามที่ได้ยินชื่อหรือสัมผัสตัวตนของคุณ:")
    lines.append("")
    
    for i, p in enumerate(parts):
        title = "ชื่อจริง" if i == 0 else "นามสกุล"
        ay = calculate_ayatana(p)
        lines.append(f"### {title} \"{p}\":")
        lines.append(f"  - สัมผัสพลังงานอายตนะ 6 ได้หมายเลข **{ay['value']}**")
        lines.append(f"  - **อิทธิพลที่แสดงผล:** {ay['meaning']}")
        lines.append("")
        
    if len(parts) > 1:
        ay_all = calculate_ayatana(name)
        lines.append(f"### ภาพรวมพลังงานอายตนะประสานทั้งหมด:")
        lines.append(f"  - สัมผัสพลังงานร่วมได้หมายเลข **{ay_all['value']}**")
        lines.append(f"  - **อิทธิพลเกื้อหนุนภาพรวม:** {ay_all['meaning']}")
    lines.append("")

    # มิติ 4
    lines.append("---")
    lines.append("## 🧭 มิติที่ 4: ทักษาปกรณ์โบราณและอักขระลิขิตรายวันเกิด")
    lines.append("")
    lines.append("ทักษาปกรณ์คือเกณฑ์ตรวจสอบความมงคลของชื่อโดยตรงกับ 'วันเกิดทางจันทรคติ' เพื่อสแกนหาจุดเกื้อหนุนที่ดีที่สุดและระบุจุดอ่อนของตัวอักษรอย่างลึกซึ้ง:")
    lines.append("")
    
    lines.append("| วันเกิด | ตัวอักษรกาลกิณีที่ปรากฏ | อักษรเด่นกุมเกณฑ์ (เดช/ศรี) | ระดับความมงคลและคำแนะนำทักษา |")
    lines.append("|:---|:---|:---|:---|")
    days = ["วันอาทิตย์","วันจันทร์","วันอังคาร","วันพุธกลางวัน","วันพุธกลางคืน","วันพฤหัสบดี","วันศุกร์","วันเสาร์"]
    for d in days:
        tmap = get_thaksa_map(d)
        analysis = analyze_thaksa(first_name, tmap)
        gala_str = ", ".join(analysis["gala_chars"]) if analysis["gala_chars"] else "—"
        
        sri_str = f"ศรี:{''.join(analysis['sri_chars'])}" if analysis['sri_chars'] else ""
        dech_str = f"เดช:{''.join(analysis['dech_chars'])}" if analysis['dech_chars'] else ""
        stars_str = " | ".join(filter(None, [sri_str, dech_str])) if (sri_str or dech_str) else "—"
        
        lines.append(f"| {d} | {gala_str} | {stars_str} | **{analysis['level']}** |")
    lines.append("")
    
    lines.append("### 🗓️ วิเคราะห์กลศาสตร์ทักษาปกรณ์รายตัวอักษรประจำวันเกิด:")
    lines.append(
        "- **อักษรเดช (อำนาจ ยศฐาบารมี สิทธิ์เสียง):** ทำหน้าที่ผลักดันชะตาชีวิตให้คุณเป็นผู้น่าเชื่อถือ มีสิทธิ์ขาดในการต่อรองบริหาร "
        "ผู้ใต้บังคับบัญชาเกิดความเกรงใจและเคารพในการตัดสินใจ"
    )
    lines.append(
        "- **อักษรศรี (โชคลาภ ทรัพย์สิน ความเสน่หา):** ทำหน้าที่เหนี่ยวนำกระแสเงินสด โอกาสทองทางธุรกิจ และดึงดูดความเอ็นดูเกื้อหนุนจากสิ่งแวดล้อมรอบตัว"
    )
    lines.append(
        "- **อักษรกาลกิณี (เคราะห์กรรม หนี้สิน อุปสรรค):** คืออักษรที่เป็นปัญหากลุ่มความร้อนรุ่มและเคราห์กรรมขัดขวางโชค "
        "หากหลีกเลี่ยงหรือไม่มีปรากฏในชื่อสำหรับวันเกิดของตน จะช่วยให้กระแสชีวิตไหลลื่นและปลอดภัยจากปัญหาเอกสารคดีความอย่างยอดเยี่ยม"
    )
    lines.append("")

    # มิติ 5 สรุป
    lines.append("---")
    lines.append("## 📝 มิติที่ 5: บทสรุปดวงชะตาสังเคราะห์เชิงสถิติและการประยุกต์ใช้งาน")
    lines.append("")
    if len(parts) > 1:
        lines.append(
            f"จากการประมวลผล 5 มิตินามศาสตร์สัญกรณ์ไทย ชื่อและนามสกุล **\"{name}\"** นี้ "
            f"มีรหัสพลังงานผลรวมสูงสุดเท่ากับเลขศาสตร์หมายเลข **{total}** ซึ่งมีความหมายวิเศษกำกับตามรายงาน มิติที่ 2 ข้างต้น "
            f"และได้รับการประสานพลังอายตนะทั้งหมดเพื่อเหนี่ยวนำออร่าที่ดีเท่ากับหมายเลข **{ay_all['value']}** ({ay_all['meaning']}) "
            f"แนะนำนำรหัสพลังเหล่านี้ไปจัดวางตำแหน่งชะตาเพื่อเกื้อพยุงวิถีชีวิตจริงได้ทันทีครับ"
        )
    else:
        num_single = calculate_numerology(name)
        ay_single = calculate_ayatana(name)
        lines.append(
            f"ชื่อจริง **\"{name}\"** นี้ มีรหัสพลังงานผลรวมเท่ากับเลขศาสตร์หมายเลข **{num_single['reduced']}** "
            f"และมีพลังอายตนะดึงดูดเท่ากับรหัสหมายเลข **{ay_single['value']}** ({ay_single['meaning']})"
        )
    lines.append("")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════
# SYSTEM HANDLER
# ═══════════════════════════════════════════

def name_analysis_handler(action: str, inp: str, entities: list) -> Dict[str, Any]:
    """ตัวประมวลผลวิเคราะห์ชื่อมงคลระดับโปรดักชัน"""
    target_name = entities[0] if entities else inp
    report = generate_name_report(target_name)
    return {
        "status": "success",
        "result": report,
        "direct_response": True
    }


# ═══════════════════════════════════════════
# TOOLS FOR SYSTEM COUPLING
# ═══════════════════════════════════════════

def get_tools() -> Dict:
    """ส่งคืนเครื่องมือสำหรับการลงทะเบียนของ ExecutionEngine"""
    return {
        "name_analysis": name_analysis_handler,
        "analyze_thai_name": name_analysis_handler,
        "analyze_name": name_analysis_handler,
    }