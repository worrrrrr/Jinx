"""Session memory and variable substitution."""

from core.memory import (
    extract_variables_from_result,
    substitute_variables_in_text,
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
