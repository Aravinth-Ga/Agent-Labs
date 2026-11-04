import json, re
from agent.llm import chat, text_of
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError

# Prompt used to tell the model how to respond.
SYSTEM = Path("prompts/parser_system.md").read_text(encoding="utf-8")


# Structure of one parsed requirement.
class DidRequirement(BaseModel):
    req_id: str | None
    service: str | None = Field(default=None, pattern=r"^0x[0-9A-Fa-f]{2}$")
    did: str | None = Field(default=None, pattern=r"^0x[0-9A-Fa-f]{4}$")
    length_bytes: int | None = Field(default=None, ge=1, le=4095)
    sessions: list[str] | None = None
    security: str | None = None
    data_source: str | None = None
    confidence: float = Field(ge=0, le=1)
    missing: list[str]

# Remove Markdown code fences and convert the model output into Python JSON.
def _extract_json(s):
    s = re.sub(r"^```(?:json)?|```$", "", s.strip(), flags=re.M).strip()
    return json.loads(s)

# Send a requirement to the model and force it to return clean structured data.
def parse_requirement(text, retries=2):
    msgs = [{"role": "user", "content": f"REQUIREMENT:\n{text}"}]
    for attempt in range(retries + 1):
        raw = text_of(chat(msgs, system=SYSTEM, max_tokens=5200))
        try:
            return DidRequirement(**_extract_json(raw)).model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Parse retry {attempt + 1}/{retries + 1}: {e}")
            print(raw)
            msgs += [{"role": "assistant", "content": raw},
                     {"role": "user", "content": f"Invalid. Error: {e}. "
                                                 "Reply with corrected JSON only."}]
    raise RuntimeError("parse failed after retries")


def run_jsonl(path):
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            text = item["text"]
            expected = item.get("expected")
            parsed = parse_requirement(text)
            print(f"\n--- Requirement {idx} ---")
            print("parsed:", parsed)
            if expected:
                print("\nexpected:", expected)


if __name__ == "__main__":
    run_jsonl("golden/requirement.jsonl")