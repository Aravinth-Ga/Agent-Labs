
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

_client = Anthropic()
MODEL = os.getenv("MODEL", "claude-sonnet-5-5")

def chat(messages, system="", tools=None, max_tokens=1024):
    """messges in, Message object out. The only place the provider is named."""
    kwargs = dict(model=MODEL, max_tokens=max_tokens, system=system, messages=messages)

    if tools:
        kwargs["tools"] = tools
    
    resp = _client.messages.create(**kwargs)

    print(f"[llm] stop={resp.stop_reason} in={resp.usage.input_tokens}" 
          f" out={resp.usage.output_tokens}")

    return resp

def text_of(resp):
    return "".join(byte.text for byte in resp.content if byte.type == "text")
