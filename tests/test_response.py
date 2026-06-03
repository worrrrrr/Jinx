"""Unit tests สำหรับ ResponseEngine."""

import pytest
from engines.response import ResponseEngine

@pytest.fixture
def engine():
    return ResponseEngine()

class TestTemplateSelection:
    def test_success_uses_success_template(self, engine):
        text = engine.format({"status": "success", "result": 42, "message": "", "metadata": {}},
                             perception={"intent": "task:solve", "domain": "math", "topic": "2+2"})
        assert "42" in text

    def test_error_shows_message(self, engine):
        text = engine.format({"status": "error", "result": None, "message": "หารด้วยศูนย์", "metadata": {}},
                             perception={"intent": "task:solve", "domain": "math", "topic": "1/0"})
        assert "หาร" in text or "ข้อผิดพลาด" in text

    def test_chat_greeting(self, engine):
        text = engine.format({"status": "success", "result": "", "message": "", "metadata": {}},
                             perception={"intent": "chat:greet", "domain": "conversation", "topic": "สวัสดี"})
        assert "ครับ" in text or "ไง" in text

    def test_chat_farewell(self, engine):
        text = engine.format({"status": "success", "result": "", "message": "", "metadata": {}},
                             perception={"intent": "chat:farewell", "domain": "conversation", "topic": "ลาก่อน"})
        assert "ไว้" in text or "บ๊ายบาย" in text or "ใหม่" in text

    def test_qa_not_found(self, engine):
        text = engine.format({"status": "success", "result": "ไม่พบข้อมูลที่ตรงกับคำค้นหา", "message": "", "metadata": {}},
                             perception={"intent": "qa:what", "domain": "qa", "topic": "unknown"})
        assert "ไม่" in text or "ยังไม่มี" in text

class TestResultFormatting:
    def test_formats_integer(self, engine):
        assert "42" in engine._format_result_value(42)

    def test_formats_float(self, engine):
        result = engine._format_result_value(3.14)
        assert "3.14" in result

    def test_formats_approx_float(self, engine):
        result = engine._format_result_value(1.150825)
        assert "1.15" in result

    def test_formats_list_of_dicts(self, engine):
        result = engine._format_result_value([{"x": 8, "y": 4}, {"x": -3, "y": -9}])
        assert "x = 8" in result
        assert "หรือ" in result

    def test_formats_knowledge_hits(self, engine):
        hits = [{"title": "test.md", "snippet": "# Test Content", "source": "data/knowledge/test.md", "line_number": 1}]
        result = engine._format_result_value(hits)
        assert "test.md" in result or "Test" in result

    def test_empty_list(self, engine):
        result = engine._format_result_value([])
        assert "ไม่พบ" in result

class TestPersonality:
    def test_set_personality(self, engine):
        engine.set_personality(name="TestBot", tone="formal")
        assert engine.personality["name"] == "TestBot"
        assert engine.personality["tone"] == "formal"

    def test_emoji_level(self, engine):
        """Default emoji_level medium should add emoji."""
        text = engine.format({"status": "success", "result": "done", "message": "", "metadata": {}},
                             perception={"intent": "task:solve", "domain": "math", "topic": "test"})
        assert len(text) > 4
