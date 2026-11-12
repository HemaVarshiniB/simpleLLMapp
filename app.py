import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import time

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
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        full_response = ""
        first_token_time = None

        start_time = time.perf_counter()

        try:
            stream = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                # Instead of receiving one complete response, you receive an iterable stream of chunks.
                stream=True
            )

            for chunk in stream:
                # Each chunk contains newly generated content. A chunk is not necessarily one complete token.
                content = chunk.choices[0].delta.content
                
                if content:
                    if first_token_time is None:
                        first_token_time = time.perf_counter()

                    # full_response accumulates the generated content.
                    full_response += content
                    
                    # placeholder.markdown() updates the displayed response. ▌ acts as a visual typing cursor.
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

            end_time = time.perf_counter()

            # TTFT (Time to First Token) measures how long the user waits before receiving the first non-empty text chunk.
            ttft = first_token_time - start_time
            
            # This measures the complete request duration, including generation and streaming.
            total_time = end_time - start_time
            
            st.caption(f"TTFT: {ttft:.2f}s")
            st.caption(f"Total response time: {total_time:.2f}s")

            # Save completed response
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            placeholder.markdown(full_response + "\n\n⚠️ Response interrupted.")

            st.error(f"Streaming error: {e}")
