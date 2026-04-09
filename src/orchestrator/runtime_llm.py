import os
import sys

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

def is_allowed_module(name):
    base = name.split(".")[0]
    return base in ALLOWED_MODULES or name.startswith("src.")

def safe_import(name):
    if not is_allowed_module(name):
        print(f"SAFE_REJECT: Otillåten import blockerades: {name}")
        sys.exit(1)
    __import__(name)

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

def display_model_name(model):
    if model == "grok":
        return "Grok-3"
    if model == "openai":
        return "OpenAI"
    return str(model)

def validate_output(response_text):
    if not response_text or not str(response_text).strip():
        raise RuntimeError("LLM returned empty output")
    return str(response_text).strip()
