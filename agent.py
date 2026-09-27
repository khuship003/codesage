import os
import json
from dotenv import load_dotenv
from groq import Groq
from tools import list_files, read_file

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- Describe our tools to the AI in the format it expects ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List every file in the target codebase repo.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
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
                    "filepath": {
                        "type": "string",
                        "description": "The full path of the file to read"
                    }
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

    # First call: let the model decide if it wants to use a tool
    first_response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = first_response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"[Agent is calling tool: {function_name}({function_args})]")

            function_to_call = available_functions[function_name]
            function_result = function_to_call(**function_args)

            messages.append({
            "role": "user",
            "content": "Now answer the original question in plain text using the information above. Do not call any more tools."
        })

        second_response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages
        )
        return second_response.choices[0].message.content


if __name__ == "__main__":
    while True:
        question = input("\nAsk the agent something (or type 'exit'): ")
        if question.lower() == "exit":
            break
        answer = run_agent(question)
        print("\nAnswer:\n", answer)