import os
from dotenv import load_dotenv
from agent.llm import chat, text_of

load_dotenv()

messages = [
    {
        "role": "user",
        "content": "What does UDS service 0x27 do?"
    }
]

resp = chat(
    messages=messages,
    system="You are AUTOSAR Diagnostic Expert. Answer in 3 sentences.",
    max_tokens=400,
)

print(text_of(resp))
print("stop:", resp.stop_reason)
print("Input tokens count:", resp.usage.input_tokens, "Output tokens count:", resp.usage.output_tokens)