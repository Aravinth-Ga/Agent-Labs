from pathlib import Path
from agent.llm import chat, text_of

# 1. Provide the system instructions
SYSTEM = Path("prompts/analyst_system.md").read_text(encoding="utf-8")

# 2. Provide the context
CONTEXT="""REQ-DIAG-042: The ECU shall support UDS service 0x22 for DID 0xF190 (VIN).
Access: default session and extended session. """

def ask(question):
    user = f"CONTEXT:\n{CONTEXT} \n \n \n QUESTION: {question}"
    return text_of(chat([{"role": "user", "content": user}], system=SYSTEM, max_tokens=1024))

print(ask("Which session allow DID 0xF190?"))
print(ask("what is the security level for DID 0xF190?"))
