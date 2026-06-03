"""Unit tests สำหรับ ReasoningEngine."""

import pytest
from engines.reasoning import ReasoningEngine

@pytest.fixture
def engine():
    return ReasoningEngine()

class TestStrategySelection:
    def test_math_strategy(self, engine):
        plan = engine.plan({
            "action": "compute_math", "intent": "task:solve",
            "domain": "math", "entities": [], "topic": "x+y=12",
            "confidence": 0.9, "is_chitchat": False, "is_question": False,
        })
        assert "compute_math" in plan["tasks"]
        assert plan["status"] == "ready"

    def test_qa_strategy(self, engine):
        plan = engine.plan({
            "action": "answer_question", "intent": "qa:what",
            "domain": "qa", "entities": ["python"],
            "topic": "python คืออะไร", "confidence": 0.8,
            "is_chitchat": False, "is_question": True,
        })
        assert "search_knowledge" in plan["tasks"] or "parse_question" in plan["tasks"]
        assert plan["status"] == "ready"

    def test_chitchat_strategy(self, engine):
        plan = engine.plan({
            "action": "handle_conversation", "intent": "chat:chitchat",
            "domain": "conversation", "entities": [],
            "topic": "วันนี้ดีจัง", "confidence": 0.7,
            "is_chitchat": True, "is_question": False,
        })
        assert plan["domain"] == "conversation"

class TestContextRules:
    def test_low_confidence_adds_check(self, engine):
        plan = engine.plan({
            "action": "compute_math", "intent": "task:solve",
            "domain": "math", "entities": [], "topic": "x+y=12",
            "confidence": 0.5, "is_chitchat": False, "is_question": False,
        })
        assert "double_check_calculation" in plan["tasks"]

    def test_emotion_adds_empathy(self, engine):
        plan = engine.plan({
            "action": "handle_conversation", "intent": "chat:chitchat",
            "domain": "conversation", "entities": [],
            "topic": "วันนี้เครียดจัง", "confidence": 0.8,
            "is_chitchat": True, "is_question": False,
        })
        tasks = plan["tasks"]
        assert tasks[0] == "respond_empathy_first"

    def test_delete_file_requires_confirm(self, engine):
        """context rule ตรวจ 'file' ใน entity name — ใช้ entity ที่มี 'file'."""
        plan = engine.plan({
            "action": "delete_file", "intent": "task:delete",
            "domain": "file", "entities": ["my_file.txt"],
            "topic": "ลบ my_file.txt", "confidence": 0.9,
            "is_chitchat": False, "is_question": False,
        })
        assert "confirm_with_user" in plan["tasks"]

class TestResponseHint:
    def test_farewell_hint(self, engine):
        plan = engine.plan({
            "action": "respond_greeting", "intent": "chat:farewell",
            "domain": "conversation", "entities": [],
            "topic": "ลาก่อน", "confidence": 0.9,
            "is_chitchat": True, "is_question": False,
        })
        assert plan["response_hint"]["style"] == "warm"

    def test_qa_hint(self, engine):
        plan = engine.plan({
            "action": "answer_question", "intent": "qa:what",
            "domain": "qa", "entities": ["python"],
            "topic": "python คืออะไร", "confidence": 0.8,
            "is_chitchat": False, "is_question": True,
        })
        assert plan["response_hint"]["style"] == "informative"
