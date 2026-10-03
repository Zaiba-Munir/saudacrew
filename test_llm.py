import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": "Roman Urdu mein ek line mein salam karo aur batao tum kaun ho."}
    ],
)
print(response.choices[0].message.content)