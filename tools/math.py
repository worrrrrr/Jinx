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
from typing import Dict, Any, List, Callable

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
                "result": solutions,
                "expression": expr_str,
                "engine": "sympy_solver"
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