import sys
import os
import json
from dotenv import load_dotenv
from langchain_xai import ChatXAI

sys.path.insert(0, os.path.abspath('.'))
load_dotenv()

from src.preprocessor.preprocessor import build_execution_packet

print('=' * 90)
print('Ω Prompt OS v1.26 - ENTERPRISE PILOT')
print('ABSOLUT SIMULATION LOCK: AKTIV')
print('Version: v1.26 - State från packet används ALLTID')
print('=' * 90)

while True:
    user_input = input('\nDu: ').strip()
    if user_input.lower() in ['exit', 'quit', 'avsluta']:
        print('Avslutar Ω Prompt OS v1.26. Hej då!')
        break
    
    packet = build_execution_packet(user_input)
    with open('src/layers/layer1_constitution.txt', 'r', encoding='utf-8') as f:
        constitution = f.read()
    
    prompt = f'''{constitution}

Execution Packet (ANVÄND DETTA STATE ALLTID - aldrig gissa):
{json.dumps(packet, ensure_ascii=False, indent=2)}

Version: v1.26
Använd exakt packet['version'], packet['session_iteration_count'] och packet['benchmark_status'] i svaret.
Inga referenser till v1.20 eller tidigare versioner tillåts.

Användarfråga: {user_input}'''

    llm = ChatXAI(model='grok-3', temperature=0.0)
    response = llm.invoke(prompt).content

    print(f'\nΩ Prompt OS (v1.26):')
    print(f' → Model used: Grok-3')
    print(f' → Intent: {packet["intent"]}')
    print(f' → Svar: {response}')
    print(f'[Vault] Hash-chained entry sparad - Build iterations today: {packet["session_iteration_count"]}')
