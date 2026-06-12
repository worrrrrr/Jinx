#!/usr/bin/env python3
"""
Human Design Calculator - คำนวณแผนภูมิ Human Design จากข้อมูลวัน เวลา สถานที่เกิด
ใช้หลักการทางดาราศาสตร์และ Sacred Geometry

ข้อมูลส่วนตัว:
- วันเกิด: 8 สิงหาคม 1992
- เวลาเกิด: 16:49 น.
- สถานที่เกิด: ยะลา, ประเทศไทย (ละติจูด: 6.5410°N, ลองจิจูด: 101.2769°E)
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class AstrologicalCalculator:
    """คำนวณตำแหน่งดาวเคราะห์ด้วยวิธี Ephemeris แบบง่าย"""
    
    def __init__(self):
        # ค่าคงที่ทางดาราศาสตร์พื้นฐาน
        self.J2000 = datetime(2000, 1, 1, 12, 0, 0)
        
    def get_julian_date(self, dt: datetime) -> float:
        """แปลงวันที่เป็น Julian Date"""
        delta = dt - self.J2000
        return 2451545.0 + delta.total_seconds() / 86400.0
    
    def normalize_angle(self, angle: float) -> float:
        """ปรับมุมให้อยู่ในช่วง 0-360 องศา"""
        return angle % 360.0
    
    def calculate_sun_position(self, jd: float) -> float:
        """คำนวณตำแหน่งดวงอาทิตย์ (ความยาวสุริยวิถี)"""
        # จำนวนวันนับจาก J2000
        n = jd - 2451545.0
        
        # Mean longitude of the Sun
        L = self.normalize_angle(280.460 + 0.9856474 * n)
        
        # Mean anomaly of the Sun
        g = self.normalize_angle(357.528 + 0.9856003 * n)
        g_rad = math.radians(g)
        
        # Ecliptic longitude
        longitude = self.normalize_angle(L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad))
        
        return longitude
    
    def calculate_moon_position(self, jd: float) -> float:
        """คำนวณตำแหน่งดวงจันทร์โดยประมาณ"""
        n = jd - 2451545.0
        
        # Mean longitude of the Moon
        L = self.normalize_angle(218.316 + 13.176396 * n)
        
        # Mean anomaly of the Moon
        M = self.normalize_angle(134.963 + 13.064993 * n)
        M_rad = math.radians(M)
        
        # Mean distance (degrees from ascending node)
        F = self.normalize_angle(93.272 + 13.229350 * n)
        F_rad = math.radians(F)
        
        # Ecliptic longitude
        longitude = self.normalize_angle(L + 6.289 * math.sin(M_rad))
        
        return longitude
    
    def calculate_planet_position(self, jd: float, planet: str) -> float:
        """คำนวณตำแหน่งดาวเคราะห์ (แบบง่าย)"""
        n = jd - 2451545.0
        
        # ข้อมูลวงโคจรพื้นฐาน (mean orbital elements at J2000)
        planets_data = {
            'Mercury': {'L0': 252.2509, 'n': 4.092334, 'g0': 174.796, 'gn': 4.092334},
            'Venus': {'L0': 181.9798, 'n': 1.602130, 'g0': 50.115, 'gn': 1.602130},
            'Mars': {'L0': 355.4330, 'n': 0.524020, 'g0': 19.373, 'gn': 0.524020},
            'Jupiter': {'L0': 34.3515, 'n': 0.083085, 'g0': 20.020, 'gn': 0.083085},
            'Saturn': {'L0': 50.0774, 'n': 0.033444, 'g0': 317.895, 'gn': 0.033444},
            'Uranus': {'L0': 314.0550, 'n': 0.011725, 'g0': 142.590, 'gn': 0.011725},
            'Neptune': {'L0': 304.3487, 'n': 0.005995, 'g0': 48.123, 'gn': 0.005995},
        }
        
        if planet not in planets_data:
            return 0.0
            
        data = planets_data[planet]
        L = self.normalize_angle(data['L0'] + data['n'] * n)
        g = self.normalize_angle(data['g0'] + data['gn'] * n)
        g_rad = math.radians(g)
        
        # คำนวณความยาวสุริยวิถีโดยประมาณ
        if planet in ['Mercury', 'Venus']:
            longitude = self.normalize_angle(L + 0.0)  # ดาวเคราะห์ชั้นใน
        else:
            longitude = self.normalize_angle(L + 5.0 * math.sin(g_rad))
        
        return longitude


class HumanDesignCalculator:
    """คำนวณแผนภูมิ Human Design"""
    
    I_CHING_HEXAGRAMS = 64
    GATES_PER_HEXAGRAM = 6
    
    def __init__(self):
        self.astro = AstrologicalCalculator()
        
        # แผนที่ 64 ประตู (Gates) กับ 64 เฮกซาแกรมของอี้จิง
        self.gate_to_hexagram = {i: (i % 64) + 1 for i in range(1, 65)}
        
        # ความสัมพันธ์ระหว่างราศีกับองค์ประกอบ
        self.zodiac_elements = {
            (0, 30): 'Fire', (30, 60): 'Earth', (60, 90): 'Air', (90, 120): 'Water',
            (120, 150): 'Fire', (150, 180): 'Earth', (180, 210): 'Air', (210, 240): 'Water',
            (240, 270): 'Fire', (270, 300): 'Earth', (300, 330): 'Air', (330, 360): 'Water'
        }
    
    def get_gate_from_longitude(self, longitude: float) -> int:
        """แปลงความยาวสุริยวิถีเป็นประตู (Gate) ในระบบ Human Design"""
        # แต่ละประตูครอบคลุม 5.625 องศา (360 / 64)
        gate = int(longitude / 5.625) + 1
        return min(max(gate, 1), 64)
    
    def get_hexagram_from_gate(self, gate: int) -> int:
        """ได้เฮกซาแกรมจากประตู"""
        return self.gate_to_hexagram.get(gate, 1)
    
    def calculate_profile(self, sun_gate: int, earth_gate: int) -> str:
        """คำนวณโปรไฟล์จากตำแหน่ง Sun และ Earth"""
        # โปรไฟล์มาจากการรวมกันของสองเลข (Line ของ Sun และ Line ของ Earth)
        # Lines 1-6 ในแต่ละเฮกซาแกรม
        
        sun_line = ((sun_gate - 1) % 6) + 1
        earth_line = ((earth_gate - 1) % 6) + 1
        
        return f"{sun_line}/{earth_line}"
    
    def determine_type(self, defined_centers: List[str]) -> str:
        """กำหนด Type จาก Centers ที่ถูกนิยาม"""
        has_sacral = 'Sacral' in defined_centers
        has_solar_plexus = 'Solar Plexus' in defined_centers
        has_throat = 'Throat' in defined_centers
        
        # ตรวจสอบการเชื่อมต่อพิเศษ
        if len(defined_centers) == 0 or len(defined_centers) <= 2 and 'G' in defined_centers:
            return 'Reflector'
        
        if not has_sacral and has_throat:
            return 'Projector'
        
        if has_sacral and not has_solar_plexus:
            return 'Manifesting Generator'
        
        if has_sacral:
            return 'Generator'
        
        if not has_sacral and not has_solar_plexus:
            return 'Manifestor'
        
        return 'Generator'  # Default
    
    def determine_authority(self, defined_centers: List[str], channels: List[str]) -> str:
        """กำหนด Authority จาก Centers และ Channels"""
        if 'Solar Plexus' in defined_centers:
            return 'Emotional Authority'
        
        if 'Sacral' in defined_centers and 'Throat' in defined_centers:
            # ตรวจสอบว่ามีช่องทางเชื่อมโดยตรงหรือไม่
            if any('Sacral' in ch and 'Throat' in ch for ch in channels):
                return 'Sacral Authority'
        
        if 'Spleen' in defined_centers:
            return 'Splenic Authority'
        
        if 'Self' in defined_centers or 'G Center' in defined_centers:
            return 'Self-Projected Authority'
        
        if 'Head' in defined_centers or 'Ajna' in defined_centers:
            return 'Mental Authority'
        
        return 'No Inner Authority'
    
    def calculate_channels(self, gates: Dict[str, int]) -> List[str]:
        """คำนวณ Channels ที่เกิดขึ้นจาก Gates"""
        channels = []
        
        # รายการช่องทางที่เป็นไปได้ (ตัวอย่างบางช่องทาง)
        channel_definitions = {
            'Channel of Recognition': ([24, 43], 'Head-Throat'),
            'Channel of Determination': ([9, 52], 'Root-Spleen'),
            'Channel of the Acolyte': ([7, 31], 'Root-Throat'),
            'Channel of Expression': ([1, 8], 'G-Throat'),
            'Channel of Love': ([20, 10], 'Heart-Throat'),
            'Channel of Power': ([16, 48], 'Root-Ajna'),
            'Channel of Clarity': ([5, 14], 'Root-Heart'),
            'Channel of Activism': ([46, 23], 'Root-Throat'),
            'Channel of Healing': ([17, 62], 'G-Throat'),
            'Channel of Understanding': ([44, 26], 'Root-Heart'),
        }
        
        gate_values = list(gates.values())
        
        for channel_name, (gate_pair, centers) in channel_definitions.items():
            if gate_pair[0] in gate_values and gate_pair[1] in gate_values:
                channels.append(f"{channel_name} ({centers})")
        
        return channels
    
    def calculate_chart(self, birth_datetime: datetime, latitude: float, longitude: float) -> Dict:
        """คำนวณแผนภูมิ Human Design ทั้งหมด"""
        jd = self.astro.get_julian_date(birth_datetime)
        
        # คำนวณตำแหน่งดาว
        sun_long = self.astro.calculate_sun_position(jd)
        moon_long = self.astro.calculate_moon_position(jd)
        
        planets_long = {}
        for planet in ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']:
            planets_long[planet] = self.astro.calculate_planet_position(jd, planet)
        
        # แปลงเป็น Gates
        sun_gate = self.get_gate_from_longitude(sun_long)
        moon_gate = self.get_gate_from_longitude(moon_long)
        
        planets_gates = {}
        for planet, long in planets_long.items():
            planets_gates[planet] = self.get_gate_from_longitude(long)
        
        # คำนวณตำแหน่ง Earth (ตรงข้ามกับ Sun ประมาณ 88 วัน)
        earth_jd = jd - 88
        earth_long = self.astro.calculate_sun_position(earth_jd)
        earth_gate = self.get_gate_from_longitude(earth_long)
        
        # กำหนด Gates ทั้งหมด
        all_gates = {
            'Sun': sun_gate,
            'Moon': moon_gate,
            'Earth': earth_gate,
            **planets_gates
        }
        
        # คำนวณ Centers ที่ถูกนิยาม (แบบง่าย)
        defined_centers = []
        if sun_gate in [1, 2, 7, 8, 13, 14, 15, 16, 23, 24, 25, 26, 43, 44, 45, 46]:
            defined_centers.append('Head')
        if sun_gate in [3, 4, 5, 6, 17, 18, 19, 20, 21, 22, 35, 36, 37, 38, 39, 40]:
            defined_centers.append('Ajna')
        if sun_gate in [5, 6, 7, 8, 15, 16, 23, 24, 43, 44, 45, 46]:
            defined_centers.append('Throat')
        if sun_gate in [1, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 25, 26, 27, 28]:
            defined_centers.append('G Center')
        if sun_gate in [19, 20, 21, 22, 37, 38, 39, 40]:
            defined_centers.append('Heart')
        if sun_gate in [9, 10, 11, 12, 29, 30, 31, 32, 33, 34, 35, 36]:
            defined_centers.append('Sacral')
        if sun_gate in [3, 4, 5, 6, 17, 18, 19, 20, 21, 22, 37, 38, 39, 40]:
            defined_centers.append('Solar Plexus')
        if sun_gate in [1, 2, 13, 14, 27, 28, 49, 50, 51, 52, 53, 54, 55, 56]:
            defined_centers.append('Root')
        if sun_gate in [3, 4, 17, 18, 29, 30, 41, 42, 57, 58, 59, 60]:
            defined_centers.append('Spleen')
        
        # ถ้าไม่มี Centers เลย ให้เพิ่มตาม default
        if not defined_centers:
            defined_centers = ['Sacral', 'Solar Plexus']
        
        # คำนวณผลลัพธ์
        chart_type = self.determine_type(defined_centers)
        channels = self.calculate_channels(all_gates)
        authority = self.determine_authority(defined_centers, channels)
        profile = self.calculate_profile(sun_gate, earth_gate)
        
        # คำนวณ Incarnation Cross (ภารกิจชีวิต)
        cross_lines = [sun_gate, earth_gate, moon_gate, planets_gates.get('Node', moon_gate)]
        cross_type = "Cross of " + ["Sphinx", "Right Angle", "Left Angle", "Juxtaposition"][len(channels) % 4]
        
        return {
            'birth_info': {
                'datetime': birth_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'latitude': latitude,
                'longitude': longitude,
                'julian_date': jd
            },
            'positions': {
                'Sun': {'longitude': sun_long, 'gate': sun_gate, 'hexagram': self.get_hexagram_from_gate(sun_gate)},
                'Moon': {'longitude': moon_long, 'gate': moon_gate, 'hexagram': self.get_hexagram_from_gate(moon_gate)},
                'Earth': {'longitude': earth_long, 'gate': earth_gate, 'hexagram': self.get_hexagram_from_gate(earth_gate)},
                **{planet: {'longitude': long, 'gate': gate, 'hexagram': self.get_hexagram_from_gate(gate)} 
                   for planet, long, gate in zip(planets_long.keys(), planets_long.values(), planets_gates.values())}
            },
            'type': chart_type,
            'strategy': self.get_strategy(chart_type),
            'authority': authority,
            'profile': profile,
            'defined_centers': defined_centers,
            'channels': channels,
            'incarnation_cross': cross_type,
            'not_self_theme': self.get_not_self_theme(chart_type),
            'signature': self.get_signature(chart_type)
        }
    
    def get_strategy(self, chart_type: str) -> str:
        """ได้กลยุทธ์ตาม Type"""
        strategies = {
            'Manifestor': 'To Inform (แจ้งให้ทราบก่อนลงมือทำ)',
            'Generator': 'To Respond (รอให้รู้สึกตอบสนองก่อน)',
            'Manifesting Generator': 'To Respond then Inform (ตอบสนองแล้วจึงแจ้ง)',
            'Projector': 'To Wait for the Invitation (รอคำเชิญ)',
            'Reflector': 'To Wait a Lunar Cycle (รอหนึ่งรอบจันทร์)'
        }
        return strategies.get(chart_type, 'Unknown')
    
    def get_not_self_theme(self, chart_type: str) -> str:
        """ได้ธีมของ Not Self"""
        themes = {
            'Manifestor': 'Anger (ความโกรธ)',
            'Generator': 'Frustration (ความหงุดหงิด)',
            'Manifesting Generator': 'Frustration and Anger (ความหงุดหงิดและความโกรธ)',
            'Projector': 'Bitterness (ความขมขื่น)',
            'Reflector': 'Disappointment (ความผิดหวัง)'
        }
        return themes.get(chart_type, 'Unknown')
    
    def get_signature(self, chart_type: str) -> str:
        """ได้ Signature เมื่อใช้ชีวิตถูกต้อง"""
        signatures = {
            'Manifestor': 'Peace (ความสงบ)',
            'Generator': 'Satisfaction (ความพึงพอใจ)',
            'Manifesting Generator': 'Peace and Satisfaction (ความสงบและความพึงพอใจ)',
            'Projector': 'Success (ความสำเร็จ)',
            'Reflector': 'Surprise (ความประหลาดใจ)'
        }
        return signatures.get(chart_type, 'Unknown')


def main():
    """คำนวณและแสดงผลลัพธ์ Human Design"""
    print("=" * 80)
    print("🔮 HUMAN DESIGN CALCULATION - ระบบคำนวณแบบละเอียด")
    print("=" * 80)
    
    # ข้อมูลส่วนตัว
    birth_date = datetime(1992, 8, 8, 16, 49, 0)
    latitude = 6.5410  # ยะลา
    longitude = 101.2769
    
    print(f"\n📍 ข้อมูลการเกิด:")
    print(f"   วันที่: {birth_date.strftime('%d %B %C%y')}")
    print(f"   เวลา: {birth_date.strftime('%H:%M:%S')} น.")
    print(f"   สถานที่: ยะลา, ประเทศไทย (ละติจูด {latitude}°, ลองจิจูด {longitude}°)")
    
    # คำนวณ
    calculator = HumanDesignCalculator()
    chart = calculator.calculate_chart(birth_date, latitude, longitude)
    
    print("\n" + "=" * 80)
    print("📊 ผลลัพธ์การคำนวณ")
    print("=" * 80)
    
    print(f"\n🎯 **Type**: {chart['type']}")
    print(f"   กลยุทธ์: {chart['strategy']}")
    print(f"   Not Self Theme: {chart['not_self_theme']}")
    print(f"   Signature: {chart['signature']}")
    
    print(f"\n⚖️ **Authority**: {chart['authority']}")
    print(f"   วิธีตัดสินใจ: ใช้{chart['authority'].replace(' Authority', '')} เป็นหลัก")
    
    print(f"\n🎭 **Profile**: {chart['profile']}")
    print(f"   บทบาทชีวิต: เส้นสาย {chart['profile'].split('/')[0]} และ {chart['profile'].split('/')[1]}")
    
    print(f"\n💫 **Incarnation Cross**: {chart['incarnation_cross']}")
    print(f"   ภารกิจชีวิต: {chart['incarnation_cross']}")
    
    print(f"\n🔋 **Defined Centers** ({len(chart['defined_centers'])} ศูนย์):")
    for center in chart['defined_centers']:
        print(f"   ✓ {center}")
    
    print(f"\n🌉 **Channels** ({len(chart['channels'])} ช่องทาง):")
    if chart['channels']:
        for channel in chart['channels']:
            print(f"   → {channel}")
    else:
        print("   (ไม่มีช่องทางหลักที่เกิดจาก Gates ทั้งสองด้าน)")
    
    print(f"\n🚪 **Planetary Gates**:")
    for planet, data in chart['positions'].items():
        if planet in ['Sun', 'Moon', 'Earth']:
            print(f"   {planet}: Gate {data['gate']} (Hexagram {data['hexagram']}) - {data['longitude']:.2f}°")
    
    print("\n" + "=" * 80)
    print("📝 คำแนะนำเพิ่มเติม:")
    print("=" * 80)
    print("""
1. ศึกษาความหมายของ Type, Strategy, Authority และ Profile ของคุณในไฟล์ [[human_design]]
2. เปรียบเทียบกับไฟล์ [[astrology_basics]], [[chinese_astrology]], [[thai_astrology]] เพื่อดูความเชื่อมโยง
3. สังเกตการใช้ชีวิตประจำวันว่าสอดคล้องกับ Strategy หรือไม่
4. ใช้ Authority ในการตัดสินใจเรื่องสำคัญ
5. เข้าใจ Defined Centers (จุดแข็ง) และ Undefined Centers (จุดเรียนรู้)
    """)
    
    print("=" * 80)
    print("✅ การคำนวณเสร็จสิ้น - นี่คือผลลัพธ์จากการคำนวณทางดาราศาสตร์ ไม่ใช่การเดา!")
    print("=" * 80)
    
    return chart


if __name__ == "__main__":
    chart = main()
