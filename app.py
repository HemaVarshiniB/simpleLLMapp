import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialise openAI client endpoint using API key from .env file 
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url=os.getenv("GROQ_URL"))

# models = client.models.list()
# for model in models.data:
#     print(model.id)
msgs = []

    
while(True):
    user_input = input("Ask anything:")
    if(user_input.lower() == "/exit"):
        break
    elif(user_input.lower() == "/clear"):
        msgs = []
        continue
    msgs.append({"role":"user", "content":user_input})
    try:
        # Sets the maximum number of tokens the model can generate in its response. It does not mean the model must generate exactly 1,000 tokens.
        # Temperature controls the randomness of the model's output. A higher temperature (e.g., 0.8) will make the output more random, while a lower temperature (e.g., 0.2) will make it more focused and deterministic.
        response = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=[{"role": m["role"], "content": m["content"]} for m in msgs], max_tokens=1000, temperature=0.7)
        if(response):
            # print(response)
            print(response.choices[0].message.content)
            msgs.append({"role":"assistant", "content":response.choices[0].message.content})
            print("Total Tokens:", response.usage.total_tokens)
            print("Prompt Tokens:", response.usage.prompt_tokens)
            print("Completion Tokens:", response.usage.completion_tokens)
    except Exception as e:
        print("Error:", e)


