import hashlib
import json
import sys
import os

def load_manifest():
    with open("omega_runtime_manifest.json", "r", encoding="utf-8-sig") as f:
        return json.load(f)

def verify_file_hash(file_path, expected_hash):
    if not os.path.exists(file_path):
        print(f"SAFE_REJECT: Fil saknas: {file_path}")
        sys.exit(1)
    actual = hashlib.sha256(open(file_path, "rb").read()).hexdigest().lower()
    if actual != expected_hash.lower():
        print(f"SAFE_REJECT: Hash mismatch för {file_path} (expected: {expected_hash}, got: {actual})")
        sys.exit(1)
    return True

def runtime_verify():
    manifest = load_manifest()
    for item in manifest.get("active_line", []):
        verify_file_hash(item["path"], item["sha256"])
    print("Runtime verification OK - only active line loaded (fail-closed enforced)")
    return True

if __name__ == "__main__":
    runtime_verify()

