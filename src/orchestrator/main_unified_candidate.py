# Ω Prompt OS v1.27 - Unified Runtime Candidate
# Thin orchestrator for unified runtime

import os
from dotenv import load_dotenv

from .runtime_modes import resolve_intent, build_prompt
from .runtime_llm import (
    resolve_provider,
    route_model,
    call_llm,
    display_model_name,
    validate_output,
)

BOOT_BANNER = "Ω Prompt OS UNIFIED CANDIDATE loaded - Thin runtime"
BOOTSTRAPPED = False


def bootstrap_candidate_runtime():
    load_dotenv()
    print(BOOT_BANNER)


def ensure_bootstrapped():
    global BOOTSTRAPPED
    if not BOOTSTRAPPED:
        bootstrap_candidate_runtime()
        BOOTSTRAPPED = True


def run_with_meta(user_input, mode="default"):
    ensure_bootstrapped()

    intent = resolve_intent(user_input, mode)
    prompt = build_prompt(intent)

    provider = resolve_provider()
    model = route_model(intent)

    raw_output = call_llm(model, prompt)
    output = validate_output(raw_output)

    return provider, model, output


def run(user_input, mode="default"):
    _, _, output = run_with_meta(user_input, mode)
    return output


def process(user_input: str):
    return run(user_input, mode="default")


if __name__ == "__main__":
    test = "Hej, hur mår du idag?"
    provider, model, result = run_with_meta(test, mode="default")

    print(f"Runtime provider: {provider}")
    print(f"Model used: {display_model_name(model)}")
    print(f"Svar: {result}")
