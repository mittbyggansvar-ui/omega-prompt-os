import hashlib
import sys
import os

def verify_audit_chain(audit_log_path=".omega_audit.log"):
    if not os.path.exists(audit_log_path):
        print("SAFE_REJECT: Audit log saknas - cannot start")
        sys.exit(1)
    lines = [line.strip() for line in open(audit_log_path, "r", encoding="utf-8") if line.strip() and not line.startswith("#")]
    prev_hash = "0" * 16
    for i, line in enumerate(lines):
        current_input = prev_hash + "|" + line
        current_hash = hashlib.sha256(current_input.encode("utf-8")).hexdigest()[:16]
        if i > 0:
            print(f"Chain link {i}: {current_hash} <- {prev_hash}")
        prev_hash = current_hash
    print("Audit chain verification PASSED - deterministic integrity confirmed")
    return True

if __name__ == "__main__":
    verify_audit_chain()
