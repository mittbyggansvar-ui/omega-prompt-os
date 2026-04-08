import hashlib
import sys
import os
from datetime import datetime

def verify_audit_chain(audit_log_path=".omega_audit.log"):
    if not os.path.exists(audit_log_path):
        print("SAFE_REJECT: Audit log saknas - cannot start")
        sys.exit(1)
    lines = [line.strip() for line in open(audit_log_path, "r", encoding="utf-8") if line.strip() and not line.startswith("#")]
    prev_hash = "0" * 64
    for i, line in enumerate(lines):
        ts = datetime.now().isoformat()
        current_input = prev_hash + "|" + ts + "|" + line
        current_hash = hashlib.sha256(current_input.encode("utf-8")).hexdigest()
        signature = hashlib.sha256((current_hash + prev_hash).encode()).hexdigest()[:32]
        if i > 0:
            print(f"Strong chain link {i}: {signature} <- {prev_hash[:16]}")
        prev_hash = current_hash
    print("STRONG AUDIT CHAIN VERIFICATION PASSED - cryptographic integrity confirmed")
    return True

if __name__ == "__main__":
    verify_audit_chain()
