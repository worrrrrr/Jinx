# AGENTS.md — Jinx Personal AI Runtime

## คำสั่งสำคัญ

| การกระทำ | คำสั่ง |
|-----------|--------|
| รัน REPL | `uv run python main.py` |
| ทดสอบสถานการณ์จริง | `uv run python realworld.py` |
| ทดสอบ LLM provider | `uv run python learning.py` |
| Benchmark ข้าม provider | `uv run python -m core.llm_compare` |
| รัน test suite | `uv run pytest` |
| Self-Eval (E2E) | `uv run python scripts/self_eval.py` |
| ติดตั้ง dependencies | `uv sync` |
| เพิ่ม dependency | `uv add <pkg>` / `uv add --dev <pkg>` |

ไม่มี linter, formatter, typecheck, หรือ CI ใด ๆ ในโปรเจกต์นี้

## ภาษาไทยใน Source Code

comment, log, error message, docstring **ทั้งหมดเป็นภาษาไทย** หากแก้ไขโค้ดต้องรักษาภาษาไทยใน comment และ message ไว้

## สถาปัตยกรรม

Pipeline 4 ขั้น ขับเคลื่อนโดย `Orchestrator.run()` (`core/orchestrator.py`):

```
Perception → Reasoning → Execution → Response
```

- แต่ละขั้นเป็น class ใน `engines/` (`perception.py`, `reasoning.py`, `execution.py`, `response.py`)
- `Orchestrator.__init__()` เริ่มต้น 4 engines แล้วเรียกเรียงลำดับใน `run()`
- ข้อมูลส่งต่อเป็น dict ระหว่างขั้น (`perception_output` → `plan_output` → `execution_output` → response)

## ลงทะเบียนเครื่องมือ (Tools)

แต่ละโมดูลใน `tools/` ต้องมีฟังก์ชัน `get_tools()` คืน `Dict[str, Callable]`:

```python
def get_tools() -> Dict[str, Callable]:
    return {"action_key": my_handler}
```

`ExecutionEngine._register_external_tools()` เรียก `get_tools()` จากทุกโมดูลโดยอัตโนมัติ (`tools/math.py`, `search.py`, `file.py`, `obsidian.py`, `utils.py`) ถ้าต้องการเพิ่ม tool ใหม่: สร้างไฟล์ใน `tools/`, เขียน `get_tools()`, แล้วจับคู่ action key กับ `PerceptionEngine._infer_action()`

## ข้อจำกัดด้านความปลอดภัย

**`tools/file.py`** ห้าม:
- ใช้ `..` ใน path
- เขียนทับ `.git/`, `__pycache__/`, `.venv/`, `node_modules/`, `.pytest_cache/`
- แก้ไข `.env`
- เขียนลง `data/knowledge/` (ต้องใช้ `tools/obsidian.py` หรือ `tools/utils.py` แทน)

**`engines/execution.py`** บล็อก `os.system`, `subprocess`, `eval(`, `exec(`, `__import__`, `shutil.`, `open(`, `write(`, `remove(`

## Knowledge Vault (Ground Truth)

`data/knowledge/` เป็นแหล่งความจริงหลักของระบบ (ดู `docs/RULES.md` ข้อ 1) Search ใช้ `rapidfuzz` แบบ fuzzy matching + alias expansion จาก `common.md` ฟังก์ชันหลัก: `tools/search.py::search_local_knowledge()`

## ระบบคณิตศาสตร์

`tools/math.py` มี 2 เอนจิน:
- **SymPy** — สมการพีชคณิต, symbolic (`_solve_with_sympy`)
- **Z3** — ข้อจำกัด/อสมการ, SAT/SMT (`_solve_with_z3`)

Router ใน `compute_math_handler()`: ตรวจจับ `<>!` และมีตัวแปรหลายตัว → Z3, นอกนั้น → SymPy มี `PerceptionEngine._extract_math_formula()` ที่แปลงภาษาไทย→สมการ (NLP to Math Compiler)

## LLM Providers (ไม่บังคับ)

`core/llm_core.py` มี 3 providers: `OllamaProvider`, `GroqProvider`, `ClaudeProvider` ใช้ `ABC` base class ต้อง implement `chat()` API key จาก `.env` (`GROQ_API_KEY`, `ANTHROPIC_API_KEY`) LLM เป็นส่วนเสริม — ระบบออกแบบให้ทำงานได้โดยไม่มี LLM (`docs/RULES.md` ข้อ 3)

## Memory

`SessionMemory` (`core/memory.py`) เก็บ:
- ประวัติสนทนา (`deque`, default 10 turns)
- ตัวแปรคณิตศาสตร์ข้าม turn (เฉพาะตัวอักษรเดี่ยว a-z)

`extract_variables_from_result()` ดึงตัวแปรจากผลลัพธ์ math tool โดยอัตโนมัติ `substitute_variables_in_text()` แทนค่าตัวแปรในสมการรอบถัดไป




# ห้ามยุ่งกับไฟล์ที่ไม่ได้เกี่ยวกับที่สั่ง
