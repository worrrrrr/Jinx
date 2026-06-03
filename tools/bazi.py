# tools/bazi.py

"""
เครื่องมือวิเคราะห์ Ba Zi (八字) และเชื่อมโยงกับ Cognitive Functions (MBTI)

Dependencies:
    - cnlunar (pip install cnlunar)
    - Python >= 3.7
"""

import datetime
import re
from typing import Dict, List, Tuple, Optional

try:
    import cnlunar
    _CNLUNAR_AVAILABLE = True
except ImportError:
    _CNLUNAR_AVAILABLE = False
    cnlunar = None  # type: ignore


# ============================================================
# Constants
# ============================================================

# Heavenly Stems (天干) และธาตุ
TIAN_GAN_ELEMENT = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# Earthly Branches (地支) และธาตุหลัก (Main Qi)
DI_ZHI_MAIN_ELEMENT = {
    '子': '水',
    '丑': '土',
    '寅': '木',
    '卯': '木',
    '辰': '土',
    '巳': '火',
    '午': '火',
    '未': '土',
    '申': '金',
    '酉': '金',
    '戌': '土',
    '亥': '水',
}

# Hidden Stems (藏干) เบื้องต้น (Main Qi เท่านั้น)
# เราอาจใช้แค่ main qi เพื่อความง่าย แต่ถ้าต้องการละเอียดจะเพิ่มภายหลัง
HIDDEN_STEMS = {
    '子': ['癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['乙'],
    '辰': ['戊', '乙', '癸'],
    '巳': ['丙', '庚', '戊'],
    '午': ['丁', '己'],
    '未': ['己', '丁', '乙'],
    '申': ['庚', '壬', '戊'],
    '酉': ['辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲'],
}

# ฤดูกาลตามเดือน Jie Qi (Earthly Branch ของเดือน)
# เดือนใน Ba Zi ใช้ Earthly Branch ของเดือน (หลัง Jie Qi)
MONTH_TO_SEASON = {
    '寅': '木',  # ต้นฤดูใบไม้ผลิ
    '卯': '木',  # กลางฤดูใบไม้ผลิ
    '辰': '土',  # ปลายฤดูใบไม้ผลิ (ดิน)
    '巳': '火',  # ต้นฤดูร้อน
    '午': '火',  # กลางฤดูร้อน
    '未': '土',  # ปลายฤดูร้อน (ดิน)
    '申': '金',  # ต้นฤดูใบไม้ร่วง
    '酉': '金',  # กลางฤดูใบไม้ร่วง
    '戌': '土',  # ปลายฤดูใบไม้ร่วง (ดิน)
    '亥': '水',  # ต้นฤดูหนาว
    '子': '水',  # กลางฤดูหนาว
    '丑': '土',  # ปลายฤดูหนาว (ดิน)
}

# ลำดับ 10 Gods (十神) mapping เทียบกับ Day Master
# ตัวอย่าง: Day Master 甲 -> 甲:比肩, 乙:劫财, 丙:食神, 丁:伤官, 戊:偏财, 己:正财, 庚:七杀, 辛:正官, 壬:偏印, 癸:正印
# เราจะสร้างตารางหรือใช้ logic

# Mapping ธาตุไปยัง Cognitive Functions (สมมติฐาน)
ELEMENT_TO_FUNCTIONS = {
    '火': ['Fi'],
    '土': ['Te', 'Si'],
    '金': ['Ni', 'Ti'],
    '水': ['Fe'],
    '木': ['Ne', 'Se'],
}

# คำอธิบาย Ten Gods เป็นภาษาไทย
GOD_DESCRIPTIONS_TH = {
    "比肩": "เพื่อนร่วมธาตุ แบบคนรอบข้างที่เป็นแนวเดียวกับเรา",
    "劫财": "เพื่อนแย่งชิง แบบคนที่มาแย่งโอกาสหรือทรัพย์",
    "食神": "อาหารหรือพรสวรรค์ มีเสน่ห์ ศิลปะ ความสุขในชีวิต",
    "伤官": "นักแสดงออก ฉลาดพูดเก่ง แต่มักต่อต้านอำนาจ",
    "偏财": "ทรัพย์จากทางลัด การลงทุน เสี่ยงโชค",
    "正财": "ทรัพย์มั่นคง การเงินจากการทำงานหนัก อดทน",
    "七杀": "แรงกดดันและอำนาจ ชีวิตมีอุปสรรคแต่ทำให้แกร่ง",
    "正官": "ตำแหน่งและวินัย เหมาะกับราชการหรือสายปกครอง",
    "偏印": "ปัญญาพิเศษด้านจินตนาการ ศาสตร์ลึกลับ",
    "正印": "ปัญญาจากการศึกษา เอกสาร ผู้ใหญ่คอยอุปถัมภ์",
}

ELEMENT_ADVICE_TH = {
    '木': 'ธาตุไม้—ถ้ามากไปใช้ไฟระบาย ถ้าน้อยไปต้องการน้ำเลี้ยง',
    '火': 'ธาตุไฟ—ถ้าแรงไปต้องการดิน/โลหะลด heat ถ้าอ่อนต้องการไม้เป็นเชื้อ',
    '土': 'ธาตุดิน—ถ้าหนักไปใช้แร่(金)ระบาย ถ้าบางไปต้องการไฟ',
    '金': 'ธาตุโลหะ—แข็งเกินต้องใช้ไฟหลอม ถ้าอ่อนต้องการดิน',
    '水': 'ธาตุน้ำ—ถ้าท่วมใช้ดินกั้น ถ้าแห้งต้องการโลหะเป็นแหล่ง',
}

# ============================================================
# Core Class
# ============================================================

class BaZi:
    """Object representing a BaZi chart and providing analysis."""

    def __init__(self, birth_datetime: datetime.datetime):
        """
        รับ datetime (local time) ในการเกิด
        """
        if not _CNLUNAR_AVAILABLE:
            raise ImportError("cnlunar ไม่ได้ติดตั้ง — ใช้ pip install cnlunar ก่อนเรียกใช้ Ba Zi")
        self.birth_dt = birth_datetime
        # ใช้ cnlunar คำนวณ (timezone ภายในของ datetime ต้องเป็น local time)
        self.lunar = cnlunar.Lunar(birth_datetime)

        # เสา 4 ตัว (干支)
        self.year_pillar = self.lunar.year8Char  # e.g. "壬申"
        self.month_pillar = self.lunar.month8Char  # e.g. "戊申"
        self.day_pillar = self.lunar.day8Char    # e.g. "丙辰"
        self.hour_pillar = self.lunar.twohour8Char  # e.g. "丙申"

        # Day Master (日主) คือ Heavenly Stem ตัวแรกของ day pillar
        self.day_master = self.day_pillar[0] if self.day_pillar else ""

        # ตรวจสอบความถูกต้อง
        if not self.day_master:
            raise ValueError("ไม่สามารถคำนวณ Day Master ได้ กรุณาตรวจสอบวันเกิด")

        # วิเคราะห์ธาตุ
        self.element_strength = self._compute_element_strength()

        # 10 Gods (เบื้องต้น)
        self.ten_gods = self._compute_ten_gods()

    def _count_element_from_ganzhi(self, gan_zhi: str, include_hidden: bool = False) -> Dict[str, int]:
        """
        นับธาตุจาก干支 หนึ่งคู่ (เช่น "丙辰")
        """
        counts = {}
        # Heavenly Stem
        if len(gan_zhi) >= 2:
            gan = gan_zhi[0]
            zhi = gan_zhi[1]
        else:
            return counts
        elem = TIAN_GAN_ELEMENT.get(gan)
        if elem:
            counts[elem] = counts.get(elem, 0) + 1

        # Earthly Branch main element
        main_elem = DI_ZHI_MAIN_ELEMENT.get(zhi)
        if main_elem:
            counts[main_elem] = counts.get(main_elem, 0) + 1

        # Hidden stems (optional)
        if include_hidden:
            hidden_list = HIDDEN_STEMS.get(zhi, [])
            for hid in hidden_list:
                elem_h = TIAN_GAN_ELEMENT.get(hid)
                if elem_h:
                    counts[elem_h] = counts.get(elem_h, 0) + 0.5  # ให้น้ำหนักครึ่งหนึ่ง

        return counts

    def _compute_element_strength(self) -> Dict[str, float]:
        """
        คำนวณความแข็งแรงของแต่ละธาตุ โดยนับจากทั้ง 8 ตัวในเสา และปรับด้วยฤดูกาล
        """
        strength = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}

        # นับจากเสา 4 ตัว
        for pillar in [self.year_pillar, self.month_pillar, self.day_pillar, self.hour_pillar]:
            counts = self._count_element_from_ganzhi(pillar, include_hidden=False)
            for elem, cnt in counts.items():
                strength[elem] += cnt

        # ปรับตามฤดูกาล (เดือน)
        month_zhi = self.month_pillar[1]  # ตัวอักษรที่สองคือ Earthly Branch ของเดือน
        season_elem = MONTH_TO_SEASON.get(month_zhi)
        if season_elem:
            # ให้ธาตุตามฤดูกาลมีน้ำหนักเพิ่ม
            strength[season_elem] += 0.5  # หรือคูณ 1.2 ก็ได้

        # กรณีเดือนเป็นดิน (辰未戌丑) ดินเด่น
        # ตรงนี้ปรับแต่งได้

        return strength

    def _compute_ten_gods(self) -> Dict[str, List[str]]:
        """
        คำนวณ 10 Gods เบื้องต้นโดยเทียบจาก Day Master
        ส่งคืน dict ที่ key เป็น pillar (year, month, day, hour) และ value เป็น list ของ God names
        """
        # สร้าง mapping 10 Gods ตาม Day Master
        # ใช้สูตรสัมพันธ์ของ 5 elements และ yin/yang
        gods = {}
        # สำหรับแต่ละเสา
        for pillar_name, pillar in [('year', self.year_pillar),
                                    ('month', self.month_pillar),
                                    ('day', self.day_pillar),
                                    ('hour', self.hour_pillar)]:
            if len(pillar) < 2:
                continue
            gan = pillar[0]
            gods[pillar_name] = self._gan_god(gan)

        return gods

    def _gan_god(self, gan: str) -> str:
        """
        Return 10 God name for a given Heavenly Stem compared to day_master.
        """
        dm = self.day_master
        # ตาราง 10 Gods: https://en.wikipedia.org/wiki/Heavenly_Stems#Ten_Gods
        # สร้าง dict สองชั้น (dm, gan) -> god
        god_map = {
            '甲': {'甲':'比肩','乙':'劫财','丙':'食神','丁':'伤官','戊':'偏财','己':'正财','庚':'七杀','辛':'正官','壬':'偏印','癸':'正印'},
            '乙': {'甲':'劫财','乙':'比肩','丙':'伤官','丁':'食神','戊':'正财','己':'偏财','庚':'正官','辛':'七杀','壬':'正印','癸':'偏印'},
            '丙': {'甲':'偏印','乙':'正印','丙':'比肩','丁':'劫财','戊':'食神','己':'伤官','庚':'偏财','辛':'正财','壬':'七杀','癸':'正官'},
            '丁': {'甲':'正印','乙':'偏印','丙':'劫财','丁':'比肩','戊':'伤官','己':'食神','庚':'正财','辛':'偏财','壬':'正官','癸':'七杀'},
            '戊': {'甲':'七杀','乙':'正官','丙':'偏印','丁':'正印','戊':'比肩','己':'劫财','庚':'食神','辛':'伤官','壬':'偏财','癸':'正财'},
            '己': {'甲':'正官','乙':'七杀','丙':'正印','丁':'偏印','戊':'劫财','己':'比肩','庚':'伤官','辛':'食神','壬':'正财','癸':'偏财'},
            '庚': {'甲':'偏财','乙':'正财','丙':'七杀','丁':'正官','戊':'偏印','己':'正印','庚':'比肩','辛':'劫财','壬':'食神','癸':'伤官'},
            '辛': {'甲':'正财','乙':'偏财','丙':'正官','丁':'七杀','戊':'正印','己':'偏印','庚':'劫财','辛':'比肩','壬':'伤官','癸':'食神'},
            '壬': {'甲':'食神','乙':'伤官','丙':'偏财','丁':'正财','戊':'七杀','己':'正官','庚':'偏印','辛':'正印','壬':'比肩','癸':'劫财'},
            '癸': {'甲':'伤官','乙':'食神','丙':'正财','丁':'偏财','戊':'正官','己':'七杀','庚':'正印','辛':'偏印','壬':'劫财','癸':'比肩'},
        }
        return god_map.get(dm, {}).get(gan, 'Unknown')

    def get_dominant_elements(self, top: int = 2) -> List[Tuple[str, float]]:
        """
        คืนค่ารายชื่อธาตุที่เด่นตามคะแนน strength เรียงจากมากไปน้อย
        """
        sorted_elements = sorted(self.element_strength.items(), key=lambda x: x[1], reverse=True)
        return sorted_elements[:top]

    def get_mbti_functions(self) -> List[str]:
        """
        ส่งคืน cognitive functions ที่อาจมีตามธาตุเด่น
        โดยนำธาตุเด่นสุด 2 อันดับมาประกอบ
        """
        dom_elements = self.get_dominant_elements()
        functions = []
        for elem, _ in dom_elements:
            funcs = ELEMENT_TO_FUNCTIONS.get(elem, [])
            functions.extend(funcs)
        # ตัดตัวซ้ำและคงลำดับ
        unique = []
        for f in functions:
            if f not in unique:
                unique.append(f)
        return unique

    def get_zodiac_summary(self) -> dict:
        """
        คืนค่าสรุปปีนักษัตร: สัตว์ปีเกิด, สามเกลอ, หกเกลอ
        """
        return {
            "year_zodiac": self._zodiac_name(self.lunar.chineseYearZodiac),
            "zodiac_mark3": [self._zodiac_name(z) for z in self.lunar.zodiacMark3List],
            "zodiac_win": self._zodiac_name(self.lunar.zodiacWin),
            "zodiac_lose": self._zodiac_name(self.lunar.zodiacLose) if hasattr(self.lunar, 'zodiacLose') else "",
        }

    @staticmethod
    def _zodiac_name(cn: str) -> str:
        mapping = {
            '鼠': 'หนู', '牛': 'วัว', '虎': 'เสือ', '兔': 'กระต่าย',
            '龙': 'มังกร', '蛇': 'งู', '马': 'ม้า', '羊': 'แพะ',
            '猴': 'ลิง', '鸡': 'ไก่', '狗': 'หมา', '猪': 'หมู',
            'Rat': 'หนู', 'Ox': 'วัว', 'Tiger': 'เสือ', 'Rabbit': 'กระต่าย',
            'Dragon': 'มังกร', 'Snake': 'งู', 'Horse': 'ม้า', 'Goat': 'แพะ',
            'Monkey': 'ลิง', 'Rooster': 'ไก่', 'Dog': 'หมา', 'Pig': 'หมู',
        }
        return mapping.get(cn, cn)

    def report(self) -> str:
        """
        พิมพ์รายงานวิเคราะห์ Ba Zi
        """
        zodiac = self.get_zodiac_summary()
        lines = [
            f"=== BaZi Analysis ===",
            f"Birth Date: {self.birth_dt}",
            f"Year Pillar: {self.year_pillar}",
            f"Month Pillar: {self.month_pillar}",
            f"Day Pillar: {self.day_pillar}",
            f"Hour Pillar: {self.hour_pillar}",
            f"Day Master: {self.day_master}",
            f"ปีนักษัตร: {zodiac['year_zodiac']}",
            f"สามเกลอ: {', '.join(zodiac['zodiac_mark3'])}",
            f"หกเกลอ: {zodiac['zodiac_win']}",
            f"ทะลวง: {zodiac['zodiac_lose']}",
            f"Element Strengths: {self.element_strength}",
            f"Dominant Elements: {self.get_dominant_elements()}",
            f"Cognitive Functions (mapped): {self.get_mbti_functions()}",
            f"10 Gods: {self.ten_gods}",
        ]
        return "\n".join(lines)


# ============================================================
# Tool Registration
# ============================================================

def get_tools():
    return {
        "bazi": bazi_handler,
        "astrology": bazi_handler,
        "ดูดวง": bazi_handler,
    }


# ============================================================
# Sifu Mode — Professional BaZi Reading
# ============================================================

# ธาตุภาษาไทย
_E = {'木':'ไม้','火':'ไฟ','土':'ดิน','金':'โลหะ','水':'น้ำ'}

# คำอธิบายบุคลิกตาม Day Master (ธาตุ)
_DM_PERSONA = {
    '木': 'ไม้ — ต้นไม้ที่ค่อยเติบโต มองการณ์ไกล ยืดหยุ่น มีเมตตา '
          'แต่บางครั้งดื้อรั้น ไม่ยอมเปลี่ยน คล้ายต้นไผ่ที่ลู่ตามลมแต่ไม่หัก',
    '火': 'ไฟ — ดั่งดวงอาทิตย์ อบอุ่น กระตือรือร้น มีพลังผู้นำ '
          'ทำอะไรตรงไปตรงมา แต่ใจร้อน วู่วาม เหมือนเปลวไฟที่สว่างไสวแต่เผาผลาญตัวเอง',
    '土': 'ดิน — มั่นคง น่าเชื่อถือ ใจกว้าง รับฟัง เป็นศูนย์รวม '
          'แต่บางครั้งเชื่องช้า หัวแข็ง เหมือนแผ่นดินที่รองรับทุกสิ่งแต่ขยับเขยื้อนยาก',
    '金': 'โลหะ — แข็งแกร่ง ยุติธรรม เด็ดขาด มีหลักการ '
          'แต่อาจแข็งกระด้าง ทำให้คนอื่นเกรงใจ เหมือนมีดที่คมแต่บาดมือ',
    '水': 'น้ำ — ฉลาด ปรับตัวเก่ง ลึกซึ้ง มีไหวพริบ '
          'แต่อารมณ์แปรปรวน คาดเดายาก เหมือนสายน้ำที่ไหลเวียนตามทาง',
}

# ความหมายของ 十神 แบบขยาย (ส่วนต้นสั้น สำหรับ inline)
_GOD_BRIEF = {
    "比肩": "เพื่อนร่วมธาตุ — ความสัมพันธ์แนวราบ เพื่อนฝูง พี่น้อง",
    "劫财": "เพื่อนแย่งชิง — คู่แข่ง การเสียทรัพย์โดยใช่เหตุ",
    "食神": "พรสวรรค์ — ศิลปะ ความสุข การแสดงออก",
    "伤官": "นักแสดงออก — ฉลาด พูดเก่ง ไม่ชอบถูกบังคับ",
    "偏财": "ทรัพย์ทางลัด — การลงทุน เสี่ยงโชค ความกล้า",
    "正财": "ทรัพย์มั่นคง — การงานประจำ การออม การเงิน穩",
    "七杀": "พลังอำนาจ — อุปสรรค แรงกดดัน แต่ทำให้แกร่ง",
    "正官": "ตำแหน่งวินัย — เกียรติยศ ความรับผิดชอบ",
    "偏印": "ปัญญาพิเศษ — จินตนาการ ศาสตร์ลึกลับ ของแปลก",
    "正印": "ปัญญาการศึกษา — ผู้ใหญ่ค้ำจุน เอกสาร ใบ cert",
}

# ระดับคะแนนคำอธิบาย
def _elem_level(v):
    if v == 0:          return 0, "❌ ขาด"
    if v <= 0.5:        return 1, "อ่อนมาก"
    if v <= 1.0:        return 2, "อ่อน"
    if v <= 1.5:        return 3, "ปานกลาง"
    if v <= 2.0:        return 4, "ค่อนข้างดี"
    if v <= 2.5:        return 5, "ดี"
    if v <= 3.0:        return 6, "แข็งแรง"
    return 7, "แข็งแรงมาก"

# คำอธิบายพิเศษ DM section
_DM_DETAIL = {
    '木': {
        'strong': 'คุณมีธาตุไม้แข็งแรง — จิตใจมั่นคง มีเป้าหมายชัด '
                  'มองการณ์ไกล เป็นที่พึ่งให้คนอื่นได้ดี แต่อย่าดื้อรั้นเกินไป',
        'weak': 'คุณมีธาตุไม้อ่อน — มีวิสัยทัศน์แต่ขาดพลังผลักดัน '
                'ต้องการคนคอยสนับสนุน หา mentor หรือทีมที่ดีจะช่วยได้มาก',
        'advice': 'เติมน้ำให้ไม้: เรียนรู้ตลอดเวลา อ่านหนังสือ หาความรู้ใหม่ๆ',
    },
    '火': {
        'strong': 'คุณมีธาตุไฟแรง — มีบารมี เป็นผู้นำโดยธรรมชาติ '
                  'คนรอบข้างมองเห็นคุณค่าของคุณ แต่ระวังอารมณ์ร้อน',
        'weak': 'คุณมีธาตุไฟอ่อน — มีความคิดสร้างสรรค์แต่ไม่กล้าแสดงออก '
                'ต้องการคนจุดประกาย ควรหาเพื่อนหรือทีมที่สนับสนุน',
        'advice': 'เติมไม้ให้ไฟ: เรียนรู้จากผู้มีประสบการณ์ หา mentor',
    },
    '土': {
        'strong': 'คุณมีธาตุดินแข็งแรง — น่าเชื่อถือ เป็นหลักให้คนรอบข้าง '
                  'มีวุฒิภาวะสูง เป็นที่พึ่งพิงได้',
        'weak': 'คุณมีธาตุดินอ่อน — ขาดความมั่นคงในชีวิต '
                'วอกแวกง่าย ต้องการระเบียบวินัยมากขึ้น',
        'advice': 'เติมไฟให้ดิน: มีความกระตือรือร้น ลงมือทำให้สม่ำเสมอ',
    },
    '金': {
        'strong': 'คุณมีธาตุโลหะแข็งแรง — เด็ดขาด ยุติธรรม มีหลักการ '
                  'เหมาะกับงานด้านกฎหมาย วิศวกรรม การบริหาร',
        'weak': 'คุณมีธาตุโลหะอ่อน — ขาดความเด็ดขาด โลเล '
                'ต้องการฝึก decision-making ที่ดีขึ้น',
        'advice': 'เติมดินให้โลหะ: สร้างวินัย วางระบบ ทำงานเป็นขั้นตอน',
    },
    '水': {
        'strong': 'คุณมีธาตุน้ำแข็งแรง — ฉลาด ปรับตัวเก่ง มีไหวพริบ '
                  'เหมาะกับงานที่ต้องเจรจา การค้า การทูต',
        'weak': 'คุณมีธาตุน้ำอ่อน — มีความคิดลึกซึ้งแต่ไม่กล้าแสดง '
                'ต้องการความมั่นใจมากขึ้น',
        'advice': 'เติมโลหะให้น้ำ: เรียนรู้เทคนิค เครื่องมือใหม่ๆ สร้างทักษะ',
    },
}


def _explain_sifu(bazi, inp):
    """อ่าน Ba Zi แบบซินแซ — ภาษาไทยธรรมชาติ เจาะลึกทุกมิติ"""
    dm = bazi.day_master
    dm_el = TIAN_GAN_ELEMENT.get(dm, '?')
    st = bazi.element_strength
    zodiac = bazi.get_zodiac_summary()
    month_zhi = bazi.month_pillar[1]
    season = MONTH_TO_SEASON.get(month_zhi, '?')

    dm_score = st[dm_el]
    others_sum = sum(v for e, v in st.items() if e != dm_el)
    is_strong = dm_score >= others_sum * 0.7
    max_elem = max(st, key=st.get)
    missing = [e for e, v in st.items() if v == 0]

    lines = []

    # ─────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────
    lines.append("🎋 พยากรณ์ดวงชาตา — BaZi (八字)")
    lines.append(f"   วันเกิด: {_describe_date(inp)}")
    lines.append("")

    # ─────────────────────────────────────────
    # Ⅰ. DAY MASTER
    # ─────────────────────────────────────────
    lines.append("━" * 40)
    lines.append("Ⅰ. DAY MASTER (日主) — แก่นแท้ของตัวตน")
    lines.append("━" * 40)
    persona = _DM_PERSONA.get(dm_el, '')
    lines.append(f"☀️ วันเกิดของคุณตรงกับ {dm} — ธาตุ{_E.get(dm_el, '?')}")
    lines.append(f"   {persona}")
    detail = _DM_DETAIL.get(dm_el, {})
    key = 'strong' if is_strong else 'weak'
    lines.append(f"   {detail.get(key, '')}")
    lines.append("")

    # ─────────────────────────────────────────
    # Ⅱ. FIVE ELEMENTS
    # ─────────────────────────────────────────
    lines.append("━" * 40)
    lines.append("Ⅱ. 五行 (Wu Xing) — สมดุลธาตุทั้งห้า")
    lines.append("━" * 40)
    lines.append(f"คะแนนธาตุจาก 4 เสา (0-4):")
    for e, v in sorted(st.items(), key=lambda x: -x[1]):
        lv, label = _elem_level(v)
        bar = "█" * lv + "░" * (7 - lv)
        mark = " ← DM" if e == dm_el else ""
        lines.append(f"   {_E[e]}: {v:.1f} {bar} ({label}){mark}")

    lines.append("")
    lines.append(f"📊 สรุป: ")
    lines.append(f"   • DM ({_E[dm_el]}) = {dm_score:.1f} | ธาตุเด่นสุด = {_E[max_elem]} ({st[max_elem]:.1f})")
    if missing:
        lines.append(f"   • ❌ ขาด: {', '.join(_E[e] for e in missing)} — ต้องหาจากภายนอก (คนรอบข้าง สภาพแวดล้อม)")
    lines.append(f"   • ฤดูกาลเกิด: {month_zhi} → {_E[season]}")

    # Interpretation of balance
    lines.append("")
    lines.append("🔍 ตีความสมดุล:")
    if max_elem == dm_el and st[max_elem] >= 2.0:
        lines.append(f"   DM เด่น = พลังตัวเองสูง กล้าแสดงออก มีความมั่นใจ")
    elif max_elem != dm_el and st[max_elem] >= st[dm_el] + 0.5:
        lines.append(f"   ธาตุ '{_E[max_elem]}' แรงกว่า DM — ชีวิตได้รับอิทธิพลจากปัจจัยภายนอกมาก")
    lines.append(f"   {_interpret_element_balance(st, dm_el)}")
    lines.append("")

    # ─────────────────────────────────────────
    # Ⅲ. FOUR PILLARS
    # ─────────────────────────────────────────
    lines.append("━" * 40)
    lines.append("Ⅲ. 四柱 — วิเคราะห์ 4 เสาแห่งชีวิต")
    lines.append("━" * 40)

    pillars = [
        ('ปี', 'วัยเด็ก | ครอบครัว | บรรพบุรุษ', bazi.year_pillar),
        ('เดือน', 'วัยทำงาน | สังคม | เพื่อนร่วมงาน', bazi.month_pillar),
        ('วัน', 'ตัวตน | คู่ครอง | ชีวิตคู่', bazi.day_pillar),
        ('เวลา', 'บั้นปลาย | บริวาร | ลูกหลาน', bazi.hour_pillar),
    ]
    for name, area, pillar in pillars:
        gan = pillar[0]; zhi = pillar[1]
        god = bazi._gan_god(gan)
        ge = _E.get(TIAN_GAN_ELEMENT.get(gan, '?'), '?')
        ze = _E.get(DI_ZHI_MAIN_ELEMENT.get(zhi, '?'), '?')
        hidden = HIDDEN_STEMS.get(zhi, [])
        hs_list = [f"{s}({_E.get(TIAN_GAN_ELEMENT.get(s,'?'),'?')})={bazi._gan_god(s)}" for s in hidden]
        marker = " ◀ DM" if gan == dm else ""

        lines.append(f"")
        lines.append(f"  [{name}] {pillar} — {area}")
        lines.append(f"    天干: {gan} ({ge}) → {god}{marker}")
        lines.append(f"    地支: {zhi} ({ze})")
        lines.append(f"    藏干: {', '.join(hs_list)}")
        lines.append(f"    → {_interpret_pillar(name, gan, zhi, god, bazi, st)}")

    lines.append("")

    # ─────────────────────────────────────────
    # Ⅳ. BODY STRENGTH
    # ─────────────────────────────────────────
    lines.append("━" * 40)
    lines.append("Ⅳ. 身强/弱 — กำลังภายใน")
    lines.append("━" * 40)
    lines.append(f"   DM ({_E[dm_el]}) = {dm_score:.1f}")
    lines.append(f"   ธาตุอื่นรวม = {others_sum:.1f}")
    ratio = dm_score / max(others_sum, 0.01)
    lines.append(f"   อัตราส่วน = {ratio:.2f}")
    lines.append("")

    if is_strong:
        lines.append("   ✅ 身强 — พลังภายในแข็งแกร่ง (Strong Body)")
        lines.append(f"   คุณมีพลัง DM ({_E[dm_el]}) สูงกว่าธาตุอื่น — ")
        lines.append(f"   มั่นคงในตัวเอง กล้าตัดสินใจ มีบารมี ไม่หวั่นไหวง่าย")
        lines.append(f"")
        if dm_el == '火':
            lines.append("   ชอบธาตุระบาย: ดิน(食傷) โลหะ(財) น้ำ(官) — ช่วยลด heat")
            lines.append("   ระวังธาตุเสริม: ไม้(印) ไฟ(比劫) — ทำให้ร้อนแรงเกินไป")
        elif dm_el == '木':
            lines.append("   ชอบธาตุระบาย: ไฟ(食傷) ดิน(財) — ใช้พลังสร้างสรรค์")
            lines.append("   ระวังธาตุเสริม: น้ำ(印) ไม้(比劫) — ทำให้แข็งทื่อเกินไป")
        elif dm_el == '土':
            lines.append("   ชอบธาตุระบาย: โลหะ(食傷) น้ำ(財) — ใช้พลังผลิตผล")
            lines.append("   ระวังธาตุเสริม: ไฟ(印) ดิน(比劫) — ทำให้หมักหมม")
        elif dm_el == '金':
            lines.append("   ชอบธาตุระบาย: น้ำ(食傷) ไม้(財) — ใช้ความเฉียบคม")
            lines.append("   ระวังธาตุเสริม: ดิน(印) โลหะ(比劫) — ทำให้แข็งกร้าว")
        else:  # 水
            lines.append("   ชอบธาตุระบาย: ไม้(食傷) ไฟ(財) — ใช้ปัญญาสร้างสรรค์")
            lines.append("   ระวังธาตุเสริม: โลหะ(印) น้ำ(比劫) — ทำให้ท่วมท้น")
    else:
        lines.append("   ⚠️ 身弱 — พลังภายในอ่อน (Weak Body)")
        lines.append(f"   DM ({_E[dm_el]}) = {dm_score:.1f} น้อยกว่าธาตุอื่นรวม {others_sum:.1f}")
        lines.append(f"   คุณมีพลัง DM อ่อน — ชีวิตมักถูกปัจจัยภายนอกครอบงำ")
        lines.append(f"   ต้องพยายามมากกว่าคนอื่นเพื่อให้ได้ผลลัพธ์เท่ากัน")
        lines.append(f"")
        if dm_el == '火':
            lines.append("   ชอบธาตุเสริม: ไม้(印) ไฟ(比劫) — เพิ่มกำลัง DM")
            lines.append("   ระวังธาตุระบาย: ดิน(食傷) โลหะ(財) น้ำ(官) — ยิ่งอ่อนลง")
        elif dm_el == '木':
            lines.append("   ชอบธาตุเสริม: น้ำ(印) ไม้(比劫) — เพิ่มกำลัง DM")
            lines.append("   ระวังธาตุระบาย: ไฟ(食傷) ดิน(財) — สูญเสียพลัง")
        elif dm_el == '土':
            lines.append("   ชอบธาตุเสริม: ไฟ(印) ดิน(比劫) — เพิ่มกำลัง DM")
            lines.append("   ระวังธาตุระบาย: โลหะ(食傷) น้ำ(財) — ยิ่งอ่อนลง")
        elif dm_el == '金':
            lines.append("   ชอบธาตุเสริม: ดิน(印) โลหะ(比劫) — เพิ่มกำลัง DM")
            lines.append("   ระวังธาตุระบาย: น้ำ(食傷) ไม้(財) — ยิ่งลดพลัง")
        else:
            lines.append("   ชอบธาตุเสริม: โลหะ(印) น้ำ(比劫) — เพิ่มกำลัง DM")
            lines.append("   ระวังธาตุระบาย: ไม้(食傷) ไฟ(財) — ยิ่งกระจายพลัง")

    lines.append("")

    # ─────────────────────────────────────────
    # Ⅴ. LIFE GUIDANCE
    # ─────────────────────────────────────────
    lines.append("━" * 40)
    lines.append("Ⅴ. ข้อแนะนำจากดวงชะตา")
    lines.append("━" * 40)

    lines.append(f"")
    lines.append(f"🔮 {zodiac['year_zodiac']} — ปีนักษัตร")
    lines.append(f"   สามเกลอ(三合): {', '.join(zodiac['zodiac_mark3'])}")
    lines.append(f"   หกเกลอ(六合): {zodiac['zodiac_win']}")
    lines.append(f"   ทะลวง(六冲): {zodiac['zodiac_lose']}")
    lines.append(f"")

    lines.append(f"💡 ข้อแนะนำ:")
    if missing:
        lines.append(f"   • เติมธาตุที่ขาด ({', '.join(_E[e] for e in missing)}): {_ELEMENT_FIX.get(missing[0], '')}")
    lines.append(f"   • 身{'强' if is_strong else '弱'} — {'ใช้พลังที่มีให้เกิดประโยชน์' if is_strong else 'เสริมกำลัง DM ก่อนแล้วค่อยขยาย'}")

    strongest_name = _E.get(max_elem, '?')
    lines.append(f"   • {ELEMENT_ADVICE_TH.get(max_elem, '')}")
    lines.append(f"   • หกเกลอ{zodiac['zodiac_win']}: คนปี{zodiac['zodiac_win']}เป็นมิตรกับคุณ")

    lines.append(f"")
    lines.append(f"📈 จุดเด่น:")
    if st[max_elem] >= 2.0:
        lines.append(f"   ✅ {_E[max_elem]}เด่น ({st[max_elem]:.1f}) — มีพลังด้านนี้สูง")
    if is_strong:
        lines.append(f"   ✅ 身强 — มั่นคง ไม่หวั่นไหวง่าย")
    if st['土'] >= 1.5:
        lines.append(f"   ✅ 食傷เด่น — มีพรสวรรค์ด้านศิลปะ การพูด")
    lines.append(f"")
    lines.append(f"📉 จุดที่ควรพัฒนา:")
    if not is_strong:
        lines.append(f"   ⚠️ 身弱 — ฝึกความมั่นใจ อย่ากลัวที่จะขอความช่วยเหลือ")
    if st[dm_el] <= 1.0:
        lines.append(f"   ⚠️ DM ({_E[dm_el]}) อ่อน — ฝึกสมาธิ สร้างกำลังภายใน")
    if '金' in missing:
        lines.append(f"   ⚠️ ขาดโลหะ — อาจขาดความเด็ดขาด ฝึก decision making")
    lines.append(f"")

    return "\n".join(lines)


def _interpret_element_balance(st, dm_el):
    """ตีความสมดุลธาตุ"""
    max_elem = max(st, key=st.get)
    min_elem = min(st, key=st.get)

    if all(v == 0 for v in st.values()):
        return "ไม่มีข้อมูลเพียงพอ"

    # หาค่าเฉลี่ยธาตุที่มีค่า > 0
    non_zero = {e: v for e, v in st.items() if v > 0}
    if len(non_zero) >= 4:
        return "ธาตุค่อนข้างสมดุล มีหลายธาตุโดดเด่น ชีวิตมีหลายมิติ"
    if len(non_zero) <= 2:
        return f"ธาตุไม่สมดุล มีเพียง {', '.join(_E[e] for e in non_zero)} ที่มีนัยสำคัญ — \
ชีวิตมีทิศทางชัดเจนแต่อาจขาดความยืดหยุ่น"

    if max_elem == dm_el and st[max_elem] >= 2.0:
        return f"DM ({_E[dm_el]}) เด่น—มีพลังในตัวเองสูง กล้าแสดงออก แต่ระวัง ego เกินไป"
    if st[dm_el] <= 0.5:
        return f"DM ({_E[dm_el]}) อ่อนมาก—ขาดความมั่นใจ ต้องพึ่งคนอื่นบ่อย \
ควรเสริม{_E[dm_el]}เพื่อสร้างกำลังภายใน"

    return "ธาตุโดยรวมอยู่ในเกณฑ์ปกติ สามารถปรับสมดุลได้"


def _interpret_pillar(name, gan, zhi, god, bazi, st):
    """ตีความแต่ละเสา"""
    gan_el = TIAN_GAN_ELEMENT.get(gan, '?')
    zhi_el = DI_ZHI_MAIN_ELEMENT.get(zhi, '?')
    dm_el = TIAN_GAN_ELEMENT.get(bazi.day_master, '?')

    if name == 'ปี':
        if god in ("正印", "偏印"):
            return "วัยเด็กได้รับการเลี้ยงดูที่ดี มีผู้ใหญ่คอยอุปถัมภ์"
        if god in ("七杀", "劫财"):
            return "วัยเด็กมีอุปสรรคหรือแรงกดดันจากครอบครัว ทำให้แกร่งตั้งแต่เด็ก"
        if god in ("正财", "偏财"):
            return "ครอบครัวมีฐานะมั่นคง ได้รับการเลี้ยงดูอย่างดี"
        if god in ("食神", "伤官"):
            return "วัยเด็กมีอิสระทางความคิด ได้รับการส่งเสริมด้านศิลปะหรือการศึกษา"
        return "วัยเด็กมีพัฒนาการตามเกณฑ์ ได้รับอิทธิพลจากสภาพแวดล้อมรอบตัว"

    if name == 'เดือน':
        if god in ("正官", "七杀"):
            return "วัยทำงานมีอำนาจ ความรับผิดชอบสูง เป็นที่ยอมรับในสังคม"
        if god in ("正财", "偏财"):
            return "รายได้ดีจากการทำงาน วางแผนการเงินเก่ง มีลู่ทางก้าวหน้า"
        if god in ("食神", "伤官"):
            return "เหมาะกับงานสร้างสรรค์ ศิลปะ การสื่อสาร งานที่ไม่จำเจ"
        if god in ("正印", "偏印"):
            return "วัยทำงานได้รับการสนับสนุนจากผู้ใหญ่ การศึกษาดี ทำงานในระบบ"
        return "วัยทำงานต้องสร้างเนื้อสร้างตัวด้วยตัวเอง"

    if name == 'วัน':
        zhi_hidden = HIDDEN_STEMS.get(zhi, [])
        if gan == bazi.day_master:
            return f"DM ซ้อนวัน — มีบารมีในตัวเอง คนรอบข้างยอมรับ \
{zhi}({_E.get(zhi_el, '?')}) ซ่อน {', '.join(_E.get(TIAN_GAN_ELEMENT.get(s,'?'),'?') for s in zhi_hidden)}"
        if god in ("正财", "偏财"):
            return f"คู่ครองหรือหุ้นส่วนมีส่วนช่วยด้านการเงิน \
{zhi}({_E.get(zhi_el, '?')}) ซ่อน {', '.join(_E.get(TIAN_GAN_ELEMENT.get(s,'?'),'?') for s in zhi_hidden)}"
        if god in ("正官", "七杀"):
            return f"คู่ครองมีวุฒิภาวะ ความรับผิดชอบ \
{zhi}({_E.get(zhi_el, '?')}) ซ่อน {', '.join(_E.get(TIAN_GAN_ELEMENT.get(s,'?'),'?') for s in zhi_hidden)}"
        return f"{zhi}({_E.get(zhi_el, '?')}) ซ่อน {', '.join(_E.get(TIAN_GAN_ELEMENT.get(s,'?'),'?') for s in zhi_hidden)}"

    if name == 'เวลา':
        if god in ("食神", "伤官"):
            return "บั้นปลายมีความสุข ลูกหลานดี มีผลงานเป็นที่ยอมรับ"
        if god in ("正印", "偏印"):
            return "บั้นปลายมีปัญญา สุขสงบ ได้รับการยกย่อง"
        if god in ("正财", "偏财"):
            return "บั้นปลายร่ำรวย ทรัพย์สินมั่นคง ลูกหลานสบาย"
        if god in ("正官", "七杀"):
            return "บั้นปลายมีเกียรติยศ เป็นที่เคารพนับถือ"
        return "บั้นปลายชีวิตมีสิ่งดีๆ รออยู่ ขึ้นอยู่กับการใช้ชีวิตช่วงต้น"


_ELEMENT_FIX = {
    '木': 'หาความรู้ เรียนหนังสือ มี mentor สีเขียว ปลูกต้นไม้',
    '火': 'ออกกำลังกาย เข้าสังคม ใส่สีแดง/ส้ม ทำงานอดิเรก',
    '土': 'สร้างวินัย ทำกิจวัตรประจำวัน ใส่สีเหลือง/น้ำตาล',
    '金': 'ฝึก decision making วางระบบ ใส่สีขาว/ทอง',
    '水': 'พักผ่อน นั่งสมาธิ ใส่สีดำ/น้ำเงิน การเดินทาง',
}


def _describe_date(text):
    """ดึงวันที่มาจากข้อความแบบสวยๆ"""
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        d, mo, y = m.groups()
        th_months = {1:'ม.ค.',2:'ก.พ.',3:'มี.ค.',4:'เม.ย.',5:'พ.ค.',6:'มิ.ย.',
                     7:'ก.ค.',8:'ส.ค.',9:'ก.ย.',10:'ต.ค.',11:'พ.ย.',12:'ธ.ค.'}
        month_name = th_months.get(int(mo), '')
        return f"วันที่ {d} {month_name} {int(y)+543} เวลา{_describe_time(text)} น."
    return text


def _describe_time(text):
    m = re.search(r"(\d{1,2})[.:](\d{1,2})", text)
    if m:
        return f"{m.group(1)}:{m.group(2)}"
    return "ไม่ระบุเวลา"


def bazi_handler(action: str, inp: str, entities: list) -> dict:
    """
    วิเคราะห์ Ba Zi จากวันเดือนปีเกิด
    รูปแบบ: "วันที่ เดือน ปี ชั่วโมง นาที" เช่น "8/8/1992 16.49" หรือ "8/8/1992 16:49"
    เพิ่ม "ละเอียด" หรือ "ten god" เพื่อดู Ten Gods + Hidden Stems แบบเต็ม
    เพิ่ม "ซินแซ" หรือ "อธิบาย" เพื่อคำอธิบายภาษาคน
    """
    if not _CNLUNAR_AVAILABLE:
        return {"status": "fail", "message": "ต้องติดตั้ง cnlunar ก่อน (pip install cnlunar)"}

    dt = _parse_datetime(inp)
    if dt is None:
        return {"status": "fail", "message": "ไม่รู้จักรูปแบบวันที่ กรุณาระบุเช่น 8/8/1992 16.49"}

    try:
        bazi = BaZi(dt)
        zodiac = bazi.get_zodiac_summary()
        inp_lower = inp.lower()
        is_sifu = any(w in inp_lower for w in ["ซินแซ", "อธิบาย", "แปล", "ซินแส", "sifu", "อ่าน"])
        is_detailed = any(w in inp_lower for w in ["ละเอียด", "ten god", "藏干", "十神", "detail", "hidden", "full"]) or is_sifu

        in_mark3 = "✓" if zodiac['year_zodiac'] in zodiac['zodiac_mark3'] else "✗"
        short_summary = f"{zodiac['year_zodiac']} 3 {zodiac['zodiac_win']} 1"

        if is_sifu:
            result = _explain_sifu(bazi, inp)
            return {"status": "success", "result": result, "direct_response": True}
        elif is_detailed:
            pillar_data = []
            for name, pillar in [('ปี', bazi.year_pillar), ('เดือน', bazi.month_pillar), ('วัน', bazi.day_pillar), ('เวลา', bazi.hour_pillar)]:
                gan, zhi = pillar[0], pillar[1]
                god = bazi._gan_god(gan)
                gan_el = TIAN_GAN_ELEMENT.get(gan, '?')
                zhi_el = DI_ZHI_MAIN_ELEMENT.get(zhi, '?')
                hidden = HIDDEN_STEMS.get(zhi, [])
                hidden_str = ", ".join(f"{s}({TIAN_GAN_ELEMENT.get(s,'?')})={bazi._gan_god(s)}" for s in hidden)
                pillar_data.append((name, pillar, gan_el, zhi_el, god, hidden_str))

            # Element breakdown
            elem_lines = []
            for elem, val in sorted(bazi.element_strength.items(), key=lambda x: -x[1]):
                bar = "█" * int(val * 4)
                elem_lines.append(f"    {elem}: {val:.1f} {bar}")

            dm_el = TIAN_GAN_ELEMENT.get(bazi.day_master, '?')
            month_zhi = bazi.month_pillar[1]
            season = MONTH_TO_SEASON.get(month_zhi, '?')

            result = (
                f"🔮 {short_summary}\n"
                f"{'═' * 35}\n"
                f"ปีนักษัตร: {zodiac['year_zodiac']} | "
                f"สามเกลอ: {', '.join(zodiac['zodiac_mark3'])} {in_mark3} | "
                f"หกเกลอ: {zodiac['zodiac_win']} | "
                f"ทะลวง: {zodiac['zodiac_lose']}\n"
                f"{'═' * 35}\n"
                f"DAY MASTER (วันจร): {bazi.day_master} ({dm_el})\n"
                f"{'═' * 35}\n"
            )
            for n, p, ge, ze, god, hs in pillar_data:
                marker = " ◀ DM" if p[0] == bazi.day_master else ""
                result += (
                    f"  {n}: {p}\n"
                    f"    {p[0]}({ge}) + {p[1]}({ze}) → {god}{marker}\n"
                    f"    Hidden Stems: {hs}\n"
                )

            result += (
                f"{'═' * 35}\n"
                f"ธาตุ (Element Strength):\n"
                + "\n".join(elem_lines) + "\n"
                f"  ฤดูกาล: {month_zhi} → {season} (+0.5)\n"
                f"  DM {bazi.day_master}({dm_el}) ต้องการ: "
                + {
                    '木': '火มีไม้ค้ำ → ต้องการ 木 เสริม',
                    '火': '火แรงไป → ต้องการ 土/金 ระบาย',
                    '土': '土适中 → ต้องการ 金泄秀',
                    '金': '金เกิน → ต้องการ 火克制',
                    '水': '水缺 → ต้องการ 金生水',
                }.get(dm_el, 'สมดุล') + "\n"
                f"{'═' * 35}"
            )
        else:
            el = {'火':'ไฟ','水':'น้ำ','木':'ไม้','金':'โลหะ','土':'ดิน'}
            dm_el = TIAN_GAN_ELEMENT.get(bazi.day_master, '?')
            month_zhi = bazi.month_pillar[1]
            season = MONTH_TO_SEASON.get(month_zhi, '?')
            def _elem_bar(val):
                n = min(int(val * 2), 8)
                return '█' * n + '░' * (8 - n)
            elem_bars = "\n".join(
                f"  {el.get(e, e)}: {v:.1f} {_elem_bar(v)}"
                for e, v in sorted(bazi.element_strength.items(), key=lambda x: -x[1])
            )
            strongest_elem = max(bazi.element_strength, key=bazi.element_strength.get)
            missing_elems = [e for e, v in bazi.element_strength.items() if v == 0]

            body = "身强 (Strong)" if bazi.element_strength[dm_el] >= sum(v for e, v in bazi.element_strength.items() if e != dm_el) * 0.7 else "身弱 (Weak)"

            pillar_info = []
            for name, pillar in [('ปี', bazi.year_pillar), ('เดือน', bazi.month_pillar), ('วัน', bazi.day_pillar), ('เวลา', bazi.hour_pillar)]:
                gan, zhi = pillar[0], pillar[1]
                god = bazi._gan_god(gan)
                ge = TIAN_GAN_ELEMENT.get(gan, '?')
                ze = DI_ZHI_MAIN_ELEMENT.get(zhi, '?')
                marker = " ◀ DM" if gan == bazi.day_master else ""
                pillar_info.append(f"  {name}: {gan}{zhi} | {gan}({ge})+{zhi}({ze}) → {god}{marker}")

            zodiac_emoji = {'หนู':'🐭','วัว':'🐮','เสือ':'🐯','กระต่าย':'🐰','มังกร':'🐲','งู':'🐍','ม้า':'🐴','แพะ':'🐑','ลิง':'🐵','ไก่':'🐔','หมา':'🐶','หมู':'🐷'}
            result = (
                f"🎋 {_describe_date(inp)}\n"
                f"{'─' * 36}\n"
                f"{zodiac_emoji.get(zodiac['year_zodiac'], '🐭')} {zodiac['year_zodiac']} | "
                f"三合 {', '.join(zodiac['zodiac_mark3'])} "
                f"| 六合 {zodiac['zodiac_win']} | 相冲 {zodiac['zodiac_lose']}\n"
                f"  🏆 {short_summary}\n"
                f"{'─' * 36}\n"
                f"☀️ DM {bazi.day_master}({dm_el}) — {body}\n"
                f"\n"
                f"📜 เสาทั้งสี่:\n"
                + "\n".join(pillar_info) + "\n"
                f"\n"
                f"🔥 ธาตุ:\n"
                f"{elem_bars}\n"
                f"  ฤดู: {month_zhi}({el.get(season, season)}) | "
                f"เด่น: {el.get(strongest_elem, strongest_elem)}\n"
            )
            if missing_elems:
                result += f"  ขาด: {', '.join(el.get(e, e) for e in missing_elems)} ⚠️\n"
            result += (
                f"{'─' * 36}\n"
                f"💡 {ELEMENT_ADVICE_TH.get(strongest_elem, 'สมดุล')}\n"
            )
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "fail", "message": f"คำนวณ Ba Zi ไม่สำเร็จ: {type(e).__name__} - {str(e)}"}


def _parse_datetime(text: str) -> Optional[datetime.datetime]:
    """
    แปลงข้อความเป็น datetime object
    รองรับ: "8/8/1992 16.49", "8/8/1992 16:49", "8/8/1992"
    """
    text = text.strip().replace("น.", "").strip()
    
    # รองรับ "8/8/1992 16.49" หรือ "8/8/1992 16:49"
    pattern = r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2})[.:](\d{1,2})"
    m = re.search(pattern, text)
    if m:
        day, month, year, hour, minute = map(int, m.groups())
        return datetime.datetime(year, month, day, hour, minute)
    
    # รองรับ "8/8/1992" (ไม่มีเวลา)
    pattern2 = r"(\d{1,2})/(\d{1,2})/(\d{4})"
    m = re.search(pattern2, text)
    if m:
        day, month, year = map(int, m.groups())
        return datetime.datetime(year, month, day, 12, 0)
    
    # รองรับ "8 สิงหา 2535" หรือรูปแบบภาษาไทย
    thai_months = {
        'ม.ค.': 1, 'ก.พ.': 2, 'มี.ค.': 3, 'เม.ย.': 4, 'พ.ค.': 5, 'มิ.ย.': 6,
        'ก.ค.': 7, 'ส.ค.': 8, 'ก.ย.': 9, 'ต.ค.': 10, 'พ.ย.': 11, 'ธ.ค.': 12,
        'มกรา': 1, 'กุมภา': 2, 'มีนา': 3, 'เมษา': 4, 'พฤษภา': 5, 'มิถุนา': 6,
        'กรกฎา': 7, 'สิงหา': 8, 'กันยา': 9, 'ตุลา': 10, 'พฤศจิกา': 11, 'ธันวา': 12,
    }
    for name, num in thai_months.items():
        if name in text:
            parts = text.split()
            try:
                day_val = int(parts[0])
                year_val = int(parts[2]) if len(parts) > 2 else 2024
                if year_val > 2500:
                    year_val -= 543  # แปลง พ.ศ. → ค.ศ.
                return datetime.datetime(year_val, num, day_val, 12, 0)
            except (ValueError, IndexError):
                pass
    
    return None


# ============================================================
# Quick Test
# ============================================================
if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    birth = datetime.datetime(1992, 8, 8, 15, 30)  # local time
    bazi = BaZi(birth)
    print(bazi.report())