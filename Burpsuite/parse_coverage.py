import csv
import base64
import json
import sys
import os
from collections import defaultdict
from datetime import datetime, timedelta

csv.field_size_limit(sys.maxsize)


def decode_base64(encoded_str):
    try:
        decoded_str = base64.b64decode(encoded_str).decode("utf-8")
        json_start = decoded_str.find("{")
        if json_start != -1:
            return decoded_str[json_start:]
        return decoded_str
    except Exception as e:
        # print(f"Error decoding base64: {e}")
        return ""


def extract_endpoint(request_payload):
    try:
        request_dict = json.loads(request_payload)
        query = request_dict.get("query", {})
        if "mutation" in query:
            start = query.index("mutation") + len("mutation")
        elif "query" in query:
            start = query.index("query") + len("query")
        else:
            return "unknown"
        start = query.index("{", start) + 1
        end = (
            query.index("(", start) if "(" in query[start:] else query.index("}", start)
        )
        return query[start:end].strip()
    except Exception as e:
        pass
    return "unknown"


def process_csv(file_path, curoff_seconds):
    endpoint_stats = defaultdict(lambda: {"pass": 0, "fail": 0})
    with open(file_path, mode="r") as csv_file:
        reader = csv.DictReader(csv_file)

        timestamps = [row.get("Time") for row in reader]
        earliest_timestamp = min(timestamps)
        earliest_time = datetime.fromisoformat(earliest_timestamp)
        cutoff_time = earliest_time + timedelta(seconds=curoff_seconds)

        csv_file.seek(0)
        next(reader)

        for row in reader:
            entry_time = datetime.fromisoformat(row.get("Time"))
            if not (earliest_time <= entry_time <= cutoff_time):
                continue

            status_code = row.get("Status code")
            request_encoded = row.get("Request")
            response_encoded = row.get("Response")

            request = decode_base64(request_encoded)
            response = decode_base64(response_encoded)

            endpoint = extract_endpoint(request)

            try:
                response_dict = json.loads(response)
                if (
                    "data" not in response_dict
                    or response_dict["data"] is None
                    or endpoint not in response_dict["data"]
                ) and (
                    "errors" not in response_dict or response_dict["errors"] is None
                ):
                    endpoint_stats[endpoint]["fail"] += 1
                elif "error" in response.lower():
                    if all(
                        err not in response.lower()
                        for err in ["syntax error", "validation error", "query error"]
                    ):
                        endpoint_stats[endpoint]["fail"] += 1
                elif (
                    status_code == "200" and response_dict["data"][endpoint] is not None
                ):
                    endpoint_stats[endpoint]["pass"] += 1
                elif status_code == "400":
                    endpoint_stats[endpoint]["fail"] += 1
            except Exception as e:
                endpoint_stats[endpoint]["fail"] += 0

    # Remove anything that isn't a proper endpoint (due to bad characters / CSV format issues)
    # Also remove introspection fields and internal system types (with __)
    formatted_endpoint_stats = {}
    for endpoint, stats in endpoint_stats.items():
        if " " in endpoint or endpoint.startswith("__") or endpoint in ['query', 'mutation']:
            continue
        else:
            formatted_endpoint_stats[endpoint] = stats

    return formatted_endpoint_stats


def calculate_positive_coverage(stats):
    total_endpoints = len(stats.keys())
    total_passes = sum(counts["pass"] for counts in stats.values())
    if total_endpoints == 0:
        return 0.0
    return (total_passes / total_endpoints) * 100

def calculate_negative_coverage(stats):
    total_endpoints = len(stats.keys())
    total_failures = sum(counts["fail"] for counts in stats.values())
    if total_endpoints == 0:
        return 0.0
    return (total_failures / total_endpoints) * 100

def main():
    cutoff_times = [5, 10, 20, 30, 60]
    current_dir = os.getcwd()
    csv_files = [
        f
        for f in os.listdir(current_dir)
        if f.endswith(".csv") and not f.endswith("-decoded.csv")
    ]

    for csv_file in csv_files:
        print(f"\nProcessing file: {csv_file}")
        for cutoff in cutoff_times:
            stats = process_csv(csv_file, cutoff)
            positive_coverage = calculate_positive_coverage(stats)
            negative_coverage = calculate_negative_coverage(stats)
            endpoints_with_pass = sum(1 for endpoint, counts in stats.items() if counts["pass"] > 0)
            endpoints_with_fail = sum(1 for endpoint, counts in stats.items() if counts["fail"] > 0)
            print(f"Cutoff Time: {cutoff} seconds - Positive Coverage: {positive_coverage:.2f}% - Endpoints with Pass: {endpoints_with_pass}")
            print(f"Cutoff Time: {cutoff} seconds - Negative Coverage: {negative_coverage:.2f}% - Endpoints with Pass: {endpoints_with_fail}")



if __name__ == "__main__":
    main()
