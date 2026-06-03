"""Unit tests สำหรับ PerceptionEngine."""

import pytest
from engines.perception import PerceptionEngine

@pytest.fixture
def engine():
    return PerceptionEngine()

class TestIntentDetection:
    def test_math_intent(self, engine):
        out = engine.perceive("9.8-9.11")
        assert out["intent"] == "task:solve"
        assert out["domain"] == "math"

    def test_search_intent(self, engine):
        out = engine.perceive("ค้นหา python คืออะไร")
        assert out["domain"] in ("web", "qa")

    def test_greeting_intent(self, engine):
        out = engine.perceive("สวัสดี")
        assert out["intent"] == "chat:greet"
        assert out["is_chitchat"] is True

    def test_create_file_intent(self, engine):
        out = engine.perceive("สร้างไฟล์ hello.py")
        assert out["domain"] == "code"

    def test_unknown_falls_to_chitchat(self, engine):
        out = engine.perceive("วันนี้อากาศดีจัง")
        assert out["domain"] in ("conversation", "general")

class TestThaiMathExtraction:
    def test_thai_add(self, engine):
        out = engine.perceive("5 บวก 3")
        assert out["domain"] == "math"
        assert "5+3" in out["topic"] or "5 + 3" in out["topic"]

    def test_thai_equation(self, engine):
        out = engine.perceive("x+y=12, 5y=1")
        assert out["domain"] == "math"
        assert "x+y=12" in out["topic"]

    def test_thai_word_problem(self, engine):
        out = engine.perceive("ถ้า x มากกว่า y อยู่ 5")
        assert out["domain"] == "math"
        assert "มากกว่า" not in out["topic"]

    def test_thai_multiply(self, engine):
        out = engine.perceive("7 คูณ 8")
        assert "7" in out["topic"] and "8" in out["topic"]

class TestDomainDetection:
    def test_file_domain(self, engine):
        out = engine.perceive("เปิดไฟล์ data.txt")
        assert out["domain"] in ("file", "general")

    def test_conversation_domain(self, engine):
        out = engine.perceive("สบายดีไหม")
        assert out["domain"] == "conversation"

    def test_qa_domain(self, engine):
        out = engine.perceive("อะไรคือ AI")
        assert "qa" in out["intent"]

class TestEntityExtraction:
    def test_extract_code_file(self, engine):
        out = engine.perceive("แก้ไขไฟล์ main.py")
        assert any("main.py" in e for e in out["entities"])

    def test_extract_url(self, engine):
        out = engine.perceive("เปิด https://example.com")
        assert any("https://example.com" in e for e in out["entities"])
