import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from db.utils import create_newChat, insert_messages, get_messages, get_all_sessions
from gmail_toolService import (
    get_gmail_service,
    send_email,
    read_email,
    search_emails,
)
from tool_schema import my_tools
from toolFunctions import get_weather, get_news
import json


def search_gmail(query, max_results):
    return search_emails(get_gmail_service(), query, max_results)


def read_gmail(message_id):
    return read_email(get_gmail_service(), message_id)


def send_gmail(to, subject, body):
    return send_email(get_gmail_service(), to, subject, body)


available_functions = {
    "get_weather": get_weather,
    "get_news": get_news,
    "read_email": read_gmail,
    "send_email": send_gmail,
    "search_emails": search_gmail,
}


load_dotenv()

# Initialise openAI client endpoint using API key from .env file 
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url=os.getenv("GROQ_URL"))

# Intialize Session State Variables
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "msgs" not in st.session_state:
    st.session_state.msgs = []


with st.sidebar:
    st.header("Chat Sessions")
    if(st.button("New Chat")):
        session_id = create_newChat()
        st.session_state.session_id = session_id
        st.session_state.msgs = []
        
    sessions = get_all_sessions()
    st.markdown("### Previous Sessions")
    for session in sessions[::-1]:
        session_id = session[0]
        if(st.button(f"Session ID: {session_id}")):
            st.session_state.session_id = session_id
            st.session_state.msgs = get_messages(session_id)
            
            
for msg in st.session_state.msgs:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        # TODO: What if model is not able to answer the question? How do we display the tool's output in the chat?

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
        # Sets the maximum number of tokens the model can generate in its response. It does not mean the model must generate exactly 1,000 tokens. max_tokens=1000 controls the maximum generated output, not the size of your input conversation.
        # Temperature controls the randomness of the model's output. A higher temperature (e.g., 0.8) will make the output more random, while a lower temperature (e.g., 0.2) will make it more focused and deterministic.
        response = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.msgs], tools=my_tools, tool_choice="auto", max_tokens=1000, temperature=0.7)
        
        iteration = 0
        max_iterations = 5  # Set a limit to prevent infinite loops
        
        # Once the LLM generates a normal response instead of requesting another tool, this condition becomes false:
        while response.choices[0].message.tool_calls:

            iteration += 1

            if iteration > max_iterations:
                raise RuntimeError("Maximum tool-call iterations exceeded")

            assistant_message = response.choices[0].message

            # Append assistant's tool-call request to conversation
            st.session_state.msgs.append(
                assistant_message.model_dump(exclude_none=True)
            )

            # 4. Execute requested functions
            for tool_call in assistant_message.tool_calls:

                function_name = tool_call.function.name

                # Extract function arguments
                arguments = json.loads(
                    tool_call.function.arguments
                )

                # Find the actual Python function
                function_to_call = available_functions.get(function_name)

                if function_to_call is None:
                    result = {"error": f"Unknown function: {function_name}"}
                else:
                    try:
                        result = function_to_call(**arguments)
                    except Exception as tool_error:
                        if function_name in {
                            "read_email",
                            "send_email",
                            "search_emails",
                        }:
                            st.error(f"{function_name} failed: {tool_error}")
                        result = {"error": str(tool_error)}

                # 5. Append function execution result
                st.session_state.msgs.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str)
                })

            # 6. Send tool results back to LLM
            response = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=st.session_state.msgs,
                tools=my_tools,
                tool_choice="auto",
                max_tokens=1000,
                temperature=0.7
            )
        
        if(response):
            # print(response)
            # print(response.choices[0].message.content)
            ai_response = response.choices[0].message.content
            st.markdown(ai_response)
            st.session_state.msgs.append({"role":"assistant", "content":ai_response})
            insert_messages(st.session_state.session_id, "assistant", ai_response)
            st.write("Total Tokens:", response.usage.total_tokens)
            st.write("Prompt Tokens:", response.usage.prompt_tokens)
            st.write("Completion Tokens:", response.usage.completion_tokens)
            
    except Exception as e:
        print("Error:", e)