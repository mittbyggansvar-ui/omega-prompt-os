# Ω Prompt OS v1.27 - Clean Active Line
# Grok-3 primary + OpenAI fallback + full enforcement

import os
import sys
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# === SAFE IMPORT ENFORCEMENT ===
ALLOWED_MODULES = {
    "hashlib", "json", "os", "sys", "datetime", "dotenv",
    "langchain_xai", "langchain_openai", "runtime_verifier", "verify_audit_chain"
}

def safe_import(name):
    base = name.split('.')[0]
    if base not in ALLOWED_MODULES and not name.startswith("src."):
        print(f"SAFE_REJECT: Otillåten import blockerades: {name}")
        sys.exit(1)
    __import__(name)

# Runtime enforcement
from src.orchestrator.runtime_verifier import runtime_verify
from src.orchestrator.runtime_verifier import runtime_verify
runtime_verify()

# Audit enforcement
from src.orchestrator.verify_audit_chain import verify_audit_chain
from src.orchestrator.verify_audit_chain import verify_audit_chain
verify_audit_chain()

# LLM setup
safe_import("langchain_xai")
safe_import("langchain_openai")
from langchain_xai import ChatXAI
from langchain_openai import ChatOpenAI

llm_grok = ChatXAI(model="grok-3", temperature=0)
llm_openai = ChatOpenAI(model="gpt-4o-mini", temperature=0)

print("Ω Prompt OS ACTIVE LINE loaded - Grok-3 primary + OpenAI fallback")

# Huvudfunktion
def process_input(user_input: str):
    try:
        response = llm_grok.invoke(user_input)
        model_used = "Grok-3"
    except Exception as e:
        print(f"Grok failed: {e}, falling back to OpenAI")
        response = llm_openai.invoke(user_input)
        model_used = "OpenAI"

    print(f"Model used: {model_used}")
    print(f"Svar: {response.content}")
    return response.content

# För test
if __name__ == "__main__":
    test = "Hej, hur mår du idag?"
    process_input(test)




