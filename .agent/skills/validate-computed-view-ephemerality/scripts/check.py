import os
import re

COMPUTED_PATTERNS = [
    r"latency",
    r"volatility",
    r"share_of_voice",
    r"efficiency_",
]

def scan_file(path: str):
    with open(path, "r", errors="ignore") as f:
        content = f.read()
    matches = []
    for pattern in COMPUTED_PATTERNS:
        if re.search(pattern, content):
            matches.append(pattern)
    return matches

def main(root: str):
    violations = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for file in filenames:
            full = os.path.join(dirpath, file)
            matches = scan_file(full)
            if matches:
                violations[full] = matches
    if violations:
        return "EPHEMERAL_VIOLATION", violations
    return "EPHEMERAL_OK"
