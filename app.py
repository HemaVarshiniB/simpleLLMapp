import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

# Initialise openAI client endpoint using API key from .env file 
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url=os.getenv("GROQ_URL"))

models = client.models.list()
for model in models.data:
    print(model.id)
    
while(True):
    user_input = input("Ask anything:")
    try:
        response = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=[{"role":"user", "content":user_input}])
        if(response):
            # print(response)
            print(response.choices[0].message.content)
            print("Total Tokens:", response.usage.total_tokens)
            print("Prompt Tokens:", response.usage.prompt_tokens)
            print("Completion Tokens:", response.usage.completion_tokens)
    except Exception as e:
        print("Error:", e)


