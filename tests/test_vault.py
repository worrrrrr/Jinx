"""Unit tests สำหรับ Obsidian Enhanced vault tools"""

import os
from tools.obsidian import vault_read_handler, vault_search_handler, _get_safe_path, VAULT_DIR


class TestVaultRead:
    def test_read_nonexistent(self):
        out = vault_read_handler("read", "", ["nonexistent_test_xyz.md"])
        assert out["status"] == "fail"

    def test_read_existing(self):
        # สร้างไฟล์ชั่วคราว
        path = os.path.join(VAULT_DIR, "_test_vault_read.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# ทดสอบ\nเนื้อหา")
        out = vault_read_handler("read", "", ["_test_vault_read.md"])
        assert out["status"] == "success"
        assert "ทดสอบ" in out["result"]
        os.remove(path)

    def test_read_blocked_path(self):
        out = vault_read_handler("read", "", ["../.env"])
        assert out["status"] == "fail"


class TestVaultSearch:
    def test_search_no_query(self):
        out = vault_search_handler("search", "", [])
        assert out["status"] == "fail"

    def test_search_finds_content(self):
        # สร้างไฟล์ชั่วคราว
        path = os.path.join(VAULT_DIR, "_test_search_temp.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# หัวข้อ\nเนื้อหาทดสอบคำค้นหา")
        out = vault_search_handler("search", "คำค้นหา", [])
        assert out["status"] == "success"
        assert "คำค้นหา" in out["result"]
        os.remove(path)

    def test_search_no_match(self):
        out = vault_search_handler("search", "zzz_nonexistent_xyz_987", [])
        assert out["status"] == "success"
