"""Unit tests สำหรับ ExecutionEngine."""

import pytest
from engines.execution import ExecutionEngine

@pytest.fixture
def engine():
    return ExecutionEngine()

class TestToolRouting:
    def test_math_routing(self, engine):
        out = engine.execute({
            "domain": "math", "action": "compute_math",
            "topic": "2+2", "entities": [],
            "tasks": ["compute_math"], "status": "ready",
            "metadata": {}, "response_hint": {},
        })
        assert out["status"] == "success"
        assert out["result"] == 4

    def test_noop_for_unknown(self, engine):
        out = engine.execute({
            "domain": "general", "action": "noop",
            "topic": "", "entities": [],
            "tasks": [], "status": "ready",
            "metadata": {}, "response_hint": {},
        })
        assert out["status"] == "noop"

class TestSecurity:
    def _dangerous_plan(self, topic, entities=None):
        """action ต้องมี tool จริง แต่ไม่ใช่ workspace tool เพื่อให้ security check ทำงาน."""
        return {
            "domain": "general", "action": "compute_math",
            "topic": topic, "entities": entities or [],
            "tasks": ["compute_math"], "status": "ready",
            "metadata": {}, "response_hint": {},
        }

    def test_blocks_os_system(self, engine):
        out = engine.execute(self._dangerous_plan("os.system('rm -rf /')"))
        assert out["status"] == "fail"
        assert "ไม่ปลอดภัย" in out["message"] or "อันตราย" in out["message"]

    def test_blocks_eval(self, engine):
        out = engine.execute(self._dangerous_plan("eval('__import__')"))
        assert out["status"] == "fail"

    def test_blocks_subprocess(self, engine):
        out = engine.execute(self._dangerous_plan("subprocess.run(['ls'])"))
        assert out["status"] == "fail"

    def test_blocks_shutil(self, engine):
        out = engine.execute(self._dangerous_plan("shutil.rmtree('/')"))
        assert out["status"] == "fail"

    def test_blocks_in_entities(self, engine):
        out = engine.execute(self._dangerous_plan("normal text", ["eval('danger')"]))
        assert out["status"] == "fail"

    def test_workspace_tool_skips_injection_check(self, engine):
        """File/workspace tools รับโค้ดจริงได้ ไม่ถูกบล็อก."""
        out = engine.execute({
            "domain": "code", "action": "write_code",
            "topic": "print('hello')", "entities": ["main.py"],
            "tasks": ["write_code"], "status": "ready",
            "metadata": {}, "response_hint": {},
        })
        assert out["status"] in ("success", "fail")
        if out["status"] == "fail":
            assert "ไม่ปลอดภัย" not in out["message"]

class TestFallbackHandlers:
    def test_fallback_math(self, engine):
        """เมื่อ import tools ล้มเหลว ใช้ fallback _math_handler."""
        engine.tools = {}
        engine._register_fallback_tools()
        out = engine.execute({
            "domain": "math", "action": "math",
            "topic": "2+2", "entities": [],
            "tasks": ["math"], "status": "ready",
            "metadata": {}, "response_hint": {},
        })
        assert out["status"] == "success"
        assert out["result"] == 4

    def test_fallback_search(self, engine):
        engine.tools = {}
        engine._register_fallback_tools()
        out = engine._search_handler("search", "test", [])
        assert out["status"] == "success"
        assert "ข้อมูลจำลอง" in out["result"][0]["title"]
