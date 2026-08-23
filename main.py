from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-5.5",
    instructions="You are a helpful job application assistant.",
    input="Explain what an AI research engineer does in one sentence."
)

print(response.output_text)
