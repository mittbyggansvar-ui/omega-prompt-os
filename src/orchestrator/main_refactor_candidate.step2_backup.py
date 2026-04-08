# Ω Prompt OS v1.27 - Clean Modular Active Line
# Grok-3 primary + OpenAI fallback

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Safe import enforcement
ALLOWED_MODULES = {"hashlib", "json", "os", "sys", "datetime", "dotenv", "langchain_xai", "langchain_openai", "runtime_verifier", "verify_audit_chain"}

def safe_import(name):
    base = name.split('.')[0]
    if base not in ALLOWED_MODULES and not name.startswith("src."):
        print(f"SAFE_REJECT: Otillåten import blockerades: {name}")
        sys.exit(1)
    __import__(name)

# Enforcement
from .runtime_verifier import runtime_verify
runtime_verify()

from src.orchestrator.verify_audit_chain import verify_audit_chain
from .verify_audit_chain import verify_audit_chain

def bootstrap_environment():
    load_dotenv()

def bootstrap_runtime_verification():
    runtime_verify()

def bootstrap_audit_verification():
    verify_audit_chain()

def bootstrap_banner():
    print("Ω Prompt OS ACTIVE LINE loaded - Grok-3 primary + OpenAI fallback")
verify_audit_chain()

# LLM clients
safe_import("langchain_xai")
safe_import("langchain_openai")
from langchain_xai import ChatXAI
from langchain_openai import ChatOpenAI

llm_grok = ChatXAI(model="grok-3", temperature=0)
llm_openai = ChatOpenAI(model="gpt-4o-mini", temperature=0)

print("Ω Prompt OS ACTIVE LINE loaded - Grok-3 primary + OpenAI fallback")

# Huvudfunktion - explicit entrypoint
def process(user_input: str):
    try:
        response = llm_grok.invoke(user_input)
        model = "Grok-3"
    except Exception as e:
        print(f"Grok failed: {e}, falling back to OpenAI")
        response = llm_openai.invoke(user_input)
        model = "OpenAI"
    
    print(f"Model used: {model}")
    print(f"Svar: {response.content}")
    return response.content

# För testkörning
if __name__ == "__main__":
    test = "Hej, hur mår du idag?"
    process(test)






