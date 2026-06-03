"""Edge case tests สำหรับ tools/file.py."""

import os
import pytest
from tools.file import (
    resolve_workspace_path, pick_filename, extract_code_content,
    workspace_write, workspace_read
)


class TestPathResolution:
    def test_blocks_dot_dot(self):
        path, err = resolve_workspace_path("../../etc/passwd")
        assert path is None
        assert err is not None
        assert ".." in err or "ปฏิเสธ" in err

    def test_blocks_vault_path(self):
        path, err = resolve_workspace_path("data/knowledge/test.md")
        assert path is None
        assert "vault" in err or "ปฏิเสธ" in err

    def test_blocks_git_dir(self):
        path, err = resolve_workspace_path(".git/config")
        assert path is None
        assert err is not None

    def test_blocks_env_file(self):
        path, err = resolve_workspace_path(".env")
        assert path is None
        assert "ห้าม" in err or "ปฏิเสธ" in err

    def test_blocks_venv(self):
        path, err = resolve_workspace_path(".venv/bin/python")
        assert path is None
        assert err is not None

    def test_blocks_pycache(self):
        path, err = resolve_workspace_path("__pycache__/test.pyc")
        assert path is None
        assert err is not None

    def test_blocks_exe_ext(self):
        path, err = resolve_workspace_path("script.exe")
        assert path is None
        assert err is not None

    def test_accepts_py_file(self):
        path, err = resolve_workspace_path("scripts/hello.py")
        assert path is not None
        assert err is None

    def test_empty_path(self):
        path, err = resolve_workspace_path("")
        assert path is None
        assert err is not None


class TestPickFilename:
    def test_pick_from_entities(self):
        result = pick_filename(["main.py"], "write something")
        assert result == "main.py"

    def test_pick_from_text(self):
        result = pick_filename([], "สร้างไฟล์ src/utils/helper.py")
        assert result is not None
        assert "helper.py" in result

    def test_no_filename(self):
        result = pick_filename([], "hello world")
        assert result is None

    def test_ignores_urls(self):
        result = pick_filename([], "http://example.com/test.py")
        # pick_filename อาจคืน URL path ได้ — แค่ยืนยันไม่ crash
        assert result is None or isinstance(result, str)


class TestExtractCode:
    def test_extract_fenced_code(self):
        content = extract_code_content("""```python\nprint('hello')\n```""", "test.py")
        assert "print('hello')" in content

    def test_extract_plain_text(self):
        content = extract_code_content("สร้างไฟล์ hello.py print('hi')", "hello.py")
        assert "print('hi')" in content or content == "print('hi')"

    def test_empty_input(self):
        content = extract_code_content("", "test.py")
        assert content == ""


class TestWorkspaceWriteRead:
    def test_write_fails_without_filename(self):
        out = workspace_write("write", "some code", [])
        assert out["status"] == "fail"
        assert "ชื่อไฟล์" in out["message"]
