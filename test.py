from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.usage.prompt_tokens)
print(response.usage.completion_tokens)
print(response.usage.total_tokens)