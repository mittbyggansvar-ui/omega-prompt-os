from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

print('🚀 Ω Prompt OS v1.0 - OpenAI Fallback Mode')
print('Layer 1 Constitution loaded with ABSOLUT SIMULATION LOCK')

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

prompt = ChatPromptTemplate.from_template("Du är Ω Prompt OS. Bekräfta att du är redo att bygga det fulla 7-lagers systemet.")

chain = prompt | llm
response = chain.invoke({})

print('\n✅ Ω Prompt OS svarar:')
print(response.content)
print('\nSystemet är nu redo för att bygga Layer 2-7.')
