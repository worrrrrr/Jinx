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

# ตั้งค่าการถอดรหัสรูปแบบสมการย่อ
SYM_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def get_tools() -> Dict[str, Callable]:
    return {
        "compute_math": compute_math_handler,
        "math": compute_math_handler,
    }


# แก้ไขในไฟล์ tools/math.py

def compute_math_handler(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    if not inp:
        return {"status": "fail", "message": "ไม่มีข้อความสมการนำเข้า"}

    # ✅ ป้องกันภาษาไทยปนเปื้อนในอินพุตของเครื่องมือคำนวณเชิงสัญลักษณ์โดยเด็ดขาด 
    # หากพบอักขระภาษาไทย ให้แจ้งเตือนเพื่อให้ผู้ใช้ป้อนเฉพาะสมการคณิตศาสตร์ดิบ เช่น "x-y=5, x*y=24"
    if re.search(r"[\u0e00-\u0e7f]", inp):
        return {
            "status": "fail", 
            "message": "ไม่สนับสนุนโจทย์อธิบายภาษาไทยในโหมดคำนวณสัญลักษณ์โดยตรง กรุณาเขียนเป็นสมการ เช่น 'x - y = 5, x*y = 24'"
        }

    # ปรับแต่งคำสั่งยกกำลัง ^ เป็น ** ล่วงหน้า
    clean_inp = inp.strip().replace("^", "**")

    # ปรับแก้กรณีระบบสมการเว้นวรรคไม่มีเครื่องหมายจุลภาคคั่น
    clean_inp = re.sub(r"(\S+=[^\s,]+)\s+([a-zA-Z0-9])", r"\1, \2", clean_inp)

    if _is_z3_constraint_problem(clean_inp):
        return _solve_with_z3(clean_inp)
    else:
        return _solve_with_sympy(clean_inp)


def _is_z3_constraint_problem(text: str) -> bool:
    has_inequality = bool(re.search(r"[<>!]", text))
    has_logical_keywords = any(kw in text for kw in ["And", "Or", "Not", "Implies", "&&", "||", ","])
    
    variables = set(re.findall(r"\b[a-zA-Z]\b", text))
    math_funcs = {"sin", "cos", "tan", "log", "exp", "abs", "diff", "integrate"}
    unique_vars = variables - math_funcs

    return (has_inequality or has_logical_keywords) and len(unique_vars) > 1


def _solve_with_sympy(expr_str: str) -> Dict[str, Any]:
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
            parts = expr_str.split("=")
            if len(parts) == 2:
                lhs = parse_expr(parts[0], transformations=SYM_TRANSFORMATIONS)
                rhs = parse_expr(parts[1], transformations=SYM_TRANSFORMATIONS)
                equation = lhs - rhs
                
                variables = list(equation.free_symbols)
                if not variables:
                    return {"status": "fail", "message": "ไม่พบตัวแปรในการแก้สมการ"}
                
                solutions = sp.solve(equation, variables, dict=True)
                return {
                    "status": "success",
                    "result": str(solutions),
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
    solver = z3.Solver()
    z3_vars = {}
    
    try:
        # สแกนและประกาศตัวแปรในโจทย์
        all_words = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", constraints_str))
        reserved_words = {"And", "Or", "Not", "Implies", "If", "sin", "cos", "tan", "log", "exp", "abs", "True", "False"}
        variables = all_words - reserved_words
        
        for var in variables:
            z3_vars[var] = z3.Real(var)
            
        eval_env = {
            **z3_vars,
            "And": z3.And,
            "Or": z3.Or,
            "Not": z3.Not,
            "Implies": z3.Implies,
            "If": z3.If
        }
        
        delimiters = r",|\n"
        constraints_list = [c.strip() for c in re.split(delimiters, constraints_str) if c.strip()]
        
        for constraint in constraints_list:
            # ข้ามกรณีประโยคที่มีภาษาไทยปนเปื้อนในเงื่อนไขย่อยโดยเด็ดขาด
            if re.search(r"[\u0e00-\u0e7f]", constraint):
                continue
                
            # แปลงข้อจำกัดแต่ละชุดด้วยฟังก์ชันประมวลผลแยกฝั่ง LHS/RHS ป้องกันบักการประเมินผลล่วงหน้าของ SymPy
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
                    # ตรวจจับประเภทตัวเลขของ Z3 แบบครอบคลุม
                    if z3.is_int_value(val):
                        solution[name] = val.as_long()
                    elif z3.is_rational_value(val):
                        # ใช้ as_fraction() เพื่อป้องกันการสูญเสียความละเอียดของเลขทศนิยมเศษส่วน
                        solution[name] = float(val.as_fraction())
                    elif z3.is_algebraic_value(val):
                        # กรณีเลขอตรรกยะ (เช่น รากที่สอง) ให้ประมาณการเป็นทศนิยม 10 ตำแหน่ง
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
    """
    วิเคราะห์และแยกโครงสร้างฝั่งซ้าย (LHS) และฝั่งขวา (RHS) เพื่อแปลงเครื่องหมายเชิงสัมพันธ์ส่งต่อให้ Z3 
    โดยหลีกเลี่ยงการใช้ '==' ของ Python ตรงๆ ในระหว่างการเรียกใช้งาน parse_expr
    """
    # เรียงลำดับตัวดำเนินการจากยาวไปสั้นเพื่อความแม่นยำในการตรวจจับสัญลักษณ์ย่อย
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
        
        # แปลงโครงสร้างแยกจากกันอิสระ ป้องกันปัญหา SymPy คืนค่า False ทันทีจากการเปรียบเทียบผิดที่
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
        # กรณีไม่มีเครื่องหมายเชิงสัมพันธ์ (เช่น การระบุพหุนามเปล่า หรือตัวแปรเดี่ยว)
        parsed = parse_expr(constraint, transformations=SYM_TRANSFORMATIONS)
        val = eval(str(parsed), {"__builtins__": {}}, eval_env)
        
        if z3.is_bool(val) or isinstance(val, bool):
            return val
        else:
            # ตั้งสมมติฐานว่าพหุนามที่เขียนเปล่า มีค่าเทียบเท่ากับการสมมติให้สมการเท่ากับ 0
            return val == 0