import sys
import os
import json
from dotenv import load_dotenv
from langchain_xai import ChatXAI
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.abspath('.'))
load_dotenv()

from src.preprocessor.preprocessor import build_execution_packet

print('=' * 90)
print('Ω Prompt OS v1.27 - DUAL LLM ENTERPRISE COMPLEMENT')
print('ABSOLUT SIMULATION LOCK: AKTIV')
print('Grok primary → OpenAI fallback → Local fallback')
print('Version: v1.27')
print('=' * 90)

while True:
    user_input = input('\nDu: ').strip()
    if user_input.lower() in ['exit', 'quit', 'avsluta']:
        print('Avslutar Ω Prompt OS v1.27. Hej då!')
        break

    packet = build_execution_packet(user_input)
    with open('src/layers/layer1_constitution.txt', 'r', encoding='utf-8') as f:
        constitution = f.read()

    prompt = f'''{constitution}

Execution Packet (ANVÄND DETTA STATE ALLTID):
{json.dumps(packet, ensure_ascii=False, indent=2)}

Användarfråga: {user_input}'''

    response = None
    model_used = 'UNKNOWN'

    # Försök Grok först
    try:
        llm = ChatXAI(model='grok-3', temperature=0.0)
        response = llm.invoke(prompt).content
        model_used = 'Grok-3'
    except Exception as e:
        print(f'Grok misslyckades: {str(e)[:80]}...')

    # Fallback till OpenAI
    if response is None:
        try:
            llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0)
            response = llm.invoke(prompt).content
            model_used = 'OpenAI gpt-4o-mini'
        except Exception as e:
            print(f'OpenAI misslyckades: {str(e)[:80]}...')

    # Sista lokala fallback
    if response is None:
        response = 'Båda LLM:er är nere (rate limit eller blockering). Lokalt fallback-svar: Systemet är aktivt men behöver fungerande API-krediter för full kapacitet.'
        model_used = 'LOCAL FALLBACK'

    print(f'\nΩ Prompt OS (v1.27):')
    print(f' → Model used: {model_used}')
    print(f' → Intent: {packet["intent"]}')
    print(f' → Svar: {response}')
    print(f'[Vault] Hash-chained entry sparad - Build iterations today: {packet["session_iteration_count"]}')
