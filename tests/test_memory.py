"""Session memory and variable substitution."""

import pytest
from core.memory import (
    SessionMemory, extract_variables_from_result, substitute_variables_in_text,
)


def test_extract_sympy_solution():
    import sympy as sp

    x, y = sp.symbols("x y")
    result = [{x: -3, y: -8}, {x: 8, y: 3}]
    vars_found = extract_variables_from_result(result)
    assert vars_found == {"x": -3.0, "y": -8.0}


def test_substitute_skips_equation_like_strings_in_orchestrator_rule():
    """สมการที่มี '=' ไม่ควรถูกแทนค่า x จากเซสชันก่อนหน้า."""
    stored = {"x": -3.0, "y": -8.0}
    topic = "3^x=x^9"
    # orchestrator จะไม่เรียก substitute เมื่อมี '=' — ทดสอบพฤติกรรมที่ต้องการ
    assert "=" in topic
    assert substitute_variables_in_text(topic, stored) != topic  # ฟังก์ชันยังแทนได้
    # แต่ orchestrator ต้องไม่แทน (ทดสอบใน test_orchestrator)


def test_substitute_expression_without_equals():
    stored = {"x": 3.0, "y": 8.0}
    assert substitute_variables_in_text("x+y", stored) == "3.0+8.0"


class TestSessionMemory:
    def test_add_turn(self):
        mem = SessionMemory(max_history=3)
        mem.add_turn("hello", "hi")
        assert len(mem.history) == 1
        assert mem.history[0]["user"] == "hello"
        assert mem.history[0]["jinx"] == "hi"

    def test_max_history(self):
        mem = SessionMemory(max_history=3)
        for i in range(5):
            mem.add_turn(f"msg{i}", f"reply{i}")
        assert len(mem.history) == 3
        assert mem.history[0]["user"] == "msg2"

    def test_store_variables(self):
        mem = SessionMemory()
        mem.store_variables({"x": 5.0, "y": 3.0})
        assert mem.variables["x"] == 5.0
        assert mem.variables["y"] == 3.0

    def test_store_only_single_alpha(self):
        mem = SessionMemory()
        mem.store_variables({"x": 1.0, "total": 100.0, "abc": 50.0})
        assert "x" in mem.variables
        assert "total" not in mem.variables
        assert "abc" not in mem.variables

    def test_get_variable(self):
        mem = SessionMemory()
        mem.store_variables({"x": 42.0})
        assert mem.get_variable("x") == 42.0
        assert mem.get_variable("y") is None

    def test_context(self):
        mem = SessionMemory()
        mem.update_context("last_intent", "task:solve")
        assert mem.get_context("last_intent") == "task:solve"
        assert mem.get_context("missing", "default") == "default"

    def test_clear(self):
        mem = SessionMemory()
        mem.add_turn("a", "b")
        mem.store_variables({"x": 1.0})
        mem.clear()
        assert len(mem.history) == 0
        assert len(mem.variables) == 0

    def test_get_all_variables_str(self):
        mem = SessionMemory()
        assert mem.get_all_variables_str() == ""
        mem.store_variables({"x": 5.0, "y": 3.0})
        s = mem.get_all_variables_str()
        assert "x = 5.0" in s
        assert "y = 3.0" in s
