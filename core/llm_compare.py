import os
import time
import json
import sympy
import ollama
from abc import ABC, abstractmethod
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# โหลด API Keys จากไฟล์ .env
load_dotenv()

# ==========================================
# 1. LLM PROVIDERS (แยกค่าย ชัดเจน ไม่พันกัน)
# ==========================================

class LLMProvider(ABC):
    """พิมพ์เขียวสำหรับทุก LLM ที่จะเอามาเสียบใน Jinx"""
    @abstractmethod
    def ask(self, messages, tools):
        pass

class OllamaProvider(LLMProvider):
    def __init__(self, model="qwen3:0.6b"):
        self.model = model
    
    def ask(self, messages, tools):
        # รันผ่านระบบ Ollama (Private Cloud/Local)
        response = ollama.chat(
            model=self.model, 
            messages=messages, 
            tools=tools
        )
        return response['message']

class GroqProvider(LLMProvider):
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model
    
    def ask(self, messages, tools):
        # รันผ่าน Groq LPU (High Speed Cloud)
        response = self.client.chat.completions.create(
            model=self.model, 
            messages=messages, 
            tools=tools
        )
        msg = response.choices[0].message
        
        # แปลงโครงสร้าง Groq ให้เป็นมาตรฐานกลางของ Jinx
        return {
            'content': msg.content,
            'tool_calls': [
                {
                    'function': {
                        'name': tc.function.name, 
                        'arguments': json.loads(tc.function.arguments)
                    }
                } for tc in msg.tool_calls
            ] if msg.tool_calls else None
        }

# ==========================================
# 2. JINX BRAIN (ตัวคุมระบบกลาง และ Tools)
# ==========================================

class JinxBrain:
    def __init__(self, provider: LLMProvider):
        self.llm = provider  # รับ Provider ตัวที่เลือกมาใช้งาน
        self.tools = self._get_tool_definitions()

    def _get_tool_definitions(self):
        """นิยามเครื่องมือให้ LLM ทุกตัวใช้มาตรฐานเดียวกัน"""
        return [{
            'type': 'function',
            'function': {
                'name': 'solve_math_symbolic',
                'description': 'แก้สมการคณิตศาสตร์ รองรับ x**2 - 4 หรือ x-y=5, x*y=24',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'expression': {'type': 'string', 'description': 'ตัวแปรและสมการ'}
                    },
                    'required': ['expression']
                }
            }
        }]

    def execute_math_tool(self, args):
        """Logic การคำนวณที่ถึกที่สุด ดักจับทุก Error"""
        print(f"DEBUG 🔍 | Raw Tool Args: {args}")
        try:
            # 1. ดึง String สมการออกมา (รองรับทั้ง Dict และ String ขยะ)
            expr_str = ""
            if isinstance(args, dict):
                expr_str = args.get('expression') or args.get('expr') or list(args.values())[0]
            else:
                expr_str = str(args)

            # 2. คลีนขยะที่ LLM บางตัวชอบแถมมา
            expr_str = expr_str.split('</')[0].replace('`', '').strip()
            
            # 3. จัดการรูปแบบสมการหลายตัวแปร
            expr_str = expr_str.replace(" and ", ",").replace(";", ",")
            parts = [p.replace("=0", "").strip() for p in expr_str.split(",")]
            
            x, y, z = sympy.symbols('x y z')
            local_dict = {'x': x, 'y': y, 'z': z}
            
            final_exprs = []
            for p in parts:
                if "=" in p and "==" not in p:
                    sides = p.split("=")
                    final_exprs.append(f"({sides[0]}) - ({sides[1]})")
                else:
                    final_exprs.append(p)

            # 4. การแก้สมการ (Symbolic ก่อน แล้วค่อย Numerical)
            sym_objects = [sympy.sympify(ex, locals=local_dict) for ex in final_exprs]
            
            # ลอง solve ปกติ (จะได้คำตอบครบ เช่น 27)
            result = sympy.solve(sym_objects, [x, y, z], dict=True)
            
            # ถ้า solve ไม่ได้ (เช่น 3^x = x^9) ให้ใช้ nsolve
            if not result and len(sym_objects) == 1:
                val = sympy.nsolve(sym_objects[0], x, 1)
                return str([{x: float(val.evalf())}])

            return str(result)

        except Exception as e:
            return f"Tool Error: {str(e)}"

    def run(self, prompt):
        """หัวใจหลักของการประมวลผล"""
        provider_name = self.llm.__class__.__name__
        print(f"\n{'='*60}\n🤖 {provider_name} | ❓ {prompt}\n{'='*60}")

        # System Prompt แยกตามโหมด
        # แก้ไขใน JinxBrain.run
        messages = [
            {
                "role": "system", 
                "content": (
                    "You are Jinx AGI. Solve math by calling 'solve_math_symbolic'.\n"
                    "STRICT RULES:\n"
                    "1. Put ALL equations inside the 'expression' argument, separated by commas.\n"
                    "2. DO NOT create new arguments like 'condition' or 'equation2'.\n"
                    "3. Example: solve_math_symbolic(expression='x-y=5, x*y=24')"
                )
            },
            {"role": "user", "content": prompt}
        ]

        start_time = time.time()
        try:
            # เรียก LLM ผ่าน Provider ที่เลือก
            res = self.llm.ask(messages, self.tools)
            duration = time.time() - start_time
            final_output = ""

            if res.get('tool_calls'):
                # ถ้า LLM สั่งใช้ Tool
                tc = res['tool_calls'][0]
                fn_name = tc['function']['name']
                fn_args = tc['function']['arguments']
                
                print(f"🛠️  Calling: {fn_name}")
                tool_res = self.execute_math_tool(fn_args)
                print(f"💡 Result: {tool_res}")
                final_output = f"Tool Answer: {tool_res}"
            else:
                # ถ้า LLM ตอบเป็นข้อความธรรมดา
                final_output = res.get('content', '')
                print(f"📝 Answer: {final_output}")

            print(f"⏱️  Done in {duration:.2f}s")
            self._log_result(provider_name, prompt, final_output, duration)

        except Exception as e:
            print(f"❌ Error during execution: {e}")

    def _log_result(self, mode, query, answer, duration):
        """บันทึกสถิติลงไฟล์ Markdown"""
        filename = "benchmark_results.md"
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write("# 🧪 Jinx LLM Benchmark\n\n| Time | Provider | Query | Duration | Result |\n|---|---|---|---|---|\n")
        
        with open(filename, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%H:%M:%S")
            clean_ans = str(answer).replace("\n", " ")[:100]
            f.write(f"| {timestamp} | {mode} | {query} | {duration:.2f}s | {clean_ans} |\n")

# ==========================================
# 3. EXECUTION: เปรียบเทียบประสิทธิภาพ
# ==========================================

if __name__ == "__main__":
    test_queries = [
        "3^x=x^9",
        "x มากกว่า y อยู่ 5 และ x*y=24 หา x และ y"
    ]
    
    # คุณสามารถเพิ่ม Provider ใหม่ๆ (เช่น GeminiProvider) ลงในลิสต์นี้ได้เลย
    active_providers = [
        OllamaProvider(), 
       # GroqProvider()
    ]
    
    for provider in active_providers:
        jinx = JinxBrain(provider)
        for q in test_queries:
            jinx.run(q)

    print(f"\n✅ All tests completed. Check 'benchmark_results.md' for details.")