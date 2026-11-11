import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="Simple LLM App", page_icon="💬", layout="centered")
st.title("Simple LLM App")
st.caption("Type a message below. It is sent to Groq and the reply appears in the chat.")

# Get Groq API key from environment
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("Set GROQ_API_KEY in your .env file.")
    st.stop()

# Initialize OpenAI client pointing to Groq's endpoint
client = OpenAI(
    api_key=api_key, 
    base_url="https://api.groq.com/openai/v1"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask anything...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",  # Active Groq free-tier model ID
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})