import os
from dotenv import load_dotenv

load_dotenv()

# Tvingad nyckel om miljövariabeln inte läses
os.environ['OPENAI_API_KEY'] = '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'

from langchain_openai import ChatOpenAI

print('🚀 Ω Prompt OS v1.0 - OpenAI Fallback Mode')
print('ABSOLUT SIMULATION LOCK är aktiv')

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0)

response = llm.invoke('Du är Ω Prompt OS. Bekräfta att du är redo att bygga det fulla 7-lagers systemet. Svara kort på svenska och nämn att Swarm är redo.')

print('\n✅ Svar från Ω Prompt OS:')
print(response.content)
print('\nSystemet är nu redo för Layer 2-7.')
