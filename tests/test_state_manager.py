"""Unit tests สำหรับ tools/state_manager.py"""

from tools.state_manager import (
    state_machine_handler,
    _load_machine,
    _transition,
    _format_diagram,
    _clear_state,
)


class TestStateManager:
    def setup_method(self):
        # รีเซ็ต state เริ่มต้น
        _clear_state("coffee")
        _clear_state("nonexistent_xyz")

    def test_load_existing_machine(self):
        m = _load_machine("coffee")
        assert m is not None
        assert m["name"] == "Coffee Machine"
        assert len(m["transitions"]) == 5

    def test_load_nonexistent_machine(self):
        m = _load_machine("nonexistent_xyz")
        assert m is None

    def test_show_current_state(self):
        out = state_machine_handler("state", "coffee", [])
        assert out["status"] == "success"
        assert "idle" in out.get("result", "") or "idle" in out.get("current", "")

    def test_no_machine_name_fails(self):
        out = state_machine_handler("state", "", [])
        assert out["status"] == "fail"

    def test_nonexistent_machine_fails(self):
        out = state_machine_handler("state", "nonexistent_xyz", [])
        assert out["status"] == "fail"

    def test_transition_insert_coin(self):
        out = state_machine_handler("state", "coffee insert_coin", [])
        assert out["status"] == "success"
        assert out["to"] == "has_coin"

    def test_transition_full_flow(self):
        out = state_machine_handler("state", "coffee insert_coin", [])
        assert out["to"] == "has_coin"

        out = state_machine_handler("state", "coffee select_drink", [])
        assert out["to"] == "brewing"

        out = state_machine_handler("state", "coffee done", [])
        assert out["to"] == "dispensing"

        out = state_machine_handler("state", "coffee take_cup", [])
        assert out["to"] == "idle"

    def test_wildcard_transition(self):
        out = state_machine_handler("state", "coffee insert_coin", [])
        assert out["to"] == "has_coin"

        out = state_machine_handler("state", "coffee cancel", [])
        assert out["to"] == "idle"

    def test_invalid_transition(self):
        out = state_machine_handler("state", "coffee invalid_event", [])
        assert out["status"] == "fail"

    def test_reset_machine(self):
        out = state_machine_handler("state", "coffee --reset", [])
        assert out["status"] == "success"

    def test_show_diagram(self):
        out = state_machine_handler("state", "coffee --show", [])
        assert out["status"] == "success"
        assert "-->" in out["result"]
        assert "idle" in out["result"]
        assert "insert_coin" in out["result"]

    def test_transition_function(self):
        machine = _load_machine("coffee")
        assert _transition(machine, "idle", "insert_coin") == "has_coin"
        assert _transition(machine, "has_coin", "select_drink") == "brewing"
        assert _transition(machine, "brewing", "invalid") is None

    def test_format_diagram(self):
        machine = _load_machine("coffee")
        diagram = _format_diagram(machine)
        assert "Coffee Machine" in diagram
        assert "idle --(insert_coin)--> has_coin" in diagram
