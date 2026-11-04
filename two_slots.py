from pathlib import Path
from agent.llm import chat, text_of

# 1. Provide the system instructions
SYSTEM = Path("prompts/analyst_system.md").read_text(encoding="utf-8")

# 2. Provide the context
CONTEXT = """REQ-DIAG-042: The ECU shall support UDS service 0x22 for DID 0xF190 (VIN).
Access: default session and extended session."""

QUESTIONS_FILE = Path("golden/b2_questions.txt")


def ask(question):
    user = f"CONTEXT:\n{CONTEXT}\n\n\nQUESTION: {question}"
    return text_of(chat([{"role": "user", "content": user}], system=SYSTEM, max_tokens=1024))


def load_questions(path):
    if not path.exists():
        raise FileNotFoundError(f"Question file not found: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


for i, question in enumerate(load_questions(QUESTIONS_FILE), start=1):
    print(f"\n--- Q{i}: {question} ---")
    print(ask(question))

