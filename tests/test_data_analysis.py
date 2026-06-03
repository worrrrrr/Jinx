"""Unit tests สำหรับ tools/data_analysis.py"""

import json
import os
import tempfile
from tools.data_analysis import analyze_data_handler, _compute_stats


SAMPLE_JSON = json.dumps([
    {"name": "A", "score": 10, "age": 20},
    {"name": "B", "score": 20, "age": 30},
    {"name": "C", "score": 30, "age": 40},
])


class TestDataAnalysis:
    def test_analyze_inline_json(self):
        out = analyze_data_handler("analyze", SAMPLE_JSON, [])
        assert out["status"] == "success"
        assert out["records"] == 3
        assert "score" in str(out.get("numeric_stats", {}))
        assert "age" in str(out.get("numeric_stats", {}))

    def test_analyze_inline_single_object(self):
        out = analyze_data_handler("analyze", json.dumps({"x": 5, "y": 10}), [])
        assert out["status"] == "success"
        assert out["records"] == 1

    def test_no_data_fails(self):
        out = analyze_data_handler("analyze", "", [])
        assert out["status"] == "fail"

    def test_csv_file_not_found(self):
        out = analyze_data_handler("analyze", "", ["nonexistent_data.csv"])
        assert out["status"] == "fail"

    def test_compute_stats_empty(self):
        out = _compute_stats([], "test")
        assert out["records"] == 0

    def test_compute_stats_single_column(self):
        data = [{"v": 1}, {"v": 2}, {"v": 3}]
        out = _compute_stats(data, "test")
        assert out["records"] == 3
        assert out["numeric_stats"]["v"]["mean"] == 2.0
        assert out["numeric_stats"]["v"]["min"] == 1.0
        assert out["numeric_stats"]["v"]["max"] == 3.0
