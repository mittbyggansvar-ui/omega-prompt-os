import os
from dotenv import load_dotenv
from langchain_xai import ChatXAI
from langchain_openai import ChatOpenAI

load_dotenv()

print("=" * 80)
print("Ω PROMPT OS - DIAGNOSTIK TEST")
print("Testar Grok och OpenAI separat")
print("=" * 80)

user_input = "Säg bara 'Grok test OK' om du fungerar."

print("\n--- TESTAR GROK ---")
try:
    llm_grok = ChatXAI(model="grok-3", xai_api_key=os.getenv("XAI_API_KEY"))
    response_grok = llm_grok.invoke(user_input)
    print("Grok svarade:", response_grok.content)
    print("Grok: SUCCESS")
except Exception as e:
    print("Grok FEL:", str(e))

print("\n--- TESTAR OPENAI ---")
try:
    llm_openai = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    response_openai = llm_openai.invoke(user_input)
    print("OpenAI svarade:", response_openai.content)
    print("OpenAI: SUCCESS")
except Exception as e:
    print("OpenAI FEL:", str(e))

print("\n--- SLUT PÅ DIAGNOSTIK ---")
print("Kopiera hela outputen och skicka till mig.")
