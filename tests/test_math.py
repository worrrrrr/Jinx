"""Math tool numeric and symbolic behavior."""

import pytest

from tools.math import compute_math_handler, _eval_pure_numeric


def test_pure_numeric_subtraction():
    # Python/SymPy ประเมิน 9.8-9.11 เป็น 0.69 (ไม่ใช่ 9.8 ลบ 9.11 แบบทศนิยมสองตัว)
    assert _eval_pure_numeric("9.8-9.11") == pytest.approx(0.69, abs=1e-9)


def test_compute_math_linear_system():
    out = compute_math_handler("compute_math", "x-y=5, xy=24", [])
    assert out["status"] == "success"
    assert isinstance(out["result"], list)
    assert len(out["result"]) >= 1


def test_compute_math_exponential_equation():
    """3^x=x^9 — หาคำตอบได้ (sympy อาจให้เฉพาะ integer solution ขึ้นกับ version)."""
    out = compute_math_handler("compute_math", "3^x=x^9", [])
    assert out["status"] == "success"
    assert out["result"]


def test_linear_system_shows_decimals():
    out = compute_math_handler("compute_math", "x+y=12, 5y=1", [])
    sol = out["result"][0]
    assert sol["y"] == pytest.approx(0.2, abs=1e-6)
    assert sol["x"] == pytest.approx(11.8, abs=1e-6)


def test_arithmetic_decimal_subtraction_via_handler():
    out = compute_math_handler("compute_math", "9.8-9.11", [])
    assert out["status"] == "success"
    assert out["result"] == pytest.approx(0.69, abs=1e-9)
    assert out.get("engine") == "numeric_eval"
