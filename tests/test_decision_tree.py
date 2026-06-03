"""Unit tests สำหรับ tools/decision_tree.py"""

import os
import json
from tools.decision_tree import (
    decision_tree_handler,
    _load_tree,
    _find_node,
    _match_choice,
    _clear_state,
    TREES_DIR,
)


class TestDecisionTree:
    def setup_method(self):
        # ล้าง state เผื่อค้าง
        _clear_state("food")

    def test_load_existing_tree(self):
        tree = _load_tree("food")
        assert tree is not None
        assert tree["name"] == "แนะนำอาหาร"
        assert len(tree["nodes"]) == 10

    def test_load_nonexistent_tree(self):
        tree = _load_tree("nonexistent_xyz")
        assert tree is None

    def test_start_tree(self):
        out = decision_tree_handler("tree", "food", [])
        assert out["status"] == "success"
        assert "ชอบอาหารประเภทไหน" in out["result"]

    def test_no_tree_name_fails(self):
        out = decision_tree_handler("tree", "", [])
        assert out["status"] == "fail"

    def test_nonexistent_tree_fails(self):
        out = decision_tree_handler("tree", "nonexistent_xyz", [])
        assert out["status"] == "fail"

    def test_navigate_thai_spicy(self):
        # step 1: เริ่ม
        out = decision_tree_handler("tree", "food ไทย", [])
        assert out["status"] == "success"

    def test_reset_tree(self):
        out = decision_tree_handler("tree", "food --reset", [])
        assert out["status"] == "success"
        assert "รีเซ็ต" in out["result"]

    def test_find_node(self):
        tree = _load_tree("food")
        node = _find_node(tree, "thai_spicy")
        assert node is not None
        assert "result" in node
        assert "ต้มยำกุ้ง" in node["result"]

    def test_match_choice_by_label(self):
        tree = _load_tree("food")
        start = _find_node(tree, "start")
        choice = _match_choice(start["choices"], "อาหารไทย")
        assert choice is not None
        assert choice["next"] == "thai_q"

    def test_match_choice_by_keyword(self):
        tree = _load_tree("food")
        start = _find_node(tree, "start")
        choice = _match_choice(start["choices"], "japanese")
        assert choice is not None
        assert choice["next"] == "japanese_q"

    def test_match_choice_no_match(self):
        tree = _load_tree("food")
        start = _find_node(tree, "start")
        choice = _match_choice(start["choices"], "korean")
        assert choice is None
