from dotenv import load_dotenv
load_dotenv()

from langchain_xai import ChatXAI
from langchain_openai import ChatOpenAI

print('✅ Ω Prompt OS environment is ready!')
print('Grok and OpenAI are configured and ready for Layer 1 testing.')

# Test med korrekt Grok-modell 2026
llm = ChatXAI(model="grok-3-beta", temperature=0.0)
response = llm.invoke("Säg 'Ω Prompt OS Boot successful' på svenska och lägg till 'Swarm är aktiverad'.")

print('\n✅ Testresultat:')
print(response.content)
