"""Unit tests สำหรับ tools/html_gen.py"""

from tools.html_gen import generate_html_handler, _extract_title, _detect_template, _convert_to_html


class TestHtmlGen:
    def test_generate_simple_html(self):
        out = generate_html_handler("html", "ชื่อเรื่อง ทดสอบ\nย่อหน้าแรก", [])
        assert out["status"] == "success"
        assert "ทดสอบ" in out["result"]
        assert "<!DOCTYPE html>" in out["result"]
        assert out["title"] == "ทดสอบ"

    def test_generate_card_html(self):
        out = generate_html_handler("html", "สร้างการ์ด\nชื่อเรื่อง สวัสดี\nเนื้อหา", [])
        assert out["status"] == "success"
        assert "card" in out["template"] or "card" in out["result"]
        assert ".card" in out["result"]

    def test_generate_with_list(self):
        out = generate_html_handler("html", "รายการ\n- ส้ม\n- กล้วย", [])
        assert out["status"] == "success"
        assert "<ul>" in out["result"]
        assert "<li>ส้ม</li>" in out["result"]

    def test_no_content_fails(self):
        out = generate_html_handler("html", "", [])
        assert out["status"] == "fail"

    def test_extract_title_from_keyword(self):
        assert _extract_title("ชื่อเรื่อง Hello") == "Hello"
        assert _extract_title("หัวข้อ ทดสอบ\nเนื้อหา") == "ทดสอบ"
        assert _extract_title("title Test Page") == "Test Page"

    def test_detect_card_template(self):
        assert _detect_template("ทำการ์ด") == "card"
        assert _detect_template("card") == "card"
        assert _detect_template("ธรรมดา") == "simple"

    def test_convert_to_html_basic(self):
        html = _convert_to_html("ทดสอบ\nบรรทัดสอง", "ทดสอบ")
        assert "<p>ทดสอบ</p>" in html or "<p>บรรทัดสอง</p>" in html
