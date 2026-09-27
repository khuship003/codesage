import streamlit as st
import os
import json
from dotenv import load_dotenv
from groq import Groq
from tools import list_files, read_file

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL_NAME = "qwen/qwen3.8-27b"

# --- Tool definitions (same as agent.py) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List every file in the target codebase repo.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a specific file, given its full path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "The full path of the file to read"}
                },
                "required": ["filepath"]
            }
        }
    }
]

available_functions = {
    "list_files": list_files,
    "read_file": read_file,
}


def run_agent(question):
    messages = [{"role": "user", "content": question}]

    first_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = first_response.choices[0].message
    tool_calls = response_message.tool_calls
    tools_used = []

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            tools_used.append(f"{function_name}({function_args})")

            function_to_call = available_functions[function_name]
            function_result = function_to_call(**function_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": str(function_result)[:3000]
            })

        second_response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=messages,
    tools=tools,
    tool_choice="none"
)
        final_answer = second_response.choices[0].message.content
    else:
        final_answer = response_message.content

    return final_answer, tools_used


# --- Streamlit UI ---
st.set_page_config(page_title="CodeSage", page_icon="🧙")
st.title("🧙 CodeSage")
st.caption("Chat with your codebase — now with agentic tools")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask a question about the codebase..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, tools_used = run_agent(question)
            st.markdown(answer)
            if tools_used:
                st.caption(f"🔧 Tools used: {', '.join(tools_used)}")

    st.session_state.messages.append({"role": "assistant", "content": answer})