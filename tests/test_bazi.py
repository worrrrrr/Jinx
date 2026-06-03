"""Unit tests สำหรับ tools/bazi.py"""

import datetime
from tools.bazi import BaZi, _parse_datetime, _CNLUNAR_AVAILABLE

import pytest


@pytest.mark.skipif(not _CNLUNAR_AVAILABLE, reason="ต้องการ cnlunar")
class TestBaZi:
    def test_create_bazi(self):
        dt = datetime.datetime(1992, 8, 8, 16, 49)
        bazi = BaZi(dt)
        assert bazi.year_pillar == "壬申"
        assert bazi.month_pillar == "戊申"
        assert bazi.day_pillar == "丙辰"
        assert bazi.hour_pillar == "丙申"
        assert bazi.day_master == "丙"

    def test_element_strength(self):
        dt = datetime.datetime(1992, 8, 8, 16, 49)
        bazi = BaZi(dt)
        s = bazi.element_strength
        assert abs(sum(s.values()) - 8.5) < 0.01  # 4 pillars * 2 + season bonus

    def test_dominant_elements(self):
        dt = datetime.datetime(1992, 8, 8, 16, 49)
        bazi = BaZi(dt)
        dom = bazi.get_dominant_elements()
        assert len(dom) == 2
        assert dom[0][1] >= dom[1][1]

    def test_zodiac_summary(self):
        dt = datetime.datetime(1992, 8, 8, 16, 49)
        bazi = BaZi(dt)
        z = bazi.get_zodiac_summary()
        assert z["year_zodiac"] == "ลิง"
        assert "มังกร" in z["zodiac_mark3"] or "ลิง" in z["zodiac_mark3"]
        assert z["zodiac_win"] == "มังกร"

    def test_ten_gods(self):
        dt = datetime.datetime(1992, 8, 8, 16, 49)
        bazi = BaZi(dt)
        assert "year" in bazi.ten_gods
        assert "month" in bazi.ten_gods
        assert "day" in bazi.ten_gods
        assert "hour" in bazi.ten_gods

    def test_report_contains_all(self):
        dt = datetime.datetime(1992, 8, 8, 16, 49)
        bazi = BaZi(dt)
        r = bazi.report()
        assert "BaZi" in r or "Analysis" in r
        assert "壬申" in r
        assert "ลิง" in r


class TestParseDatetime:
    def test_full_datetime_dot(self):
        dt = _parse_datetime("8/8/1992 16.49")
        assert dt is not None
        assert dt.year == 1992
        assert dt.month == 8
        assert dt.day == 8
        assert dt.hour == 16
        assert dt.minute == 49

    def test_full_datetime_colon(self):
        dt = _parse_datetime("25/12/2023 10:30")
        assert dt is not None
        assert dt.year == 2023
        assert dt.month == 12
        assert dt.day == 25
        assert dt.hour == 10

    def test_date_only(self):
        dt = _parse_datetime("1/1/2000")
        assert dt is not None
        assert dt.hour == 12  # default noon

    def test_with_thai_suffix(self):
        dt = _parse_datetime("8/8/1992 16.49 น.")
        assert dt is not None
        assert dt.hour == 16

    def test_thai_month(self):
        dt = _parse_datetime("8 สิงหา 2535")
        assert dt is not None
        assert dt.year == 1992  # 2535 - 543
        assert dt.month == 8
        assert dt.day == 8

    def test_invalid(self):
        assert _parse_datetime("") is None
        assert _parse_datetime("abc") is None
