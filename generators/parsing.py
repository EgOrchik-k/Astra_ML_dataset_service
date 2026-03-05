#паресер независимо от файла выдает
#всегда одинаковый структурированные
#данные: list[dict]

import csv
import io
import json
import re
from typing import List, Dict, Any, Optional

KV_RE = re.compile(r"(\w+)=([^\s]+)")

def _parse_csv(text: str) -> List[Dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]

def _parse_json(text: str) -> List[Dict[str, Any]]:
    obj = json.loads(text)
    if isinstance(obj, list):
        if not all(isinstance(x, dict) for x in obj):
            raise ValueError("JSON list must contain objects")
        return obj
    if isinstance(obj, dict):
        return [obj]
    raise ValueError("Unsupported JSON structure")

def _parse_jsonl(text: str) -> List[Dict[str, Any]]:
    rows = []
    for i, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSONL decode error on line {i}: {e}")
        if not isinstance(obj, dict):
            raise ValueError(f"JSONL line {i} must be an object")
        rows.append(obj)
    return rows

def _parse_kv_log(text: str) -> List[Dict[str, Any]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        pairs = KV_RE.findall(line)
        if pairs:
            rows.append({k: v for k, v in pairs})
        else:
            # fallback: сохраняем как "message"
            rows.append({"message": line})
    return rows

def parse_bytes(raw: bytes, filename: Optional[str] = None) -> List[Dict[str, Any]]:
    text = raw.decode("utf-8", errors="ignore")
    ext = ""
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "csv":
        return _parse_csv(text)
    if ext == "json":
        return _parse_json(text)
    if ext in ("jsonl", "ndjson"):
        return _parse_jsonl(text)

    # по умолчанию: логовый key=value / message
    return _parse_kv_log(text)