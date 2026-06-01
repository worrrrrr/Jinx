"""Readable solution formatting (≈ for approximations)."""

from tools.math import format_solution_pair, format_solutions_readable, _humanize_solutions
import sympy as sp


def test_format_pair_uses_equals_for_integer():
    assert format_solution_pair("x", 27) == "x = 27"


def test_format_pair_uses_approx_for_float():
    assert format_solution_pair("x", 1.150825) == "x ≈ 1.150825"


def test_lambertw_humanized_to_approx_display():
    x = sp.symbols("x")
    raw = sp.solve(3**x - x**9, x, dict=True)
    human = _humanize_solutions(raw)
    text = format_solutions_readable(human)
    assert "LambertW" not in text
    assert "≈" in text
    assert "27" in text
