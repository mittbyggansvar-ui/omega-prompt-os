import hashlib
import json
import sys
import os

def load_manifest():
    with open("omega_runtime_manifest.json", "r", encoding="utf-8") as f:
        return json.load(f)

def verify_file_hash(file_path, expected_hash):
    if not os.path.exists(file_path):
        print(f"SAFE_REJECT: Fil saknas: {file_path}")
        sys.exit(1)
    actual = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
    if actual != expected_hash:
        print(f"SAFE_REJECT: Hash mismatch för {file_path}")
        sys.exit(1)
    return True

def runtime_verify():
    manifest = load_manifest()
    active_files = ["src/orchestrator/main.py", "src/preprocessor/preprocessor.py", "src/layers/layer1_constitution.txt"]
    for f in active_files:
        key = f"hash_{f.replace('/', '_').replace('\\', '_')}"
        if key in manifest:
            verify_file_hash(f, manifest[key])
    print("Runtime verification OK - only active line loaded")
    return True

if __name__ == "__main__":
    runtime_verify()
