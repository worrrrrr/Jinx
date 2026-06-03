"""End-to-end orchestrator scenarios from REPL issues."""

import pytest

from core.orchestrator import Orchestrator
from engines.response import ResponseEngine


@pytest.fixture
def jinx():
    return Orchestrator()


def test_qa_python_returns_readable_text(jinx):
    reply = jinx.run("Python คืออะไร")
    assert "python.md" in reply.lower() or "Python" in reply
    assert "title =" not in reply
    assert "snippet =" not in reply


def test_qa_typo_python_still_finds_knowledge(jinx):
    """fuzzy + alias จาก common.md ช่วยพิมพ์ผิด pythonn."""
    reply = jinx.run("pythonn คืออะไร")
    assert "ไม่พบ" not in reply or "python" in reply.lower()
    assert "python" in reply.lower()


def test_math_decimal_subtraction(jinx):
    reply = jinx.run("9.8-9.11")
    assert "0.69" in reply


def test_exponential_equation_after_prior_math_session(jinx):
    """หลังแก้ x,y แล้วถาม 3^x=x^9 ต้องไม่ได้คำตอบว่าง."""
    jinx.run("x-y=5, xy=24")
    reply = jinx.run("3^x=x^9")
    assert reply.strip()
    assert "27" in reply
    assert "LambertW" not in reply
    assert "≈" in reply
    assert "1.150" in reply


def test_linear_system_reply_uses_decimals(jinx):
    reply = jinx.run("x+y=12, 5y=1")
    assert "59/5" not in reply
    assert "11.8" in reply or "11.80" in reply


def test_memory_stores_variables(jinx):
    jinx.run("x-y=5, xy=24")
    assert "x" in jinx.memory.variables
    assert "y" in jinx.memory.variables


def test_response_formats_knowledge_hits():
    engine = ResponseEngine()
    hits = [
        {
            "title": "python.md",
            "snippet": "# Python Guide",
            "source": "data/knowledge/python.md",
            "line_number": 3,
        }
    ]
    text = engine._format_result_value(hits)
    assert "python" in text
    assert "Python Guide" in text
