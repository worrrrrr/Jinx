# tools/data_analysis.py — Data Analysis Tool

import csv
import io
import json
import os
import statistics
from typing import Dict, Any, List, Callable


def get_tools() -> Dict[str, Callable]:
    return {
        "analyze_data": analyze_data_handler,
        "data_analysis": analyze_data_handler,
    }


def analyze_data_handler(action: str, inp: str, entities: List[str]) -> Dict[str, Any]:
    if not entities and not inp:
        return {"status": "fail", "message": "ไม่ระบุไฟล์หรือข้อมูลที่จะวิเคราะห์"}

    # ถ้ามี entities ให้ลองโหลดไฟล์
    source = entities[0] if entities else inp.strip()
    data = None

    if source.endswith(".csv"):
        data = _load_csv(source)
    elif source.endswith(".json"):
        data = _load_json(source)
    else:
        # ลอง parse เป็น JSON inline
        try:
            parsed = json.loads(source)
            if isinstance(parsed, dict):
                data = [parsed]
            elif isinstance(parsed, list):
                data = parsed
            else:
                return {"status": "fail", "message": f"JSON ต้องเป็น object หรือ array: {source}"}
        except (json.JSONDecodeError, TypeError):
            return {"status": "fail", "message": f"ไม่รู้จักรูปแบบข้อมูล: {source}"}

    if data is None:
        return {"status": "fail", "message": f"ไม่พบไฟล์หรืออ่านข้อมูลไม่ได้: {source}"}

    return _compute_stats(data, source)


def _load_csv(path: str) -> List[Dict[str, Any]]:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full = os.path.join(root, path)
    if not os.path.exists(full):
        return None
    with open(full, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _load_json(path: str) -> List[Dict[str, Any]]:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full = os.path.join(root, path)
    if not os.path.exists(full):
        return None
    with open(full, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [data]
    return data


def _compute_stats(data: List[Dict[str, Any]], source: str) -> Dict[str, Any]:
    if not data:
        return {"status": "success", "result": "ไม่มีข้อมูล", "records": 0}

    keys = list(data[0].keys())
    numeric_cols = []
    stats = {}

    for col in keys:
        vals = []
        for row in data:
            try:
                vals.append(float(row[col]))
            except (ValueError, TypeError):
                continue
        if vals:
            numeric_cols.append(col)
            stats[col] = {
                "count": len(vals),
                "mean": round(statistics.mean(vals), 4),
                "min": round(min(vals), 4),
                "max": round(max(vals), 4),
                "stdev": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0,
            }
            if any(v != int(v) for v in vals):
                stats[col]["median"] = round(statistics.median(vals), 4)

    result_lines = [f"📊 วิเคราะห์ข้อมูลจาก {source} ({len(data)} รายการ)"]
    result_lines.append(f"คอลัมน์: {', '.join(keys)}")
    for col, s in stats.items():
        parts = [f"{k}={v}" for k, v in s.items()]
        result_lines.append(f"  {col}: {', '.join(parts)}")

    return {
        "status": "success",
        "result": "\n".join(result_lines),
        "source": source,
        "records": len(data),
        "columns": keys,
        "numeric_stats": stats,
        "engine": "data_analysis",
    }
