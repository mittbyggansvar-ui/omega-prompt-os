
# === RUNTIME ENFORCEMENT - FAIL-CLOSED ===
# ABSOLUT SIMULATION LOCK + boundary proof
safe_import("runtime_verifier import runtime_verify
runtime_verify()

# Audit chain verification at startup
safe_import("verify_audit_chain import verify_audit_chain
verify_audit_chain()


# === MILJÖSKYDD - ZERO-TRUST ===
import os
os.environ.clear()  # Rensa alla env-variabler
os.environ["PYTHONIOENCODING"] = "utf-8  # Endast tillåtna
# Blockera subprocess
import subprocess
subprocess.Popen = lambda *args, **kwargs: (_ for _ in ()).throw(Exception("SAFE_REJECT: subprocess blocked"))


# === STRICT IMPORT ENFORCEMENT - ZERO-TRUST ===
ALLOWED_MODULES = {
    "hashlib", "json", "os", "sys", "datetime", "runtime_verifier", "verify_audit_chain
}

def safe_import(name):
    base = name.split('.')[0]
    if base not in ALLOWED_MODULES and not name.startswith("src."):
        print(f"SAFE_REJECT: Otillåten import blockerades: {name}")
        import sys
        sys.exit(1)
    __import__(name)
    print(f"Import OK: {name}")

safe_import("sys
safe_import("os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

sys.stdout.reconfigure(encoding="utf-8")

safe_import("json
safe_import("hashlib
safe_import("datetime import datetime
safe_import("dotenv import load_dotenv
safe_import("langchain_xai import ChatXAI
safe_import("langchain_openai import ChatOpenAI

load_dotenv()

safe_import("src.preprocessor.preprocessor import build_execution_packet

RUN_LOG = ".omega_runs_active.jsonl
ACTIVE_VERSION = "ACTIVE_LINE

FORBIDDEN_EXTERNAL_TERMS = [
    "gdpr",
    "hipaa",
    "iso 27001",
    "iso27001",
    "soc 2",
    "soc2",
    "nist",
    "pci-dss",
    "pci dss
]

FORBIDDEN_VERSION_TERMS = [
    "v1.0","v1.1","v1.2","v1.3","v1.4","v1.5","v1.6","v1.7","v1.8","v1.9",
    "v1.10","v1.11","v1.12","v1.13","v1.14","v1.15","v1.16","v1.17","v1.18","v1.19",
    "v1.20","v1.21","v1.22","v1.23","v1.24","v1.25","v1.26","v1.27","v1.28","v1.29","v1.30","v1.31","v1.32
]

print("= * 90)
print("Ω Prompt OS - ACTIVE LINE")
print("ABSOLUT SIMULATION LOCK: AKTIV")
print("STRICT RESPONSE CONTRACT: AKTIV")
print(f"Project root: {PROJECT_ROOT}")
print("= * 90)

def build_strict_prompt(constitution, packet, effective_input):
    intent = packet["intent"]

    if intent == "GENERAL":
        output_contract = "
Tillåtet svarformat för GENERAL:

STRICT ANSWER
INTENT: <intent>
INPUT: <normalized_input>
SESSION_ITERATION: <number>
HISTORY_COUNT: <number>
ANSWER:
- <kort saklig punkt 1>
- <kort saklig punkt 2>
- <kort saklig punkt 3>

Regler:
- Exakt rubrik "STRICT ANSWER
- Exakt en rad för INTENT
- Exakt en rad för INPUT
- Exakt en rad för SESSION_ITERATION
- Exakt en rad för HISTORY_COUNT
- Exakt en ANSWER-sektion
- Max 3 punktlistor i ANSWER
- Inga extra sektioner
- Inga rekommendationer om inte användaren uttryckligen bad om det
- Nämn aldrig versionsnummer
"
    elif intent == "SUMMARIZE_SESSION":
        output_contract = "
Tillåtet svarformat för SUMMARIZE_SESSION:

STATUS REPORT
INTENT: <intent>
SESSION_ITERATION: <number>
HISTORY_COUNT: <number>
SUMMARY:
- <punkt 1 baserad på verklig recent_runs>
- <punkt 2 baserad på verklig recent_runs>
- <punkt 3 baserad på verklig recent_runs>

Regler:
- Exakt rubrik "STATUS REPORT
- Exakt en rad för INTENT
- Exakt en rad för SESSION_ITERATION
- Exakt en rad för HISTORY_COUNT
- Exakt en SUMMARY-sektion
- Max 3 punktlistor i SUMMARY
- Inga extra sektioner
- Ingen improviserad historik
- Nämn aldrig versionsnummer
"
    elif intent == "SHELL_COMMAND":
        output_contract = "
Tillåtet svarformat för SHELL_COMMAND:

STRICT ANSWER
INTENT: <intent>
INPUT: <normalized_input>
SESSION_ITERATION: <number>
HISTORY_COUNT: <number>
ANSWER:
- <vad kommandot gör>
- <att det behandlas som kod/shell>
- <ingen simulering>

Regler:
- Exakt rubrik "STRICT ANSWER
- Exakt en rad för INTENT
- Exakt en rad för INPUT
- Exakt en rad för SESSION_ITERATION
- Exakt en rad för HISTORY_COUNT
- Exakt en ANSWER-sektion
- Max 3 punktlistor i ANSWER
- Inga extra sektioner
- Säg aldrig att detta är simulering
- Nämn aldrig versionsnummer
"
    else:
        output_contract = "
Tillåtet svarformat:

STRICT ANSWER
INTENT: <intent>
INPUT: <normalized_input>
SESSION_ITERATION: <number>
HISTORY_COUNT: <number>
ANSWER:
- <kort saklig punkt 1>
"

    prompt = f"{constitution}

Execution Packet:
{json.dumps(packet, ensure_ascii=False, indent=2)}

STRICT RESPONSE CONTRACT:
{output_contract}

Obligatoriska regler:
- Använd endast execution packet som källa.
- Använd endast active line-historik.
- Nämn aldrig gamla versioner eller någon v1.xx.
- Lägg inte till externa standarder eller ramverk.
- Lägg inte till egna förbättringsförslag om användaren inte uttryckligen frågar efter förbättringar.
- Håll dig strikt till tillåtet svarformat.
- Om du bryter mot formatet kommer svaret att underkännas.

Användarfråga:
{effective_input if effective_input else "[TOM INPUT]"}
    return prompt

def validate_response(response, packet):
    if response is None:
        return False, "SAFE_REJECT: Tomt svar från modellen.

    text = str(response).strip()
    lower = text.lower()

    if text == "":
        return False, "SAFE_REJECT: Tomt svar efter trimning.

    for term in FORBIDDEN_EXTERNAL_TERMS:
        if term in lower:
            return False, f"SAFE_REJECT: Otillåtet externt tillägg upptäckt ({term}).

    for term in FORBIDDEN_VERSION_TERMS:
        if term in lower:
            return False, f"SAFE_REJECT: Gammalt versionsspår upptäckt ({term}).

    if text.count("Benchmark Status") > 1:
        return False, "SAFE_REJECT: Dubbelt benchmarkblock upptäckt.

    intent = packet.get("intent")
    expected_header = "STATUS REPORT if intent == "SUMMARIZE_SESSION else "STRICT ANSWER

    lines = [line.rstrip() for line in text.splitlines() if line.strip() != ""]
    if len(lines) < 6:
        return False, "SAFE_REJECT: För kort eller ofullständigt svar.

    if lines[0] != expected_header:
        return False, f"SAFE_REJECT: Fel huvudrubrik. Förväntade {expected_header}.

    required_common = [
        f"INTENT: {intent}",
        f"SESSION_ITERATION: {packet['session_iteration_count']}",
        f"HISTORY_COUNT: {packet['history_count']}
    ]

    for req in required_common:
        if req not in text:
            return False, f"SAFE_REJECT: Saknar obligatoriskt fält ({req}).

    if intent in ["GENERAL", "SHELL_COMMAND"]:
        req_input = f"INPUT: {packet['normalized_input']}
        if req_input not in text:
            return False, f"SAFE_REJECT: Saknar korrekt INPUT-fält ({req_input}).
        if "ANSWER: not in text:
            return False, "SAFE_REJECT: Saknar ANSWER-sektion.

    if intent == "SUMMARIZE_SESSION":
        if "SUMMARY: not in text:
            return False, "SAFE_REJECT: Saknar SUMMARY-sektion.

    bullet_count = sum(1 for line in lines if line.startswith("- "))
    if bullet_count < 1:
        return False, "SAFE_REJECT: Saknar punktlista.
    if bullet_count > 3:
        return False, "SAFE_REJECT: För många punktlistor.

    if intent == "SHELL_COMMAND":
        if "simulering in lower and "ingen simulering not in lower:
            return False, "SAFE_REJECT: Shell-input feltolkad som simulering.

    if intent == "SUMMARIZE_SESSION and not packet.get("has_real_history", False):
        if "ingen verklig aktiv körhistorik not in lower and "safe_reject not in lower:
            return False, "SAFE_REJECT: Summering utan historik försökte improvisera.

    return True, "VALID

while True:
    user_input = input("\nDu: ").strip()

    if user_input.lower() in ["exit", "quit", "avsluta"]:
        print("Avslutar Ω Prompt OS ACTIVE LINE. Hej då!")
        break

    packet = build_execution_packet(user_input)
    effective_input = packet["normalized_input"]

    constitution_path = os.path.join(PROJECT_ROOT, "src", "layers", "layer1_constitution.txt")
    with open(constitution_path, "r", encoding="utf-8")")
        constitution = f.read()

    response = None
    model_used = "UNKNOWN
    safe_reject = False
    validation_status = "NOT_RUN

    if packet["intent"] == "SUMMARIZE_SESSION and not packet["has_real_history"]:
        response = "SAFE_REJECT: Ingen verklig aktiv körhistorik finns ännu att sammanfatta.
        model_used = "RULE_ENGINE
        safe_reject = True
        validation_status = "RULE_ENGINE_REJECT

    if response is None:
        prompt = build_strict_prompt(constitution, packet, effective_input)

        try:
            llm = ChatXAI(model="grok-3", temperature=0.0)
            response = llm.invoke(prompt).content
            model_used = "Grok-3
        except Exception:
            try:
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
                response = llm.invoke(prompt).content
                model_used = "OpenAI gpt-4o-mini
            except Exception:
                if packet["intent"] == "SUMMARIZE_SESSION and packet["has_real_history"]:
                    bullets = []
                    for run in packet["recent_runs"][-3:]:
                        bullets.append(f"- {run.get('intent','UNKNOWN')}: {str(run.get('input',")).strip()[:80]}")
                    response = (
                        "STATUS REPORT\n
                        f"INTENT: {packet['intent']}\n
                        f"SESSION_ITERATION: {packet['session_iteration_count']}\n
                        f"HISTORY_COUNT: {packet['history_count']}\n
                        "SUMMARY:\n + "\n".join(bullets[:3])
                    )
                elif packet["intent"] == "SUMMARIZE_SESSION":
                    response = "SAFE_REJECT: Ingen verklig aktiv körhistorik finns ännu.
                    safe_reject = True
                elif packet["intent"] == "SHELL_COMMAND":
                    response = (
                        "STRICT ANSWER\n
                        f"INTENT: {packet['intent']}\n
                        f"INPUT: {packet['normalized_input']}\n
                        f"SESSION_ITERATION: {packet['session_iteration_count']}\n
                        f"HISTORY_COUNT: {packet['history_count']}\n
                        "ANSWER:\n
                        "- Kommandot behandlas som kod/shell.\n
                        "- Systemet exekverar inte kommandot i denna runtime.\n
                        "- Ingen simulering används.
                    )
                else:
                    response = (
                        "STRICT ANSWER\n
                        f"INTENT: {packet['intent']}\n
                        f"INPUT: {packet['normalized_input']}\n
                        f"SESSION_ITERATION: {packet['session_iteration_count']}\n
                        f"HISTORY_COUNT: {packet['history_count']}\n
                        "ANSWER:\n
                        "- Lokal fallback aktiv.\n
                        "- Externa LLM-anrop misslyckades.\n
                        "- Svar begränsat till aktiv runtime.
                    )
                model_used = "LOCAL FALLBACK

    if not safe_reject:
        is_valid, validation_message = validate_response(response, packet)
        if not is_valid:
            response = validation_message
            safe_reject = True
            validation_status = "POST_VALIDATION_REJECT
            model_used = "RULE_ENGINE
        else:
            validation_status = "VALID

    signature_base = f"{effective_input}|{response}|{packet['intent']}
    signature = hashlib.sha256(signature_base.encode("utf-8")).hexdigest()[:16]

    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": effective_input,
        "raw_input": user_input,
        "intent": packet["intent"],
        "model_used": model_used,
        "response": response,
        "session_iteration_count": packet["session_iteration_count"],
        "signature": signature,
        "safe_reject": safe_reject,
        "validation_status": validation_status
    }

    run_log_path = os.path.join(PROJECT_ROOT, RUN_LOG)
    with open(run_log_path, "a", encoding="utf-8")")
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\nΩ Prompt OS ACTIVE LINE:")
    print(f" -> Model used: {model_used}")
    print(f" -> Intent: {packet['intent']}")
    print(f" -> Effective input: {effective_input}")
    print(f" -> Session iteration: {packet['session_iteration_count']}")
    print(f" -> SAFE_REJECT: {safe_reject}")
    print(f" -> Validation: {validation_status}")
    print(f" -> Signature: {signature}")
    print(f" -> Svar: {response}")
    print(f"[RunLog] Entry appended -> {run_log_path}")







