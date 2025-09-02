#!/usr/bin/env python3
import argparse
import re
import json
from collections import defaultdict

# ——— Split on lines that are *exactly* ==== <n> ==========
DELIM = re.compile(r'^====\s*\d+\s*={10}\s*$', re.MULTILINE)
OP_REGEX = re.compile(r'^(?:mutation|query)\s*(?:\w+)?\s*\{\s*(\w+)', re.IGNORECASE)

def split_sections(text):
    parts = DELIM.split(text)
    if parts and not parts[0].strip():
        parts = parts[1:]
    return [p.strip() for p in parts if p.strip()]

def extract_json_blocks(section: str):
    blocks = []
    i = section.find('{')
    while i != -1:
        depth = 0
        for j, ch in enumerate(section[i:], start=i):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    blocks.append(section[i:j+1])
                    i = section.find('{', j+1)
                    break
        else:
            break
    return blocks

def parse_file(path: str):
    with open(path, 'r') as f:
        text = f.read()

    entries = []
    for sec in split_sections(text):
        blocks = extract_json_blocks(sec)
        req = blocks[0] if len(blocks) > 0 else ''
        resp = blocks[1] if len(blocks) > 1 else ''
        entries.append({
            "request": req,
            "response": resp
        })

    return entries

def contains_non_null(obj):
    """Recursively check if any value in obj is not None."""
    if isinstance(obj, dict):
        return any(contains_non_null(v) for v in obj.values())
    if isinstance(obj, list):
        return any(contains_non_null(v) for v in obj)
    return obj is not None

def summarize(entries):
    # counters: endpoint -> { valid: int, error: int }
    stats = defaultdict(lambda: {"valid": 0, "error": 0})

    for e in entries:
        # 1) extract endpoint name from request JSON
        endpoint = "unknown"
        try:
            req_obj = json.loads(e["request"])
            q = req_obj.get("query", "").strip().splitlines()[0]
            m = OP_REGEX.search(q)
            if m:
                endpoint = m.group(1)
        except Exception:
            pass

        # 2) classify response
        has_error = False
        is_valid = False
        try:
            resp_obj = json.loads(e["response"])
            if "errors" in resp_obj:
                has_error = True
            elif "data" in resp_obj and contains_non_null(resp_obj["data"]):
                is_valid = True
        except json.JSONDecodeError:
            # treat parse failure as error
            has_error = True

        # 3) increment
        if has_error:
            stats[endpoint]["error"] += 1
        elif is_valid:
            stats[endpoint]["valid"] += 1
        else:
            # neither error nor valid (all-null data); count as error
            stats[endpoint]["error"] += 1

    return stats

def main():
    p = argparse.ArgumentParser(
        description="Extract request/response pairs and summarize per GraphQL endpoint"
    )
    p.add_argument(
        '-f', '--file',
        required=True,
        help="Path to <endpoint>-messages.txt"
    )
    args = p.parse_args()

    entries = parse_file(args.file)
    stats = summarize(entries)

    # Count endpoints with at least one valid, and with at least one error
    endpoints_with_valid = sum(1 for v in stats.values() if v["valid"] != 0)
    endpoints_with_errors = sum(1 for v in stats.values() if v["error"] != 0)

    # Print the per-endpoint stats and the summary counts
    print("Per-endpoint stats:")
    print(json.dumps(stats, indent=2))

    print(f"Unique endpoints with valid responses: {endpoints_with_valid}")
    print(f"Unique endpoints with error responses: {endpoints_with_errors}")


if __name__ == '__main__':
    main()
