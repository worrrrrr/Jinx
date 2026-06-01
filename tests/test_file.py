"""Workspace file tools (Phase 1)."""

import os
import tempfile
import shutil

import pytest

from tools import file as wf
from core.orchestrator import Orchestrator


@pytest.fixture
def sandbox_file():
    rel = "tmp_test_jinx_phase1/hello.py"
    abs_path = os.path.join(wf.PROJECT_ROOT, rel)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    yield rel, abs_path
    if os.path.exists(abs_path):
        os.remove(abs_path)
    parent = os.path.dirname(abs_path)
    if os.path.isdir(parent) and not os.listdir(parent):
        os.rmdir(parent)


def test_resolve_blocks_traversal():
    _, err = wf.resolve_workspace_path("../../etc/passwd")
    assert err


def test_resolve_blocks_vault():
    _, err = wf.resolve_workspace_path("data/knowledge/secret.md")
    assert err and "vault" in err.lower()


def test_workspace_write_and_read(sandbox_file):
    rel, abs_path = sandbox_file
    code = "def greet():\n    return 'hi'\n"
    out = wf.workspace_write("write_code", f"สร้าง {rel}\n```python\n{code}```", [rel])
    assert out["status"] == "success"
    assert os.path.isfile(abs_path)
    with open(abs_path, encoding="utf-8") as f:
        assert "def greet" in f.read()

    read = wf.workspace_read("read_code", rel, [rel])
    assert read["status"] == "success"
    assert "greet" in read["result"]


def test_apply_patch(sandbox_file):
    rel, abs_path = sandbox_file
    wf.workspace_write("write_code", f"{rel}\n```python\nx = 1\n```", [rel])
    wf.workspace_apply_patch("apply_patch", f"{rel} x = 1|||x = 2", [rel])
    with open(abs_path, encoding="utf-8") as f:
        assert f.read().strip() == "x = 2"


def test_orchestrator_create_python_file(sandbox_file):
    rel, abs_path = sandbox_file
    o = Orchestrator()
    reply = o.run(
        f'สร้างไฟล์ {rel} ```python\nprint("jinx")\n```'
    )
    assert "สร้าง" in reply or "อัปเดต" in reply or rel.replace("\\", "/") in reply
    assert os.path.isfile(abs_path)
    with open(abs_path, encoding="utf-8") as f:
        assert "print" in f.read()
