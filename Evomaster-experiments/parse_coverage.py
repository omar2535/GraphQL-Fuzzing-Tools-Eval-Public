#!/usr/bin/env python3
# Parses EvoMaster GraphQL black-box tests in a directory
# For <prefix>_successes_Test.java: reports non-nullValue assertions per test
# For <prefix>_faults_Test.java: counts total tests

import re
import sys
import os
import glob

def parse_successes(java_source: str):
    decl_pattern = re.compile(r'public void (test_\d+)\s*\(\)\s*throws Exception\s*\{')
    decls = [(m.group(1), m.start()) for m in decl_pattern.finditer(java_source)]
    results = []
    total_flagged = 0

    for i, (test_name, start_idx) in enumerate(decls):
        end_idx = decls[i+1][1] if i+1 < len(decls) else len(java_source)
        block = java_source[start_idx:end_idx]

        op_match = re.search(
            r'"query"\s*:\s*"\s*(?:mutation\s*\{\s*)?([A-Za-z_][A-Za-z0-9_]*)',
            block
        )
        op_name = op_match.group(1) if op_match else "<unknown>"

        non_null_count = 0
        for matcher in re.findall(r'\.body\s*\(\s*[^,]+,\s*([A-Za-z0-9_\.]+\([^)]*\))\s*\)', block):
            if not matcher.startswith('nullValue'):
                non_null_count += 1

        # flag once per test
        if non_null_count:
            total_flagged += 1
        results.append((test_name, op_name, non_null_count))

    return results, total_flagged

# Count tests in faults file

def count_fault_tests(java_source: str):
    decl_pattern = re.compile(r'public void (test_\d+)\s*\(\)\s*throws Exception\s*\{')
    return len(decl_pattern.findall(java_source))


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory_path>")
        sys.exit(1)

    dir_path = sys.argv[1]
    if not os.path.isdir(dir_path):
        print(f"Error: '{dir_path}' is not a directory")
        sys.exit(1)

    # Find successes and faults files
    successes_files = glob.glob(os.path.join(dir_path, '*_successes_Test.java'))
    faults_files = glob.glob(os.path.join(dir_path, '*_faults_Test.java'))

    if not successes_files:
        print("No '_successes_Test.java' file found in directory.")
    else:
        for path in successes_files:
            # print(f"Processing successes file: {os.path.basename(path)}")
            with open(path, 'r') as f:
                src = f.read()
            results, total = parse_successes(src)
            # for test_name, op_name, count in results:
            #     print(f"{test_name}: operation `{op_name}`, non-nullValue assertions = {count}")
            # print("="*50)
            print(f"Total tests with non-nullValue assertions: {total}")

    if not faults_files:
        print("No '_faults_Test.java' file found in directory.")
    else:
        for path in faults_files:
            # print(f"Processing faults file: {os.path.basename(path)}")
            with open(path, 'r') as f:
                src = f.read()
            count = count_fault_tests(src)
            print(f"Total number of tests in faults file: {count}")

if __name__ == '__main__':
    main()
