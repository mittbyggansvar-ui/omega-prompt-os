import json
import os
from datetime import datetime

SESSION_COUNTER = '.session_counter.txt'

def load_or_init_session():
    if os.path.exists(SESSION_COUNTER):
        with open(SESSION_COUNTER, 'r') as f:
            count = int(f.read().strip()) + 1
    else:
        count = 1
    with open(SESSION_COUNTER, 'w') as f:
        f.write(str(count))
    return count

def build_execution_packet(user_input):
    iterations = load_or_init_session()
    lower = user_input.lower().strip()
    is_empty = lower == '' or lower.startswith('===') or lower.startswith('du:')
    is_powershell = any(cmd in lower for cmd in ['cd ', 'write-host', 'out-file', 'remove-item'])
    
    if is_empty:
        intent = 'SUMMARIZE_SESSION'
    elif is_powershell:
        intent = 'SHELL_COMMAND'
    elif any(word in lower for word in ['kontrakt', 'risk', 'avtal', 'contract']):
        intent = 'CONTRACT_ANALYSIS'
    else:
        intent = 'GENERAL'
    
    return {
        'normalized_input': user_input,
        'intent': intent,
        'session_iteration_count': iterations,
        'benchmark_status': {'runs': iterations - 1 if iterations > 0 else 0, 'questions': 7},
        'version': 'v1.26',
        'policy_context': {
            'code_mode': is_powershell,
            'simulation_lock_applicable': False
        }
    }
