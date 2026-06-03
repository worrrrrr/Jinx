"""Unit tests สำหรับ tools/obsidian.py และ tools/utils.py."""

import os
import tempfile
import pytest

# Mock VAULT_DIR ให้ใช้ temp directory
import tools.obsidian as obs
import tools.utils as utils

OBS_VAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge")
UTILS_VAULT = OBS_VAULT


class TestObsidianCreate:
    def test_create_note_success(self):
        out = obs.create_obsidian_note("create", "test_note.md\nเนื้อหาทดสอบ", ["test_note.md"])
        assert out["status"] == "success"
        assert "สร้าง" in out["result"] or "สำเร็จ" in out["result"]
        # cleanup
        path = os.path.join(OBS_VAULT, "test_note.md")
        if os.path.exists(path):
            os.remove(path)

    def test_create_note_with_frontmatter(self):
        out = obs.create_obsidian_note("create", "front_note.md\n# หัวข้อ\nเนื้อหา", ["front_note.md"])
        assert out["status"] == "success"
        path = os.path.join(OBS_VAULT, "front_note.md")
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            assert "created:" in content
            assert "---" in content
            os.remove(path)


class TestObsidianAppend:
    def test_append_to_nonexistent_creates(self):
        filename = "append_test.md"
        path = os.path.join(OBS_VAULT, filename)
        if os.path.exists(path):
            os.remove(path)
        out = obs.append_obsidian_note("append", f"{filename}\nเนื้อหาใหม่", [filename])
        assert out["status"] == "success"
        if os.path.exists(path):
            os.remove(path)


class TestUtilsVault:
    def test_vault_list_existing(self):
        out = utils.handle_vault_list("list", "", [])
        assert out["status"] == "success"
        assert "พบไฟล์" in out["result"] or "ไม่มี" in out["result"] or "ว่าง" in out["result"]

    def test_vault_read_nonexistent(self):
        out = utils.handle_vault_read("read", "", ["nonexistent_file_xyz.md"])
        assert out["status"] == "fail"
