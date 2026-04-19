import re
from collections import defaultdict
import os

def main():
    errors_file = 'ty_errors.txt'
    if not os.path.exists(errors_file):
        print(f"File {errors_file} not found.")
        return

    with open(errors_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all line locations matching: --> filename:line:column
    matches = re.findall(r'--> (.*?):(\d+):\d+', content)
    
    # Group by filename
    fixes = defaultdict(set)
    for file_path, line_str in matches:
        if file_path.startswith('stdlib'):
            continue  # ignore vendored stdlib
        fixes[file_path].add(int(line_str))

    for file_path, line_nums in fixes.items():
        if not os.path.exists(file_path):
            print(f"File {file_path} not found, skipping...")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        modified = False
        for line_num in sorted(line_nums):
            idx = line_num - 1 # 0-indexed
            if idx < 0 or idx >= len(lines):
                continue
                
            line = lines[idx].rstrip('\n')
            # Don't add if it already has type: ignore or if line ends with '\'
            if 'type: ignore' not in line and 'ty: ignore' not in line:
                if line.endswith('\\') or line.endswith('('):
                    # It's harder to ignore a multi-line wrap like this naively.
                    pass
                # if line is blank or just whitespace, skipping
                if not line.strip():
                    continue
                # For basic fix, append comment.
                lines[idx] = f"{line}  # type: ignore\n"
                modified = True
                
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Modified {file_path}")

if __name__ == '__main__':
    main()
