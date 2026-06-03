"""Integration tests — full perception→reasoning→execution→response pipeline."""

import pytest
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.orchestrator import Orchestrator


@pytest.fixture
def jinx():
    return Orchestrator()


def test_math_basic_arithmetic(jinx):
    reply = jinx.run("5 + 3")
    assert "8" in reply


def test_math_algebra(jinx):
    reply = jinx.run("x + 5 = 10")
    assert "5" in reply


def test_math_system(jinx):
    reply = jinx.run("x+y=12, 5y=1")
    assert "11.8" in reply or "11.80" in reply


def test_bazi_astrology(jinx):
    try:
        import cnlunar
        cnlunar  # suppress unused
    except ImportError:
        pytest.skip("ต้องติดตั้ง cnlunar ก่อน")
    reply = jinx.run("ดูดวง 8/8/1992 16.49")
    assert "ลิง" in reply
    assert "มังกร" in reply


def test_knowledge_search(jinx):
    reply = jinx.run("Python คืออะไร")
    assert "Python" in reply
    assert "title" not in reply


def test_html_generation(jinx):
    reply = jinx.run("สร้าง html ชื่อเรื่อง ทดสอบ")
    assert "<!DOCTYPE html>" in reply
    assert "ทดสอบ" in reply


def test_decision_tree(jinx):
    reply = jinx.run("tree food")
    assert "อาหาร" in reply or "ประเภท" in reply


def test_state_machine(jinx):
    reply = jinx.run("state coffee")
    assert "idle" in reply


def test_chat_greeting(jinx):
    reply = jinx.run("สวัสดี")
    assert "สวัสดี" in reply
    assert "ดี" in reply


def test_file_listing(jinx):
    reply = jinx.run("list_dir .")
    assert "tools" in reply or "core" in reply


def test_data_analysis(jinx):
    reply = jinx.run('analyze data [{"x":1,"y":2}]')
    assert "x" in reply and "y" in reply


def test_web_search_fallback(jinx):
    reply = jinx.run("ค้นหา ดาวอังคาร")
    assert "ดาวอังคาร" in reply


def test_response_no_raw_dict_leaks(jinx):
    """Response must not leak raw JSON/dict fields to user."""
    reply = jinx.run("Python คืออะไร")
    assert "title =" not in reply
    assert "snippet =" not in reply
    assert "status" not in reply.split()[0] if "status" in reply else True


def test_memory_persists_variables(jinx):
    jinx.run("x - y = 5")
    jinx.run("x + y = 15")
    assert "x" in jinx.memory.variables
    assert "y" in jinx.memory.variables


def test_identical_input_produces_correct_math(jinx):
    """Repeated identical input should produce correct result (random template may differ)."""
    r1 = jinx.run("5+3")
    r2 = jinx.run("5+3")
    assert "8" in r1
    assert "8" in r2
    # Core math result "8" must appear regardless of template randomization


def test_orchestrator_runs_all_engines(jinx):
    """Verify all 4 engines exist and run returns a string."""
    assert hasattr(jinx, "perception")
    assert hasattr(jinx, "reasoning")
    assert hasattr(jinx, "execution")
    assert hasattr(jinx, "response")
    reply = jinx.run("hello")
    assert isinstance(reply, str) and len(reply) > 0
