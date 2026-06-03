import unittest
from datetime import datetime
from astro import (
    compute_western_chart,
    compute_bazi_chart,
    compute_vedic_chart,
    synthesize_mbti_enneagram
)

test_data = [
    ("Elon Musk", datetime(1971,6,28,14,0,0), -25.7, 28.2, 2, "INTJ", "5w6", True),
    ("คุณ (8/8/1992)", datetime(1992,8,8,16,49,0), 6.5, 101.3, 7, "INFJ", "5w4", True),
    ("Suga (BTS)", datetime(1993,3,9,12,0,0), 35.87, 128.60, 9, "ISTP", "5w6", False),
    ("Woozi (SVT)", datetime(1996,11,22,12,0,0), 35.18, 129.08, 9, "INTJ", "1w9", False),
    ("V (BTS)", datetime(1995,12,30,12,0,0), 35.87, 128.60, 9, "INFP", "4w3", False),
    ("Kai (EXO)", datetime(1994,1,14,12,0,0), 37.57, 126.98, 9, "INFJ", "4w5", False),
    ("Wonwoo (SVT)", datetime(1996,7,17,12,0,0), 35.23, 128.68, 9, "INFP", "9w1", False),
    ("Mina (TWICE)", datetime(1997,3,24,12,0,0), 34.69, 135.18, 9, "ISFP", "9w1", False),
    ("Jihyo (TWICE)", datetime(1997,2,1,12,0,0), 37.59, 127.14, 9, "ESFP", "3w2", False),
    ("Jungkook (BTS)", datetime(1997,9,1,12,0,0), 35.18, 129.08, 9, "INTP", "9w8", False),
    ("Lisa (BLACKPINK)", datetime(1997,3,27,12,0,0), 14.99, 103.10, 7, "ESFJ", "7w6", False),
    ("Billie Eilish", datetime(2001,12,18,12,0,0), 34.05, -118.24, -8, "ISFP", "4w5", False),
]

def run_one_person(name, dt, lat, lon, tz, exp_mbti, exp_ennea, time_known):
    w = compute_western_chart(dt, lat, lon, tz)
    b = compute_bazi_chart(dt)
    v = compute_vedic_chart(dt, lat, lon, tz)
    
    # Debug เฉพาะ Elon กับคุณ
    if "Elon" in name or "8/8/1992" in name:
        print(f"\n=== BaZi Debug: {name} ===")
        print("Day Master:", b['day_master'])
        print("Strength:", b['day_master_strength'])
        print("Ten Gods:", b['ten_gods'])
        print("Wu Xing:", b['wu_xing_balance'])
        print("Branch Animals:", b['branch_animals'])
        print("==============================\n")
    
    final = synthesize_mbti_enneagram(b, w, v, time_known)
    return final['mbti'], final['enneagram']

class TestAstrology(unittest.TestCase):
    def test_person(self):
        mbti_correct = 0
        ennea_correct = 0
        total = len(test_data)
        
        for name, dt, lat, lon, tz, exp_mbti, exp_ennea, time_known in test_data:
            pred_mbti, pred_ennea = run_one_person(name, dt, lat, lon, tz, exp_mbti, exp_ennea, time_known)
            mbti_ok = (pred_mbti == exp_mbti)
            ennea_ok = (pred_ennea == exp_ennea)
            if mbti_ok: mbti_correct += 1
            if ennea_ok: ennea_correct += 1
            print(f"\n{name} {'(⏰ เกิดจริง)' if time_known else '(🕛 ใช้เที่ยง)'}")
            print(f"  MBTI: {pred_mbti} (expected {exp_mbti}) {'✅' if mbti_ok else '❌'}")
            print(f"  Enneagram: {pred_ennea} (expected {exp_ennea}) {'✅' if ennea_ok else '❌'}")
        
        mbti_acc = mbti_correct / total * 100
        ennea_acc = ennea_correct / total * 100
        print(f"\n{'='*50}")
        print(f"MBTI Accuracy: {mbti_correct}/{total} ({mbti_acc:.1f}%)")
        print(f"Enneagram Accuracy: {ennea_correct}/{total} ({ennea_acc:.1f}%)")

if __name__ == "__main__":
    unittest.main()