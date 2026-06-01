# tools/math.py

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
import z3
import re
from typing import Dict, Any, List, Callable, Optional, Union

SYM_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def get_tools() -> Dict[str, Callable]:
    return {
        "compute_math": compute_math_handler,
        "math": compute_math_handler,
    }


def compute_math_handler(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    if not inp:
        return {"status": "fail", "message": "ไม่มีข้อความสมการนำเข้า"}

    clean_inp = inp.strip().replace("^", "**")
    clean_inp = re.sub(r"(\S+=[^\s,]+)\s+([a-zA-Z0-9])", r"\1, \2", clean_inp)

    if _is_z3_constraint_problem(clean_inp):
        return _solve_with_z3(clean_inp)
    else:
        return _solve_with_sympy(clean_inp)


def _is_z3_constraint_problem(text: str) -> bool:
    """
    ตรวจจับอสมการหรือฟังก์ชันตรรกศาสตร์สากลเพื่อเรียกใช้ค่าย Z3
    """
    has_inequality = bool(re.search(r"[<>!]", text))
    has_logical_keywords = any(kw in text for kw in ["And", "Or", "Not", "Implies", "If", "&&", "||"])
    
    variables = set(re.findall(r"\b[a-zA-Z]\b", text))
    math_funcs = {"sin", "cos", "tan", "log", "exp", "abs", "diff", "integrate"}
    unique_vars = variables - math_funcs

    return (has_inequality or has_logical_keywords) and len(unique_vars) > 1


def _var_name_from_sympy_key(key: Any) -> str:
    if isinstance(key, str):
        return key
    name = getattr(key, "name", None)
    return str(name) if name else str(key)


def _sympy_to_display_number(val: Any) -> Union[int, float, str]:
    """
    แปลงค่า SymPy เป็นตัวเลขทศนิยม/จำนวนเต็มที่อ่านง่าย 
    และคัดกรองค่าประมาณ (เช่น LambertW หรือจำนวนอตรรกยะ) เป็นข้อความที่มีสัญลักษณ์ ≈ นำหน้าโดยตรง
    """
    if val is None:
        return "ไม่มีค่า"
    try:
        # ตรวจจับฟังก์ชัน LambertW และบังคับส่งคืนเป็นสตริงค่าประมาณ "≈ {value}" ทันที
        if "LambertW" in str(val):
            f = float(sp.N(val))
            approx_val = round(f, 6)
            return f"≈ {approx_val:,.6f}".rstrip("0").rstrip(".")

        if getattr(val, "is_Rational", False) and val.is_Rational:
            f = float(val)
            if abs(f - round(f)) < 1e-9:
                return int(round(f))
            
            # ตรวจสอบว่าเป็นทศนิยมไม่รู้จบในฐานสิบ (เช่น 1/3) หรือไม่ หากใช่ให้แปลงเป็นค่าประมาณ
            from fractions import Fraction
            frac = Fraction(f).limit_denominator(1000)
            denom = frac.denominator
            while denom % 2 == 0: denom //= 2
            while denom % 5 == 0: denom //= 5
            if denom != 1:
                return f"≈ {round(f, 6):,.6f}".rstrip("0").rstrip(".")
            return round(f, 6)

        if getattr(val, "is_number", False) and val.is_number:
            approx = complex(val.evalf(15))
            if abs(approx.imag) > 1e-8:
                return str(val)
            f = approx.real
            if abs(f - round(f)) < 1e-9 and abs(f) < 1e12:
                return int(round(f))
            
            # ตรวจหาค่ารากพหุนามและจำนวนอตรรกยะ (เช่น pi, sqrt(2)) ที่ไม่ใช่ค่าตรรกยะปกติ
            if not getattr(val, "is_rational", False):
                return f"≈ {round(f, 6):,.6f}".rstrip("0").rstrip(".")
            return round(f, 6)
            
    except (TypeError, ValueError, AttributeError):
        pass
    return str(val)


def _humanize_solutions(solutions: List[Dict[Any, Any]]) -> List[Dict[str, Union[int, float, str]]]:
    """แปลงผล solve ของ SymPy เป็น dict ตัวเลขธรรมดาหรือสตริงค่าประมาณ."""
    rows: List[Dict[str, Union[int, float, str]]] = []
    for sol in solutions:
        row: Dict[str, Union[int, float, str]] = {}
        for key, val in sol.items():
            row[_var_name_from_sympy_key(key)] = _sympy_to_display_number(val)
        rows.append(row)

    def sort_key(row: Dict[str, Union[int, float, str]]) -> tuple:
        # ตรรกะแยกตัวเลขจากสตริงที่มีเครื่องหมาย "≈" เพื่อความแม่นยำในการจัดเรียงผลลัพธ์
        def extract_numeric(v):
            if isinstance(v, (int, float)):
                return float(v)
            if isinstance(v, str) and v.startswith("≈"):
                try:
                    return float(v.replace("≈", "").strip())
                except ValueError:
                    return 0
            return 0

        nums = [extract_numeric(v) for v in row.values()]
        primary = nums[0] if nums else 0
        is_int = any(isinstance(v, int) for v in row.values())
        return (0 if is_int else 1, primary)

    return sorted(rows, key=sort_key)


def format_solution_pair(name: str, val: Union[int, float, str]) -> str:
    """จัดรูปแบบ x = 27 (ค่าเท่ากัน) หรือ x ≈ 1.150825 (ค่าประมาณ)."""
    if isinstance(val, int):
        return f"{name} = {val}"
    if isinstance(val, str) and val.strip().startswith("≈"):
        # รักษารูปแบบสัญลักษณ์ ≈ ที่ถูกจัดแต่งมาจากเครื่องมือคอร์หลัก
        return f"{name} {val.strip()}"
    if isinstance(val, float):
        text = f"{val:,.6f}".rstrip("0").rstrip(".")
        return f"{name} ≈ {text}"
    return f"{name} = {val}"


def format_solutions_readable(solutions: List[Dict[str, Union[int, float, str]]]) -> str:
    """ข้อความสรุปผลสมการสำหรับแสดงผู้ใช้."""
    if not solutions:
        return "ไม่พบคำตอบจากสมการ"
    parts = []
    for sol in solutions:
        pairs = ", ".join(format_solution_pair(k, v) for k, v in sol.items())
        parts.append(f"({pairs})")
    return " หรือ ".join(parts)


def _is_pure_numeric(expr_str: str) -> bool:
    """นิพจน์ตัวเลขล้วน (ไม่มีตัวแปร) — SymPy parse บางรูปแบบเช่น 9.8-9.11 ผิดพลาด."""
    compact = expr_str.replace(" ", "").replace("**", "")
    return bool(compact) and bool(re.fullmatch(r"[\d.+\-*/^%()]+", compact))


def _eval_pure_numeric(expr_str: str) -> Any:
    """คำนวณเลขด้วย Python eval (สอดคล้องกับ SymPy สำหรับนิพจน์ตัวเลขล้วน)."""
    clean = expr_str.strip().replace("^", "**")
    if not _is_pure_numeric(clean):
        return None
    try:
        value = eval(clean, {"__builtins__": None}, {})
        if isinstance(value, (int, float)):
            rounded = round(float(value), 10)
            return int(rounded) if rounded == int(rounded) else rounded
    except (SyntaxError, TypeError, ZeroDivisionError):
        return None
    return None


def _solve_with_sympy(expr_str: str) -> Dict[str, Any]:
    """
    วิเคราะห์คำนวณและหาเซ็ตคำตอบพีชคณิตทั้งหมดด้วย SymPy
    """
    try:
        if "diff" in expr_str or "integrate" in expr_str:
            parsed_expr = parse_expr(expr_str, transformations=SYM_TRANSFORMATIONS)
            return {
                "status": "success",
                "result": str(parsed_expr),
                "expression": expr_str,
                "engine": "sympy_calculus"
            }

        if "=" in expr_str:
            delimiters = r",|\n"
            eq_strings = [e.strip() for e in re.split(delimiters, expr_str) if e.strip()]
            
            parsed_eqs = []
            for eq in eq_strings:
                if "=" in eq:
                    parts = eq.split("=", 1)
                    lhs = parse_expr(parts[0], transformations=SYM_TRANSFORMATIONS)
                    rhs = parse_expr(parts[1], transformations=SYM_TRANSFORMATIONS)
                    parsed_eqs.append(lhs - rhs)
                else:
                    parsed_eqs.append(parse_expr(eq, transformations=SYM_TRANSFORMATIONS))
            
            variables = set()
            for parsed_eq in parsed_eqs:
                variables.update(parsed_eq.free_symbols)
                
            solutions = sp.solve(parsed_eqs, list(variables), dict=True)
            return {
                "status": "success",
                "result": _humanize_solutions(solutions) if solutions else solutions,
                "expression": expr_str,
                "engine": "sympy_solver"
            }

        numeric_result = _eval_pure_numeric(expr_str)
        if numeric_result is not None:
            return {
                "status": "success",
                "result": numeric_result,
                "expression": expr_str,
                "engine": "numeric_eval",
            }

        parsed_expr = parse_expr(expr_str, transformations=SYM_TRANSFORMATIONS)
        result = parsed_expr.evalf() if parsed_expr.is_number else sp.simplify(parsed_expr)
        
        if isinstance(result, sp.Float):
            result_val = float(result)
            result_val = round(result_val, 6) if abs(result_val) < 1e10 else result_val
        else:
            result_val = str(result)

        return {
            "status": "success",
            "result": result_val,
            "expression": expr_str,
            "engine": "sympy_evaluate"
        }

    except Exception as e:
        return {"status": "fail", "message": f"SymPy Error: {type(e).__name__} - {str(e)}"}


def _solve_with_z3(constraints_str: str) -> Dict[str, Any]:
    """
    วิเคราะห์แก้ไขอสมการจำกัดขอบเขตด้วย Z3-Solver
    """
    solver = z3.Solver()
    z3_vars = {}
    
    try:
        all_variables = set(re.findall(r"\b[a-zA-Z]\b", constraints_str))
        reserved_words = {"And", "Or", "Not", "Implies", "If", "sin", "cos", "tan", "log", "exp", "abs", "True", "False"}
        variables = all_variables - reserved_words
        
        for var in variables:
            z3_vars[var] = z3.Real(var)
            
        eval_env = {
            **z3_vars,
            "And": z3.And,
            "Or": z3.Or,
            "Not": z3.Not,
            "Implies": z3.Implies,
            "If": z3.If,
            "Eq": lambda a, b: a == b,
            "Ne": lambda a, b: a != b,
            "Lt": lambda a, b: a < b,
            "Le": lambda a, b: a <= b,
            "Gt": lambda a, b: a > b,
            "Ge": lambda a, b: a >= b,
            "StrictLessThan": lambda a, b: a < b,
            "LessThan": lambda a, b: a <= b,
            "StrictGreaterThan": lambda a, b: a > b,
            "GreaterThan": lambda a, b: a >= b,
        }
        
        delimiters = r",|\n"
        constraints_list = [c.strip() for c in re.split(delimiters, constraints_str) if c.strip()]
        
        for constraint in constraints_list:
            if re.search(r"[\u0e00-\u0e7f]", constraint):
                continue
                
            constraint_obj = _parse_and_build_z3_constraint(constraint, eval_env)
            if constraint_obj is not None:
                solver.add(constraint_obj)
            
        if len(solver.assertions()) == 0:
            return {"status": "fail", "message": "ไม่พบเงื่อนไขทางคณิตศาสตร์ที่สมบูรณ์ในการประมวลผล"}
            
        check_result = solver.check()
        
        if check_result == z3.sat:
            model = solver.model()
            solution = {}
            for name, var_obj in z3_vars.items():
                val = model[var_obj]
                if val is not None:
                    if z3.is_int_value(val):
                        solution[name] = val.as_long()
                    elif z3.is_rational_value(val):
                        solution[name] = float(val.as_fraction())
                    elif z3.is_algebraic_value(val):
                        approx_val = val.approx(10)
                        solution[name] = float(approx_val.as_fraction())
                    else:
                        solution[name] = str(val)
                else:
                    solution[name] = None
            return {
                "status": "success",
                "result": solution,
                "engine": "z3_solver"
            }
        elif check_result == z3.unsat:
            return {"status": "fail", "message": "เงื่อนไขขัดแย้งกัน ไม่มีคำตอบที่สอดคล้อง"}
        else:
            return {"status": "fail", "message": "ไม่สามารถหาคำตอบได้จากสมการที่ระบุ"}
            
    except Exception as e:
        return {"status": "fail", "message": f"Z3 Error: {type(e).__name__} - {str(e)}"}


def _parse_and_build_z3_constraint(constraint: str, eval_env: Dict[str, Any]) -> Any:
    operators = [("==", "=="), ("!=", "!="), ("<=", "<="), (">=", ">="), ("=", "=="), ("<", "<"), (">", ">")]
    
    op_found = None
    for op, z3_op in operators:
        if op in constraint:
            if op == "=" and "==" in constraint:
                continue
            op_found = (op, z3_op)
            break
            
    if op_found:
        op, z3_op = op_found
        parts = constraint.split(op, 1)
        lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
        
        lhs_parsed = parse_expr(lhs_str, transformations=SYM_TRANSFORMATIONS)
        rhs_parsed = parse_expr(rhs_str, transformations=SYM_TRANSFORMATIONS)
        
        lhs_val = eval(str(lhs_parsed), {"__builtins__": {}}, eval_env)
        rhs_val = eval(str(rhs_parsed), {"__builtins__": {}}, eval_env)
        
        if z3_op == "==": return lhs_val == rhs_val
        elif z3_op == "!=": return lhs_val != rhs_val
        elif z3_op == "<": return lhs_val < rhs_val
        elif z3_op == ">": return lhs_val > rhs_val
        elif z3_op == "<=": return lhs_val <= rhs_val
        elif z3_op == ">=": return lhs_val >= rhs_val
    else:
        parsed = parse_expr(constraint, transformations=SYM_TRANSFORMATIONS)
        val = eval(str(parsed), {"__builtins__": {}}, eval_env)
        
        if z3.is_bool(val) or isinstance(val, bool):
            return val
        else:
            return val == 0