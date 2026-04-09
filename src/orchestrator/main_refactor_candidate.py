# Ω Prompt OS v1.27 - Refactor Candidate Runtime v1
# Grok-3 primary + OpenAI fallback

import os
import sys
from dotenv import load_dotenv

BOOT_BANNER = "Ω Prompt OS ACTIVE LINE loaded - Grok-3 primary + OpenAI fallback"
BOOTSTRAPPED = False

# Safe import enforcement
ALLOWED_MODULES = {
    "hashlib",
    "json",
    "os",
    "sys",
    "datetime",
    "dotenv",
    "langchain_xai",
    "langchain_openai",
    "runtime_verifier",
    "verify_audit_chain",
}

from .runtime_modes import resolve_mode, resolve_intent, build_prompt

def is_allowed_module(name):
    base = name.split(".")[0]
    return base in ALLOWED_MODULES or name.startswith("src.")

def safe_import(name):
    if not is_allowed_module(name):
        print(f"SAFE_REJECT: Otillåten import blockerades: {name}")
        sys.exit(1)
    __import__(name)

def bootstrap_environment():
    load_dotenv()

def bootstrap_runtime_verification():
    from .runtime_verifier import runtime_verify
    runtime_verify()

def bootstrap_audit_verification():
    from .verify_audit_chain import verify_audit_chain
    verify_audit_chain()

def bootstrap_banner():
    print(BOOT_BANNER)

def bootstrap_active_line():
    bootstrap_environment()
    bootstrap_runtime_verification()
    bootstrap_audit_verification()
    bootstrap_banner()

def route_model(intent):
    if os.getenv("XAI_API_KEY"):
        return "grok"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    raise RuntimeError("No supported LLM credentials found. Set XAI_API_KEY or OPENAI_API_KEY.")

def _extract_text(response):
    if response is None:
        return ""
    if isinstance(response, str):
        return response.strip()
    content = getattr(response, "content", None)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
        return "\n".join(parts).strip()
    return str(response).strip()

def call_grok(prompt):
    safe_import("langchain_xai")
    from langchain_xai import ChatXAI

    model_name = os.getenv("OMEGA_GROK_MODEL", "grok-3")
    temperature = float(os.getenv("OMEGA_TEMPERATURE", "0"))

    llm = ChatXAI(
        model=model_name,
        temperature=temperature,
        api_key=os.getenv("XAI_API_KEY")
    )

    response = llm.invoke(prompt)
    return _extract_text(response)

def call_openai(prompt):
    safe_import("langchain_openai")
    from langchain_openai import ChatOpenAI

    model_name = os.getenv("OMEGA_OPENAI_MODEL", "gpt-4.1")
    temperature = float(os.getenv("OMEGA_TEMPERATURE", "0"))

    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = llm.invoke(prompt)
    return _extract_text(response)

def call_llm(model, prompt):
    if model == "grok":
        return call_grok(prompt)
    if model == "openai":
        return call_openai(prompt)
    raise RuntimeError(f"Unsupported model route: {model}")

def validate_output(response_text):
    if not response_text or not str(response_text).strip():
        raise RuntimeError("LLM returned empty output")
    return str(response_text).strip()

def ensure_bootstrapped():
    global BOOTSTRAPPED
    if not BOOTSTRAPPED:
        bootstrap_active_line()
        BOOTSTRAPPED = True

def run_with_meta(user_input, mode="default"):
    ensure_bootstrapped()
    intent = resolve_intent(user_input, mode)
    prompt = build_prompt(intent)
    model = route_model(intent)
    raw_output = call_llm(model, prompt)
    output = validate_output(raw_output)
    return model, output

def run(user_input, mode="default"):
    _, output = run_with_meta(user_input, mode)
    return output


def process(user_input: str):
    return run(user_input, mode="default")

if __name__ == "__main__":
    test = "Hej, hur mår du idag?"
    model, result = run_with_meta(test, mode="default")
    print(f"Model used: {model}")
    print(f"Svar: {result}")






