import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from db.utils import create_newChat, insert_messages

load_dotenv()

# Initialise openAI client endpoint using API key from .env file 
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url=os.getenv("GROQ_URL"))

if "session_id" not in st.session_state:
    st.session_state.session_id = None
    
if "msgs" not in st.session_state:
    st.session_state.msgs = []

with st.sidebar:
    st.header("Chat Sessions")
    
    if(st.button("New Chat")):
        st.session_state.session_id = create_newChat()
        st.session_state.msgs = []
    
for msg in st.session_state.msgs:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

user_input = st.chat_input("Ask anything:")
    
if user_input:
    if st.session_state.session_id is None:
        st.session_state.session_id = create_newChat()
    
    session_id = st.session_state.session_id
    
    user_msg = {"role":"user", "content":user_input}
    st.session_state.msgs.append(user_msg)
    
    insert_messages(st.session_state.session_id, "user", user_input)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
        
    try:
        # Sets the maximum number of tokens the model can generate in its response. It does not mean the model must generate exactly 1,000 tokens.
        # Temperature controls the randomness of the model's output. A higher temperature (e.g., 0.8) will make the output more random, while a lower temperature (e.g., 0.2) will make it more focused and deterministic.
        response = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.msgs], max_tokens=1000, temperature=0.7)
        if(response):
            # print(response)
            print(response.choices[0].message.content)
            ai_response = response.choices[0].message.content
            st.markdown(ai_response)
            st.session_state.msgs.append({"role":"assistant", "content":ai_response})
            insert_messages(st.session_state.session_id, "assistant", ai_response)
            st.write("Total Tokens:", response.usage.total_tokens)
            st.write("Prompt Tokens:", response.usage.prompt_tokens)
            st.write("Completion Tokens:", response.usage.completion_tokens)
    except Exception as e:
        print("Error:", e)