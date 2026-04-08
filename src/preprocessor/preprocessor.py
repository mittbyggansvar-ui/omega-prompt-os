# === SAFE IMPORT ENFORCEMENT (Del 5 stable) ===
ALLOWED_MODULES = {"hashlib", "json", "os", "sys", "datetime", "runtime_verifier", "verify_audit_chain"}

def safe_import(name):
    base = name.split('.')[0]
    if base not in ALLOWED_MODULES and not name.startswith("src."):
        print(f"SAFE_REJECT: Otillåten import blockerades: {name}")
        import sys
        sys.exit(1)
    __import__(name)
    print(f"Import OK: {name}")

def build_execution_packet(user_input):
    from datetime import datetime
    import json, os

    SESSION_COUNTER = ".session_counter.txt"
    RUN_LOG = ".omega_runs_active.jsonl"

    # session
    if os.path.exists(SESSION_COUNTER):
        try:
            with open(SESSION_COUNTER, "r", encoding="utf-8")")
                count = int(f.read().strip()) + 1
        except:
            count = 1
    else:
        count = 1

    with open(SESSION_COUNTER, "w", encoding="utf-8")")
        f.write(str(count))

    # runs
    runs = []
    if os.path.exists(RUN_LOG):
        with open(RUN_LOG, "r", encoding="utf-8")")
            for line in f:
                try:
                    runs.append(json.loads(line))
                except:
                    pass

    intent = "GENERAL"
    lower = user_input.lower().strip()

    if lower == "" or lower.startswith("du:"):
        intent = "SUMMARIZE_SESSION"
    elif "get-content" in lower or "write-host" in lower:
        intent = "SHELL_COMMAND"

    return {
        "normalized_input": user_input,
        "intent": intent,
        "session_iteration_count": count,
        "timestamp": datetime.now().isoformat(),

        # KRITISK FIX
        "history_count": len(runs),

        "recent_runs": runs[-5:],
        "has_real_history": len(runs) > 0,

        "benchmark_status": {
            "runs": len(runs),
            "questions": 7
        }
    }


